# 🏥 Informatrix AI Project

This is an AI-powered medical diagnosis system that uses deep learning models to analyze **CT scans, X-rays, and skin images**. The project was developed for **Informatrix 2025 (AI Programming section)**.

## 🚀 Features
- 📸 **Medical Image Analysis** (CT, X-ray, skin images)
- 🤖 **AI-powered Symptom Diagnosis** using `BioGPT`
- 🌍 **Multi-language Support** (Uses `googletrans` for translation)
- 🏥 **Fast & Automated Analysis** with `torch`, `tensorflow`, and `grad-cam`

---

## 📦 Technologies Used
- **Backend**: Django, Django REST Framework
- **Machine Learning**: PyTorch, TensorFlow, Transformers (Hugging Face)
- **Medical Imaging**: OpenCV, PIL, Pytorch Grad-CAM
- **Translation**: `googletrans`
- **Database**: MySQL 

---

## 🔧 Installation Guide

Follow these steps to set up the project:

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/Alishnis/informatrix-project2.git
cd informatrix-ai-project

2️⃣ Create a Virtual Environment

python -m venv venv
source venv/bin/activate  # For macOS/Linux
venv\Scripts\activate  # For Windows

3️⃣ Install Dependencies

pip install -r requirements.txt

4️⃣ Run Migrations

python manage.py makemigrations
python manage.py migrate

5️⃣ Start the Development Server

python manage.py runserver

Now, open your browser and go to http://127.0.0.1:8000/analysis (main page) to see the project in action!

🛠 How to Use
	1.	📂 Upload a medical image (CT scan, X-ray, or skin image).
	2.	🏥 AI analyzes the image and provides diagnosis suggestions.
	3.	🔍 View results & explanations (with heatmaps for Grad-CAM).
	4.	🌍 Translate results if needed.

📞 Contact

For questions or suggestions, feel free to reach out:
	•	✉️ Email: romankulalisher@gmail.com
	
