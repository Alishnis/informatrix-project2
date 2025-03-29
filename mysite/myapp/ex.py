from transformers import AutoTokenizer, AutoModelForCausalLM
from googletrans import Translator

def main():
    

    symptoms = input("Enter symptoms: ").strip()

    if not symptoms:
        print("You did not enter any symptoms. Please try again.")
        return

    try:
        translator = Translator()

        symptoms_en = translator.translate(symptoms, src='ru', dest='en').text

        print("Loading the model and tokenizer... This might take a few seconds.")
        tokenizer = AutoTokenizer.from_pretrained("microsoft/BioGPT")
        model = AutoModelForCausalLM.from_pretrained("microsoft/BioGPT")

        print("Analyzing symptoms...")
        input_text = f"Patient symptoms: {symptoms_en}. Based on these symptoms, provide possible diagnoses:"
        inputs = tokenizer(input_text, return_tensors="pt")
        outputs = model.generate(
            **inputs,
            max_length=100,
            temperature=0.7,
            do_sample=True,
            top_k=50,
            top_p=0.9,
            num_return_sequences=1
        )

        diagnosis_en = tokenizer.decode(outputs[0], skip_special_tokens=True)

        print(f"\nPossible diagnoses : {diagnosis_en}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()