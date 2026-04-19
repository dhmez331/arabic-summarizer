import re
import os
import requests
from dotenv import load_dotenv
from hijridate import Hijri
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever

load_dotenv()

API_URL = "https://router.huggingface.co/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {os.getenv('HF_API_KEY')}",
    "Content-Type": "application/json"
}

EMBEDDING_MODELS = {
    "e5-large": "intfloat/multilingual-e5-large",
    "mpnet":    "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
    "minilm":   "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
}

HIJRI_MONTHS = [
    "محرم", "صفر", "ربيع الأول", "ربيع الثاني",
    "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان",
    "رمضان", "شوال", "ذو القعدة", "ذو الحجة"
]


# ═══════════════════════════════════════════
# تحويل الأرقام العربية
# ═══════════════════════════════════════════

def normalize_digits(text):
    for i in range(10):
        text = text.replace(chr(0x0660 + i), str(i))
    return text

def clean_for_rag(text):
    text = re.sub(r'[\u064B-\u0652]', '', text)
    return text

# ═══════════════════════════════════════════
# مسار RAG — Hybrid Search
# ═══════════════════════════════════════════

def build_rag(text, model_key="minilm"):
    normalized_text = normalize_digits(clean_for_rag(text))

    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    chunks = splitter.split_text(normalized_text)

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODELS[model_key])
    faiss_store = FAISS.from_texts(chunks, embeddings)
    faiss_retriever = faiss_store.as_retriever(search_kwargs={"k": 3})

    bm25_retriever = BM25Retriever.from_texts(chunks)
    bm25_retriever.k = 5

    hybrid_retriever = EnsembleRetriever(
        retrievers=[faiss_retriever, bm25_retriever],
        weights=[0.5, 0.5]
    )

    return hybrid_retriever


def retrieve_date_chunks(retriever):
    queries = [
        "تاريخ هجري بالأرقام",
        "تاريخ هجري مكتوب بالحروف",
        "شهر هجري",
    ]
    seen = set()
    chunks = []
    for query in queries:
        for doc in retriever.invoke(query):
            if doc.page_content not in seen:
                seen.add(doc.page_content)
                chunks.append(doc.page_content)
    return chunks


def extract_dates_from_chunks(chunks):
    all_text = " ".join(chunks)
    return extract_dates_regex(all_text)


def display_with_llm(chunks):
    context = "\n".join(chunks)
    payload = {
        "model": "Qwen/Qwen2.5-72B-Instruct",
        "provider": "novita",
        "messages": [
            {
                "role": "system",
                "content": "اعرض فقط التواريخ الهجرية الموجودة في النص، كل تاريخ في سطر، بدون أي كلام إضافي."
            },
            {
                "role": "user",
                "content": context
            }
        ],
        "max_tokens": 200
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content'].strip()
    return f"Error: {response.status_code}"


# ═══════════════════════════════════════════
# مسار Regex — مرجع المقارنة (مستقل)
# ═══════════════════════════════════════════

def extract_dates_regex(text):
    normalized = normalize_digits(text)
    found = set()

    pattern_normal   = r'(0?[1-9]|[12][0-9]|30)[\/\-\.](0?[1-9]|1[0-2])[\/\-\.](1[0-9]{3})'
    pattern_reversed = r'(1[0-9]{3})[\/\-\.](0?[1-9]|1[0-2])[\/\-\.](0?[1-9]|[12][0-9]|30)'

    for m in re.finditer(pattern_normal, normalized):
        day, month, year = m.groups()
        try:
            Hijri(int(year), int(month), int(day))
            found.add(m.group())
        except ValueError:
            pass

    for m in re.finditer(pattern_reversed, normalized):
        year, month, day = m.groups()
        try:
            Hijri(int(year), int(month), int(day))
            found.add(m.group())
        except ValueError:
            pass

    for month in HIJRI_MONTHS:
        if month in text:
            found.add(month)

    return list(found)


# ═══════════════════════════════════════════
# الدالة الرئيسية
# ═══════════════════════════════════════════

def run_evaluation(text, model_key="minilm"):
    retriever   = build_rag(text, model_key)
    rag_chunks  = retrieve_date_chunks(retriever)
    rag_dates   = extract_dates_from_chunks(rag_chunks)
    llm_display = display_with_llm(rag_chunks)
    regex_dates = extract_dates_regex(text)

    return {
        "embedding_model": EMBEDDING_MODELS[model_key],
        "rag_chunks":      rag_chunks,
        "rag_dates":       rag_dates,
        "rag_display":     llm_display,
        "regex_dates":     regex_dates,
    }