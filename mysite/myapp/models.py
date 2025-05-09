from django.db import models

from django.contrib.auth.models import User


class Analysis(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    analysis_file = models.FileField(upload_to='uploads/analysis/',null=True)
    gradcam_path = models.TextField(blank=True, null=True)
    result = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
class AnalysisCT(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    analysis_file = models.FileField(upload_to='uploads/analysis/',null=True)
    gradcam_path = models.TextField(blank=True, null=True)
    result = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
class AnalysisSkin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    analysis_file = models.FileField(upload_to='uploads/analysis/',null=True)
    gradcam_path = models.TextField(blank=True, null=True)
    result = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
class Disease(models.Model):
    name = models.CharField(max_length=200)
    
    
    treatment = models.TextField()
    
    

    def __str__(self):
        return self.name
    
class CTAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    ct_file = models.FileField(upload_to='uploads/ct_analysis/', null=True)
    result = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CT Analysis by {self.user.username} on {self.uploaded_at}"

from django.db import models
from django.contrib.auth.models import User

class BloodAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    analysis_file = models.FileField(upload_to='uploads/analysis/', null=True)
    leukocytes_level = models.FloatField(null=True, blank=True) 
    hemoglobin_level = models.FloatField(null=True, blank=True)  
    erythrocytes_level = models.FloatField(null=True, blank=True)   
    thrombocytes_level=models.FloatField(null=True,blank=True)
    hematocrit_level=models.FloatField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Blood Analysis by {self.user.username} on {self.uploaded_at}"
