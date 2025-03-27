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
    width, height = letter  # Default letter size is 8.5 x 11 inches

    # Title of the PDF
    c.setFont("Helvetica-Bold", 14)
    c.drawString(200, 750, "Blood Analysis Report")

    # Table headers
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 700, "Attribute")
    c.drawString(250, 700, "Blood Test")
    c.drawString(400, 700, "Value")

    # Table data
    c.setFont("Helvetica", 12)
    
    # Row 1 - Hemoglobin
    hemoglobin_value = generate_random_value(12.0, 16.0)  # Hemoglobin range: 12.0 to 16.0 g/dL
    c.drawString(100, 680, "Hemoglobin")
    c.drawString(250, 680, "Hemoglobin")
    c.drawString(400, 680, f"{hemoglobin_value} g/dL")
    
    # Row 2 - Leukocytes
    leukocytes_value = generate_random_value(4.0, 10.0)  # Leukocytes range: 4.0 to 10.0 x10^3/μL
    c.drawString(100, 660, "Leukocytes")
    c.drawString(250, 660, "Leukocytes")
    c.drawString(400, 660, f"{leukocytes_value} x10^3/μL")

    # Row 3 - Erythrocytes (Red Blood Cells)
    erythrocytes_value = generate_random_value(4.5, 5.9)  # Erythrocytes range: 4.5 to 5.9 million/μL
    c.drawString(100, 640, "Erythrocytes")
    c.drawString(250, 640, "Erythrocytes")
    c.drawString(400, 640, f"{erythrocytes_value} million/μL")

    # Row 4 - Platelets (Thrombocytes)
    thrombocytes_value = generate_random_value(150, 400)  # Thrombocytes range: 150 to 400 x10^3/μL
    c.drawString(100, 620, "Thrombocytes")
    c.drawString(250, 620, "Thrombocytes")
    c.drawString(400, 620, f"{thrombocytes_value} x10^3/μL")
    
    # Row 5 - Hematocrit
    hematocrit_value = generate_random_value(40, 50)  # Hematocrit range: 40% to 50%
    c.drawString(100, 600, "Hematocrit")
    c.drawString(250, 600, "Hematocrit")
    c.drawString(400, 600, f"{hematocrit_value}%")

    c.save()

generate_blood_analysis_pdf()
