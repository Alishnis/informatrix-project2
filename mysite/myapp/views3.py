from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from transformers import AutoTokenizer, AutoModelForCausalLM
from googletrans import Translator

class SymptomAnalysisView(APIView):
    def post(self, request):
        symptoms = request.data.get('symptoms', '').strip()

        if not symptoms:
            return Response({"error": "No symptoms provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Переводим симптомы на английский
            translator = Translator()
            symptoms_en = translator.translate(symptoms, src='ru', dest='en').text

            # Загружаем модель и токенизатор
            tokenizer = AutoTokenizer.from_pretrained("microsoft/BioGPT")
            model = AutoModelForCausalLM.from_pretrained("microsoft/BioGPT")

            # Формируем входной текст для модели
            input_text = f"Patient symptoms: {symptoms_en}. Based on these symptoms, provide possible diagnoses:"
            inputs = tokenizer(input_text, return_tensors="pt")
            outputs = model.generate(
                **inputs,
                max_length=80,
                temperature=0.7,
                do_sample=True,
                top_k=50,
                top_p=0.8,
                num_return_sequences=1
            )

            # Декодируем результат
            diagnosis_en = tokenizer.decode(outputs[0], skip_special_tokens=True)
            resultind=diagnosis_en.find('provide possible diagnoses:')
            result1=diagnosis_en[resultind:].replace('provide possible diagnoses:','')
            resultfin=result1.split(',')

            return Response({"diagnosis": resultfin}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)