import requests
import os
import json 
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

def extract_metadata(text):
    payload = {
        "model": "Qwen/Qwen2.5-72B-Instruct",
        "messages": [
            {
                "role": "system",
                "content": """أنت محلل نصوص عربي محترف. مهمتك استخراج البيانات الوصفية من النص.
يجب أن ترد فقط بـ JSON صالح بهذا الشكل بالضبط، بدون أي نص إضافي:
{
  "topics": ["الموضوع الرئيسي 1", "الموضوع الرئيسي 2"],
  "tags": ["وسم1", "وسم2", "وسم3"],
  "keywords": ["كلمة1", "كلمة2", "كلمة3", "كلمة4", "كلمة5"],
  "language": "فصحى أو لهجة"
}"""
            },
            {
                "role": "user",
                "content": f"استخرج البيانات الوصفية من النص التالي:\n\n{text}"
            }
        ],
        "max_tokens": 300
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        raw = response.json()['choices'][0]['message']['content'].strip()
        cleaned = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
    else:
        return {"error": f"{response.status_code} - {response.text}"}


def extract_metadata_chunked(text, chunk_size=500):
    # 1. Split the text into a list of words
    words = text.split()
    
    # 2. Divide the words into chunks
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    
    # 3. Extract metadata from each chunk
    all_topics = []
    all_tags = []
    all_keywords = []
    
    for chunk in chunks:
        result = extract_metadata(chunk)
        
        if "error" not in result:
            all_topics.extend(result.get("topics", []))
            all_tags.extend(result.get("tags", []))
            all_keywords.extend(result.get("keywords", []))
    
    # 4. Merge results and remove duplicates
    return {
        "topics": list(set(all_topics)),
        "tags": list(set(all_tags)),
        "keywords": list(set(all_keywords)),
        "language": "multi-part"
    }

# Decied which to use (LLM or Chunking+LLM)
def get_metadata(text, word_count):
    if word_count < 1500:
        return extract_metadata(text)
    else:
        return extract_metadata_chunked(text)