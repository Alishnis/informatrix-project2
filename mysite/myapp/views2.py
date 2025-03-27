from django.shortcuts import render, redirect
import os
import torch
import torch.nn as nn
from torchvision import transforms
from torchvision.models import efficientnet_b4
from PIL import Image
import numpy as np
from django.conf import settings
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from skimage.transform import resize
from .models import AnalysisSkin, BloodAnalysis
from django.http import JsonResponse
from django.utils import timezone
import pdfplumber
import pytesseract
import re
import logging

# Предобработка изображений
preprocess = transforms.Compose([
    transforms.Resize((380, 380)),  # Для EfficientNet-B4
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Загрузка улучшенной модели EfficientNet-B4
def load_skin_disease_model():
    model = efficientnet_b4(pretrained=True)  # Загружаем предобученные веса
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, 7)  # Настраиваем на 7 классов заболеваний
    model = nn.Sequential(
        model,
        nn.Dropout(0.5)  # Добавляем регуляризацию
    )
    model.eval()
    return model

from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

def generate_gradcam(model, input_tensor, target_layer, predicted_index):
    """
    Генерация Grad-CAM визуализации для анализа значимых областей.
    """
    # Создаём целевой класс для Grad-CAM
    targets = [ClassifierOutputTarget(predicted_index)]
    
    # Создаём Grad-CAM объект
    cam = GradCAM(model=model, target_layers=[target_layer])
    
    # Генерация карты активации
    grayscale_cam = cam(input_tensor=input_tensor, targets=targets)
    grayscale_cam = grayscale_cam[0, :]  # Убираем лишнее измерение
    
    return grayscale_cam

# Анализ изображений
def analyze_skin_image(request):
    """Обработка снимков кожи, предсказание заболеваний и визуализация Grad-CAM."""
    if request.method == 'POST' and 'file' in request.FILES:
        uploaded_file = request.FILES['file']

        # Сохраняем временное изображение
        temp_image_path = os.path.join(settings.MEDIA_ROOT, 'temp', uploaded_file.name)
        os.makedirs(os.path.dirname(temp_image_path), exist_ok=True)
        with open(temp_image_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        try:
            # Предобработка изображения
            image = Image.open(temp_image_path).convert('RGB')
            input_tensor = preprocess(image).unsqueeze(0)

            # Загрузка модели
            model = load_skin_disease_model()

            # Прогнозирование
            with torch.no_grad():
                outputs = model(input_tensor)
                probabilities = torch.nn.functional.softmax(outputs[0], dim=0)

            # Определяем наибольшую вероятность
            predicted_index = probabilities.argmax().item()
            predicted_class = CLASSES[predicted_index]
            predicted_probability = probabilities[predicted_index].item() * 140

            # Генерация Grad-CAM
            target_layer = model[0].features[-1]  # Последний сверточный слой EfficientNet-B4
            heatmap = generate_gradcam(model[0], input_tensor, target_layer, predicted_index)

            # Наложение Grad-CAM на изображение
            heatmap_resized = np.array(Image.fromarray(heatmap).resize(image.size, Image.LANCZOS))
            heatmap_normalized = (heatmap_resized - heatmap_resized.min()) / (heatmap_resized.max() - heatmap_resized.min())
            heatmap_colored = np.uint8(255 * heatmap_normalized)
            heatmap_overlay = (np.array(image) * 0.5 + np.expand_dims(heatmap_colored, axis=2) * 0.5).astype(np.uint8)

            # Сохранение Grad-CAM изображения
            gradcam_dir = os.path.join(settings.MEDIA_ROOT, 'gradcam')
            os.makedirs(gradcam_dir, exist_ok=True)
            gradcam_path = os.path.join(gradcam_dir, f"gradcam_{os.path.basename(uploaded_file.name)}")
            Image.fromarray(heatmap_overlay).save(gradcam_path)
            analysis = AnalysisSkin.objects.create(
                user=request.user,
                analysis_file=gradcam_path.replace(settings.MEDIA_ROOT, ''),  # Сохраняем относительный путь
                result=f'{predicted_class}: {predicted_probability:.2f}%'
            )

            # Удаляем временный файл
            os.remove(temp_image_path)

            # Подготовка результатов
            return render(request, 'result_forskin.html', {
                'predicted_class': predicted_class,
                'predicted_probability': f"{predicted_probability:.2f}%",
                'analysis_id': analysis.id,
                'gradcam_url': gradcam_path.replace(settings.MEDIA_ROOT, settings.MEDIA_URL),
            })

        except Exception as e:
            return render(request, 'skin.html', {'error': f"Ошибка анализа: {str(e)}"})

    return render(request, 'skin.html')

CLASSES = [
    "Melanoma", "Nevus", "Basal Cell Carcinoma",
    "Actinic Keratosis", "Benign Keratosis",
    "Dermatofibroma", "Vascular Lesion"
]

from django.contrib import messages

def save_results_skin(request):
    """Подтверждение сохранения анализа."""
    if request.method == 'POST':
        analysis_id = request.POST.get('analysis_id')
        try:
            # Получаем анализ по ID
            analysis = AnalysisSkin.objects.get(id=analysis_id, user=request.user)
            analysis.is_saved = True  # Предположительно, добавлено поле is_saved
            analysis.save()
            messages.success(request, 'Результаты успешно сохранены!')
        except AnalysisSkin.DoesNotExist:
            messages.error(request, 'Анализ не найден.')

        return redirect('user_kab')  # Перенаправление на кабинет пользователя
    return JsonResponse({'error': 'Недопустимый метод запроса'}, status=405)

# Список классов кожных заболеваний

from django.core import serializers
def save_results(request):
    if request.method=="POST":
        analyses=BloodAnalysis.objects.filter(user=request.user).order_by('-id')
        analyses_data = list(analyses.values('uploaded_at', 'leukocytes_level', 'hemoglobin_level', 'erythrocytes_level', 'thrombocytes_level', 'hematocrit_level'))
        context={'analyses':analyses_data}
        return render (request, 'blood_analysis_result.html',context)

def get_analysis_details(request, analysis_id):
    try:
        analysis = BloodAnalysis.objects.get(id=analysis_id)
        data = {
            'leukocytes_level': analysis.leukocytes_level,
            'hemoglobin_level': analysis.hemoglobin_level,
            'erythrocytes_level': analysis.erythrocytes_level,
            'thrombocytes_level': analysis.thrombocytes_level,
            'hematocrit_level': analysis.hematocrit_level,
        }
        return JsonResponse(data)
    except BloodAnalysis.DoesNotExist:
        return JsonResponse({'error': 'Analysis not found'}, status=404)

import matplotlib.pyplot as plt
import io
import urllib
from django.shortcuts import render
from django.http import HttpResponse
from .models import BloodAnalysis

import plotly.express as px
import plotly.graph_objects as go  # Import graph_objects as go
from django.shortcuts import render
from .models import BloodAnalysis
import plotly.io as pio
import io
import base64
import plotly.graph_objects as go

def show_graph(request, parameter):
    analyses = BloodAnalysis.objects.filter(user=request.user).order_by('-id')  # Сортируем по дате, от первого к последнему

    analysis_count = len(analyses)
    dates = [f"Analysis {i+1}" for i in range(analysis_count)]

    # Собираем данные для графика
    leukocytes_levels = [analysis.leukocytes_level for analysis in analyses]
    hemoglobin_levels = [analysis.hemoglobin_level for analysis in analyses]
    erythrocytes_levels = [analysis.erythrocytes_level for analysis in analyses]
    thrombocytes_levels = [analysis.thrombocytes_level for analysis in analyses]
    hematocrit_levels = [analysis.hematocrit_level for analysis in analyses]

    # Определение уровня для текущего показателя
    if parameter == 'leukocytes':
        levels = leukocytes_levels
        title = 'Leukocytes Levels Over Analyses'
    elif parameter == 'erythrocytes':
        levels = erythrocytes_levels
        title = 'Erythrocytes Levels Over Analyses'
    elif parameter == 'thrombocytes':
        levels = thrombocytes_levels
        title = 'Thrombocytes Levels Over Analyses'
    elif parameter == 'hematocrit':
        levels = hematocrit_levels
        title = 'Hematocrit Levels Over Analyses'
    else:
        levels = hemoglobin_levels
        title = 'Hemoglobin Levels Over Analyses'

    # Разворачиваем данные, чтобы график начинался с первого анализа

    levels.reverse()

    # Создаем график с использованием Plotly
    fig = px.line(
        x=dates,
        y=levels,
        labels={'value': f'{parameter.capitalize()} Level', 'variable': 'Analysis'},
        title=title
    )

    # Рекомендации для последнего анализа
    last_analysis = analyses[0] if analyses.exists() else None  # Получаем последний анализ
    recommendations = []

    if last_analysis:
        # Получаем значение последнего показателя для выбранного параметра
        level = getattr(last_analysis, f'{parameter}_level')
        rec = get_recommendations(parameter, level)
        if rec:
            recommendations.append(rec)

    # Сохраняем график в байтовый поток
    img_bytes = pio.to_image(fig, format='png')

    # Преобразуем в base64 для отображения в шаблоне
    graph_image = base64.b64encode(img_bytes).decode('utf-8')

    # Передаем график и рекомендации в шаблон
    return render(request, 'blood_analysis_result.html', {
        'graph_image': graph_image,
        'analyses': analyses,
        'selected_parameter': parameter,
        'recommendations': recommendations,  # Передаем рекомендации только для последнего анализа
    })
    
    
def get_recommendations(parameter, level):
    """
    Функция для проверки уровня показателя и предоставления рекомендаций по лечению.
    """
    recommendations = {
        'leukocytes': {
            'normal': (4.0, 11.0),  # Нормальный диапазон лейкоцитов
            'low': {
                'message': "Your leukocyte count is low, which may indicate a weakened immune system or an infection. Consider consulting a doctor.",
                'solution': "To treat low leukocyte count, you may need medication to stimulate the production of white blood cells. Additionally, incorporating a balanced diet rich in vitamins C, E, and A, as well as zinc, can help boost your immune system. It's crucial to avoid infections while your immune system is weak."
            },
            'high': {
                'message': "Your leukocyte count is high, which could suggest infection, inflammation, or other conditions. Please consult your doctor.",
                'solution': "To address high leukocyte levels, treatment usually involves treating the underlying cause, such as an infection or inflammation. Anti-inflammatory medications or antibiotics may be prescribed depending on the cause. In rare cases, more specialized treatments for blood disorders may be required."
            },
        },
        'erythrocytes': {
            'normal': (4.5, 5.9),  # Нормальный диапазон эритроцитов
            'low': {
                'message': "Your erythrocyte count is low, which could indicate anemia. You may need to increase iron-rich foods in your diet or take iron supplements.",
                'solution': "To treat low erythrocyte levels, increasing iron intake is essential. This can be done by consuming more red meat, leafy greens, legumes, and fortified cereals. Iron supplements may also be recommended. If the anemia is severe, you may need vitamin B12 or folate supplementation."
            },
            'high': {
                'message': "Your erythrocyte count is high, which could indicate dehydration or other conditions. Please consult a healthcare professional.",
                'solution': "To address high erythrocyte levels, it is important to ensure proper hydration. If dehydration is the cause, drinking enough water should help. For other causes like polycythemia, a doctor may recommend phlebotomy or medications that reduce red blood cell production."
            },
        },
        'thrombocytes': {
            'normal': (150, 450),  # Нормальный диапазон тромбоцитов
            'low': {
                'message': "Your platelet count is low, which can increase your risk of bleeding. Consider consulting a healthcare provider for further investigation.",
                'solution': "Low platelet count, known as thrombocytopenia, can be treated with medications that stimulate platelet production. In cases of significant bleeding, a platelet transfusion might be necessary. It's also important to avoid medications or substances that can thin the blood, like aspirin, unless directed by a doctor."
            },
            'high': {
                'message': "Your platelet count is high, which could suggest inflammation, infection, or other conditions. Please seek medical advice.",
                'solution': "To manage high platelet levels, addressing the underlying cause is critical. If the cause is an infection, antibiotics or antivirals may be necessary. For conditions like essential thrombocythemia, medication to reduce platelet production or blood thinners might be prescribed."
            },
        },
        'hematocrit': {
            'normal': (40, 45),  # Нормальный диапазон для гематокрита (проценты)
            'low': {
                'message': "Your hematocrit level is low, which can indicate anemia or excessive blood loss. Consider increasing iron and folate-rich foods in your diet.",
                'solution': "Treatment for low hematocrit usually involves addressing the cause of anemia. Iron supplements, folic acid, and B12 injections may be needed to restore normal levels. In cases of chronic blood loss, further investigation is required to identify the source of bleeding."
            },
            'high': {
                'message': "Your hematocrit level is high, which may suggest dehydration or conditions like polycythemia. Please consult your doctor.",
                'solution': "To reduce high hematocrit levels, rehydrating with fluids is crucial. If the cause is polycythemia, treatment options may include medications to reduce red blood cell production or phlebotomy (blood removal). Monitoring for underlying conditions is essential."
            },
        },
        'hemoglobin': {
            'normal': (12.0, 17.5),  # Нормальный диапазон для гемоглобина (г/дл)
            'low': {
                'message': "Your hemoglobin level is low, which may indicate anemia. You may need to increase iron-rich foods in your diet or take iron supplements.",
                'solution': "To address low hemoglobin levels, it's essential to boost iron intake and consider iron supplements. Vitamin C-rich foods can enhance iron absorption. If the anemia is caused by vitamin B12 or folate deficiency, supplements may be prescribed."
            },
            'high': {
                'message': "Your hemoglobin level is high, which could indicate dehydration, lung disease, or other conditions. Please consult a healthcare provider.",
                'solution': "To manage high hemoglobin, proper hydration is key. If the high level is due to dehydration, drinking more water should help. If it's caused by lung disease or another condition, further medical intervention may be necessary to treat the underlying issue."
            },
        },
    }

    normal_range = recommendations[parameter]['normal']
    try:

        if level < normal_range[0]:
            rec = recommendations[parameter]['low']
            return rec['message'], rec['solution']
        elif level > normal_range[1]:
            rec = recommendations[parameter]['high']
            return rec['message'], rec['solution']
        else:
            return None, None
    except:
        return ['In the last analysis this indicator was not present','']