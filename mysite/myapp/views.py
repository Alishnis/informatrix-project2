from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.shortcuts import render, redirect


from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Analysis
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

def analysis_page(request):
    if request.user.is_authenticated:  # Проверяем, авторизован ли пользователь
        return render(request, 'main.html')  # Шаблон для авторизованных
    else:
        return render(request, 'main2.html')  # Шаблон для всех


# def user_kab(request):
    
#     if request.user.is_authenticated:
        
#         analyses = Analysis.objects.filter(user=request.user).order_by('-id') # Получаем анализы пользователя
        
#         return render(request, 'user_kab.html', {
#             'user': request.user,
#             'analyses': analyses
#         })
#     return render(request,'error.html')



# def register_view(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')
        
#         # Проверка существования пользователя
#         if User.objects.filter(username=email).exists():
#             messages.error(request, 'Пользователь с таким email уже зарегистрирован.')
#         else:
#             # Создаем нового пользователя
#             user = User.objects.create_user(username=email, password=password)
#             user.save()
#             login(request, user)
#             return redirect('analysis_page')
    
#     return render(request, 'register.html')
# def login_view(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')
        
#         # Аутентификация пользователя
#         user = authenticate(request, username=email, password=password)
#         if user is not None:
#             login(request, user)
#             return redirect('analysis_page')  # Перенаправление на main.html
#         else:
#             messages.error(request, 'Неверный email или пароль.')

    # return render(request, 'register.html')
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required(login_url='/login/')  # Перенаправление на страницу входа
def main_view(request):
    return render(request, 'main.html')
 
 


from django.http import JsonResponse
from .models import Analysis

