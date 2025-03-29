import random
import uuid
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_random_value(min_value, max_value, decimal_places=2):
    return round(random.uniform(min_value, max_value), decimal_places)

def generate_blood_analysis_pdf():
    unique_filename = f"{uuid.uuid4().hex[:3]}.pdf" 
    c = canvas.Canvas(unique_filename, pagesize=letter)
    width, height = letter 

    c.setFont("Helvetica-Bold", 14)
    c.drawString(200, 750, "Blood Analysis Report")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 700, "Attribute")
    c.drawString(250, 700, "Blood Test")
    c.drawString(400, 700, "Value")

    c.setFont("Helvetica", 12)
    
    hemoglobin_value = generate_random_value(12.0, 16.0) 
    c.drawString(100, 680, "Hemoglobin")
    c.drawString(250, 680, "Hemoglobin")
    c.drawString(400, 680, f"{hemoglobin_value} g/dL")
    
    leukocytes_value = generate_random_value(4.0, 10.0) 
    c.drawString(100, 660, "Leukocytes")
    c.drawString(250, 660, "Leukocytes")
    c.drawString(400, 660, f"{leukocytes_value} x10^3/μL")

    erythrocytes_value = generate_random_value(4.5, 5.9) 
    c.drawString(100, 640, "Erythrocytes")
    c.drawString(250, 640, "Erythrocytes")
    c.drawString(400, 640, f"{erythrocytes_value} million/μL")

    thrombocytes_value = generate_random_value(150, 400)  
    c.drawString(100, 620, "Thrombocytes")
    c.drawString(250, 620, "Thrombocytes")
    c.drawString(400, 620, f"{thrombocytes_value} x10^3/μL")
    
    hematocrit_value = generate_random_value(40, 50) 
    c.drawString(100, 600, "Hematocrit")
    c.drawString(250, 600, "Hematocrit")
    c.drawString(400, 600, f"{hematocrit_value}%")

    c.save()

generate_blood_analysis_pdf()
