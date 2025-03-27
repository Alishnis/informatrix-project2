from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Analysis,BloodAnalysis

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.objects.filter(username=email).exists():
            messages.error(request, 'A user with this email is already registered.')
        else:
            user = User.objects.create_user(username=email, password=password)
            user.save()
            login(request, user)
            return redirect('analysis_page')
    
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('analysis_page')
        else:
            messages.error(request, 'Incorrect email or password.')
    return render(request, 'register.html')

from .models import AnalysisCT, AnalysisSkin, Analysis  # Модели для разных типов анализов
from django.core import serializers
def user_kab(request):
    """Показать личный кабинет с разным контентом в зависимости от выбранного раздела."""
    selected_section = request.GET.get('section', 'ct')  # Получаем выбранный раздел, по умолчанию "Анализ КТ снимков"

    context = {
        'user': request.user,
    }

    if selected_section == 'ct':
        analyses = AnalysisCT.objects.filter(user=request.user).order_by('-id')
        context.update({
            'section_title': 'Analysis of CT images',
            'analyses': analyses,
        })
    elif selected_section == 'xray':
        analyses = Analysis.objects.filter(user=request.user).order_by('-id')  # Рентген анализы
        context.update({
            'section_title': 'Analysis of X-ray images',
            'analyses': analyses,
        })
    elif selected_section == 'skin':
        analyses = AnalysisSkin.objects.filter(user=request.user).order_by('-id')  # Анализы кожи
        context.update({
            'section_title': 'Skin analysis',
            'analyses': analyses,
        })
    elif selected_section == 'blood':
        analyses = BloodAnalysis.objects.filter(user=request.user).order_by('-id')
        analyses_data = list(analyses.values('uploaded_at', 'leukocytes_level', 'hemoglobin_level', 'erythrocytes_level', 'thrombocytes_level', 'hematocrit_level'))
        
        
        
        
        return render (request, 'blood_analysis_result.html',{'analyses':analyses_data})
        
    
    else:
        context.update({
            'section_title': 'Неизвестный раздел',
            'analyses': [],
        })

    return render(request, 'user_kab.html', context)