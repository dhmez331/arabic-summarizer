import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://router.huggingface.co/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {os.getenv('HF_API_KEY')}",
    "Content-Type": "application/json"
}

def summarize_text(text, model_choice="qwen", max_tokens=200):
    # Select model basd  on user choice
    if model_choice == "llama":
        # llamma model from meta
        selected_model = "meta-llama/Llama-3.1-8B-Instruct"
    else:
        # Qwen model
        selected_model = "Qwen/Qwen2.5-72B-Instruct"

    payload = {
        "model": selected_model,
        "messages": [
            {"role": "system", "content": "أنت مساعد ذكي ومحترف. قم بتلخيص النص العربي التالي بإيجاز شديد وبدقة."},
            {"role": "user", "content": text}
        ],
        "max_tokens": max_tokens
    }
    
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    else:
        return f"Error: {response.status_code} - {response.text}"