def handle_upload(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            analysis = Analysis.objects.create(
                user=request.user,  
                
                analysis_file=uploaded_file,
                result='Good',
            )
            return JsonResponse({'message': 'Файл успешно загружен!'}, status=200)
        return JsonResponse({'error': 'Файл не был загружен.'}, status=400)
    return JsonResponse({'error': 'Недопустимый метод запроса.'}, status=405)






from django.shortcuts import render
from django.http import JsonResponse
 




import subprocess



def analyze_symptoms(request):
    if request.method == 'POST':
        symptoms = request.POST.get('symptoms', '')
        if symptoms:
            try:
                
                import os

                script_path = os.path.join(os.path.dirname(__file__), "ex.py")
                result = subprocess.check_output(
                    ['python', script_path], 
                    input=symptoms, 
                    text=True
                )
                resultind=result.find('provide possible diagnoses:')
                result1=result[resultind:].replace('provide possible diagnoses:','')
                resultfin=result1.split(',')
                
                
               
                return render(request, 'symptom_form.html', {'diagnosis': resultfin})
            except Exception as e:
                return render(request, 'symptom_form.html', {'diagnosis': f"Ошибка: {e}"})
    return render(request, 'symptom_form.html')   

from django.shortcuts import render
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline
from myapp.models import Disease
import logging

logger = logging.getLogger(__name__)

def treatment_view(request):
    """
    Обработка запроса для получения рекомендаций по лечению.
    """
    recommendations = None
    if request.method == 'POST':
        illness = request.POST.get('illness', '').strip()
        if illness:
            try:
                try:
                    treatment = Disease.objects.get(name__iexact=illness)
                except Disease.DoesNotExist:
                    return render(request, 'treatment.html', {
                        'recommendations': "No treatment information available. Consult your doctor."
                    })
                except Disease.MultipleObjectsReturned:
                    return render(request, 'treatment.html', {
                        'recommendations': "Multiple records found for disease. Contact administrator."
                    })

                recommendations = treatment.treatment
                if not recommendations:
                    return render(request, 'treatment.html', {
                        'recommendations': "No treatment information available. Consult your doctor."
                    })

                

                

            except Exception as e:
                logger.error(f"Error processing request: {str(e)}")
                recommendations = f"An error occurred while processing data: {str(e)}"

    return render(request, 'treatment.html', {'recommendations': recommendations})




from django.shortcuts import render
from django.conf import settings
from PIL import Image
import os
import torch
from torchvision import transforms
from torchvision.models import densenet121
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from skimage.transform import resize
import numpy as np

preprocess = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def load_chexnet():
    """Загружаем предобученную модель DenseNet121."""
    model = densenet121(pretrained=True)
    model.classifier = torch.nn.Linear(model.classifier.in_features, 14)
    model.eval()
    return model

model = load_chexnet()


import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing import image
from skimage.transform import resize
from matplotlib import pyplot as plt

def generate_gradcam_keras(model, input_tensor, last_conv_layer_name, image_path):
    """Генерация Grad-CAM визуализации для Keras модели."""
    grad_model = Model(
        inputs=[model.inputs],
        outputs=[model.get_layer(last_conv_layer_name).output, model.output]
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(input_tensor)
        predicted_class = tf.argmax(predictions[0])  
        loss = predictions[:, predicted_class]

    grads = tape.gradient(loss, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_outputs = conv_outputs[0]
    heatmap = tf.reduce_sum(pooled_grads * conv_outputs, axis=-1)
    heatmap = np.maximum(heatmap, 0) / np.max(heatmap)  

    img = Image.open(image_path).convert("RGB")
    heatmap_resized = resize(heatmap, (img.size[1], img.size[0]))
    overlay = show_cam_on_image(np.array(img) / 255.0, heatmap_resized)

    gradcam_dir = os.path.join(settings.MEDIA_ROOT, 'gradcam')
    os.makedirs(gradcam_dir, exist_ok=True)
    gradcam_path = os.path.join(gradcam_dir, f"gradcam_{os.path.basename(image_path)}.png")
    Image.fromarray((overlay * 255).astype(np.uint8)).save(gradcam_path)

    return gradcam_path


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Analysis

from django.shortcuts import render
from django.contrib import messages
from .models import Analysis
import os
from django.conf import settings
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from skimage.transform import resize
from pytorch_grad_cam.utils.image import show_cam_on_image

def analyze_image(request):
    """Обработка загрузки изображения, генерация Grad-CAM и сохранение результата."""
    if request.method == 'POST' and 'file' in request.FILES:
        uploaded_file = request.FILES['file']

       
        temp_image_path = os.path.join(settings.MEDIA_ROOT, 'temp', uploaded_file.name)
        os.makedirs(os.path.dirname(temp_image_path), exist_ok=True)
        with open(temp_image_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        try:
        
            img = Image.open(temp_image_path).convert("RGB").resize((128, 128))
            img_array = np.array(img) / 255.0
            input_tensor = np.expand_dims(img_array, axis=0)  # (1, 128, 128, 3)

            
            predictions = model.predict(input_tensor)
            probabilities = predictions[0] 

           
            classes = [
                "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration", "Mass",
                "Nodule", "Pneumonia", "Pneumothorax", "Consolidation", "Edema",
                "Emphysema", "Fibrosis", "Pleural Thickening", "Hernia"
            ]

         
            detected_diseases = [
                f"{classes[i]}: {prob * 100:.2f}%"
                for i, prob in enumerate(probabilities) if prob > 0.6  
            ]
            result_text = "\n".join(detected_diseases)

            gradcam_path = generate_gradcam_keras(
                model=model,
                input_tensor=input_tensor,
                last_conv_layer_name="block5_conv3", 
                image_path=temp_image_path
            )

            gradcam_file_path = os.path.join(settings.MEDIA_ROOT, 'uploads/analysis/', os.path.basename(gradcam_path))
            os.makedirs(os.path.dirname(gradcam_file_path), exist_ok=True)
            os.rename(gradcam_path, gradcam_file_path) 

        
            analysis = Analysis.objects.create(
                user=request.user,
                analysis_file=gradcam_file_path.replace(settings.MEDIA_ROOT, ''),  
                result=result_text
            )           

           
            os.remove(temp_image_path)

            return render(request, 'result.html', {
                'diseases': detected_diseases,
                'gradcam_path': gradcam_file_path.replace(settings.MEDIA_ROOT, settings.MEDIA_URL),
                'analysis_id': analysis.id
            })

        except Exception as e:
            return render(request, 'upload.html', {'error': f"Ошибка анализа: {str(e)}"})

    return render(request, 'upload.html')
from .models import AnalysisCT
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ImageUploadSerializer
class ImageAnalysisView(APIView):
    def post(self, request):
        serializer = ImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_file = request.FILES['file']
            temp_image_path = os.path.join('temp', uploaded_file.name)

            # Сохраняем файл
            with open(temp_image_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            # Загружаем изображение
            img = Image.open(temp_image_path).convert("RGB")
            img = preprocess(img)
            img = img.unsqueeze(0)  # Добавляем batch размер

            # Прогоняем изображение через модель
            with torch.no_grad():
                outputs = model(img)
                probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
                _, predicted_idx = torch.max(probabilities, dim=0)

            # Список классов
            classes = [
                "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration", "Mass",
                "Nodule", "Pneumonia", "Pneumothorax", "Consolidation", "Edema",
                "Emphysema", "Fibrosis", "Pleural Thickening", "Hernia"
            ]

            # Результат
            result = classes[predicted_idx]
            analysis = Analysis.objects.create(
                user=request.user,
                analysis_file=uploaded_file.name,
                result=result,
            )

            os.remove(temp_image_path)  # Удаляем временный файл

            return Response({
                'result': result,
                'analysis_id': analysis.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def save_results(request):
    """Подтверждение сохранения анализа."""
    if request.method == 'POST':
        analysis_id = request.POST.get('analysis_id')
        try:
            analysis = Analysis.objects.get(id=analysis_id, user=request.user)
            analysis.is_saved = True 
            analysis.save()
            messages.success(request, 'Results saved successfully!')
        except Analysis.DoesNotExist:
            messages.error(request, 'Analysis not found.')

        return redirect('user_kab') 
    return JsonResponse({'error': 'Invalid request method'}, status=405)
def save_results_ct(request):
    """Подтверждение сохранения анализа."""
    if request.method == 'POST':
        analysis_id = request.POST.get('analysis_id')
        try:
            analysis = AnalysisCT.objects.get(id=analysis_id, user=request.user)
            analysis.is_saved = True 
            analysis.save()
            messages.success(request, 'Results saved successfully!')
        except Analysis.DoesNotExist:
            messages.error(request, 'Analysis not found.')

        return redirect('user_kab') 
    return JsonResponse({'error': 'Invalid request method'}, status=405)


import os
import numpy as np
from django.shortcuts import render
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications import VGG16
from tensorflow.keras.layers import Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.preprocessing.image import ImageDataGenerator

import os
from django.conf import settings

BASE_DIR = os.path.join(settings.BASE_DIR, 'data')
MODEL_PATH = "trained_model.h5"
IMG_SIZE = (128, 128)
BATCH_SIZE = 32

def load_or_train_model():
    if os.path.exists(MODEL_PATH):
        model = load_model(MODEL_PATH)
        print("Модель успешно загружена из 'trained_model.h5'")
        return model

    train_datagen = ImageDataGenerator(rescale=1./255)
    valid_datagen = ImageDataGenerator(rescale=1./255)

    train_generator = train_datagen.flow_from_directory(
        os.path.join(BASE_DIR, 'train'),
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )

    valid_generator = valid_datagen.flow_from_directory(
        os.path.join(BASE_DIR, 'valid'),
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )

    base_model = VGG16(weights='imagenet', include_top=False, input_shape=(128, 128, 3))

    for layer in base_model.layers:
        layer.trainable = False

    x = base_model.output
    x = Flatten()(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.5)(x)
    predictions = Dense(len(train_generator.class_indices), activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)

    model.compile(optimizer=Adam(learning_rate=0.0001),
                  loss='categorical_crossentropy', 
                  metrics=['accuracy'])

    early_stopping = EarlyStopping(monitor='val_loss', patience=5)
    model.fit(train_generator, 
              validation_data=valid_generator, 
              epochs=15, 
              callbacks=[early_stopping])

    model.save(MODEL_PATH)
    print(f"Модель сохранена в '{MODEL_PATH}'")
    return model

model = load_or_train_model()

def get_class_labels(train_generator):
    return {v: k for k, v in train_generator.class_indices.items()}

CLASS_TRANSLATIONS = {
    "Large Cell Carcinoma": "Большеклеточная карцинома",
    "Adenocarcinoma": "Аденокарцинома",
    "Squamous Cell Carcinoma": "Плоскоклеточная карцинома",
    "normal": "Нормальное состояние",
}

def analyze_image2(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file'] 
        uploads_dir = os.path.join(BASE_DIR, 'uploads/analysis')
        os.makedirs(uploads_dir, exist_ok=True)
        saved_image_path = os.path.join(uploads_dir, uploaded_file.name)

        with open(saved_image_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        temp_image_path = os.path.join(BASE_DIR, 'temp', uploaded_file.name)
        os.makedirs(os.path.dirname(temp_image_path), exist_ok=True)
        with open(temp_image_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        img = load_img(temp_image_path, target_size=IMG_SIZE)
        img_array = img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)  

        predicted_probs = model.predict(img_array)
        predicted_index = np.argmax(predicted_probs, axis=1)[0]
        predicted_probability = predicted_probs[0][predicted_index] * 100 

        train_datagen = ImageDataGenerator(rescale=1./255)
        train_generator = train_datagen.flow_from_directory(
            os.path.join(BASE_DIR, 'train'),
            target_size=IMG_SIZE,
            batch_size=BATCH_SIZE,
            class_mode='categorical'
        )
        class_labels = get_class_labels(train_generator)

        predicted_class = class_labels[predicted_index]
        readable_class = CLASS_TRANSLATIONS.get(predicted_class, "Unknown class")
        analysis = AnalysisCT.objects.create(
                user=request.user,
                analysis_file=os.path.relpath(saved_image_path, BASE_DIR),
                
              
                result=f'{predicted_class}: {predicted_probability:.2f}%'
            )   

        os.remove(temp_image_path)
        

        if predicted_probability > 20:
            probability_message = f"{predicted_probability:.2f}"
        else:
            probability_message = "Less than 20%"

        return render(request, 'result2.html', {
            'predicted_class': predicted_class,
            'predicted_probability': probability_message,
            'analysis_id':analysis.id,
        })

    return render(request, 'upload2.html')


from django.http import JsonResponse
from django.utils import timezone
import pdfplumber
import pytesseract
import re
import logging
from .models import BloodAnalysis

def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def extract_text_from_pdf(pdf_path):
    text = ''
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def extract_blood_data(text):
    leukocytes_level = None
    hemoglobin_level = None
    erythrocytes_level = None
    thrombocytes_level = None
    hematocrit_level = None

    hemoglobin_match = re.search(r"hemoglobin\s*[:\-]?\s*([\d.]+)", text, re.IGNORECASE)
    if hemoglobin_match:
        hemoglobin_level = float(hemoglobin_match.group(1))

    leukocytes_match = re.search(r"leukocytes?\s*[:\-]?\s*([\d.]+)", text, re.IGNORECASE)
    if leukocytes_match:
        leukocytes_level = float(leukocytes_match.group(1))

    erythrocytes_match = re.search(r"erythrocytes?\s*[:\-]?\s*([\d.]+)", text, re.IGNORECASE)
    if erythrocytes_match:
        erythrocytes_level = float(erythrocytes_match.group(1))

    thrombocytes_match = re.search(r"thrombocytes?\s*[:\-]?\s*([\d.]+)", text, re.IGNORECASE)
    if thrombocytes_match:
        thrombocytes_level = float(thrombocytes_match.group(1))

    hematocrit_match = re.search(r"hematocrit\s*[:\-]?\s*([\d.]+)", text, re.IGNORECASE)
    if hematocrit_match:
        hematocrit_level = float(hematocrit_match.group(1))

    return leukocytes_level, hemoglobin_level, erythrocytes_level, thrombocytes_level, hematocrit_level



def process_blood_analysis_file(request):
    if request.method == 'POST' and 'file' in request.FILES:
        uploaded_file = request.FILES['file']
        file_path = os.path.join(settings.MEDIA_ROOT, 'uploads/analysis', uploaded_file.name)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            logging.info(f"File uploaded successfully: {file_path}")
        except Exception as e:
            logging.error(f"Error saving file: {str(e)}")
            return JsonResponse({'error': f'Error saving file: {str(e)}'}, status=500)

        text = ''
        try:
            if uploaded_file.name.endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
            elif uploaded_file.name.endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                text = extract_text_from_image(file_path)
            logging.info(f"Extracted text: {text[:100]}...")  
        except Exception as e:
            logging.error(f"Error processing file: {str(e)}")
            return JsonResponse({'error': f'Error processing file: {str(e)}'}, status=500)

        leukocytes_level, hemoglobin_level, erythrocytes_level, thrombocytes_level, hematocrit_level = extract_blood_data(text)

        analysis_data = {
            'leukocytes_level': leukocytes_level,
            'hemoglobin_level': hemoglobin_level,
            'erythrocytes_level': erythrocytes_level,
            'thrombocytes_level': thrombocytes_level,
            'hematocrit_level': hematocrit_level
        }

        BloodAnalysis.objects.create(
            user=request.user,
            analysis_file=uploaded_file.name,
            uploaded_at=timezone.now(),
            leukocytes_level=leukocytes_level,
            hemoglobin_level=hemoglobin_level,
            erythrocytes_level=erythrocytes_level,
            thrombocytes_level=thrombocytes_level,
            hematocrit_level=hematocrit_level
        )

        logging.info(f"Analysis data extracted and saved: {analysis_data}")
        return render(request, 'upload_analysis.html', {'analysis_data': analysis_data})

    return render(request, 'upload_analysis.html')
