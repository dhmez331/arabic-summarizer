# 🤖 Smart Arabic Article Summarizer API

**End-to-End Arabic NLP Application Deployed on OCI**

> Developed by: Abdulrahman Awadh Asban
> Internship @ Innovation Team — Riyadh, Saudi Arabia
> February–March 2026

---

## 📌 Project Overview

This project is a complete Arabic NLP pipeline that:

1. Accepts Arabic text input (Modern Standard Arabic or dialects)
2. Cleans and normalizes the text (removes diacritics, normalizes characters, strips punctuation)
3. Sends the cleaned text to a Hugging Face-hosted LLM via the Inference API
4. Returns a structured JSON response with the original text, cleaned text, word counts, and an AI-generated summary
5. Exposes the pipeline as a REST API via FastAPI
6. Provides an HTML interface for browser-based testing
7. Deployed on Oracle Cloud Infrastructure (OCI)

---

## 🧱 System Architecture

```
User (HTML Page)
      ↓
FastAPI Backend (main.py)
      ↓
Arabic Text Preprocessing (text_processing.py)
      ↓
Hugging Face Inference API (model.py)
      ↓
Structured JSON Response
      ↓
Display in HTML
```

> **Why Hugging Face Inference API instead of loading the model locally?**
> Loading Arabic LLMs locally requires 8GB+ of RAM. Using the Inference API offloads model execution to Hugging Face servers, keeping the OCI VM lightweight and the solution 100% free.

---

## 📁 Project Structure

```
arabic_summarizer/
│
├── main.py              → FastAPI app & /summarize endpoint
├── text_processing.py   → Arabic text cleaning functions
├── model.py             → Hugging Face Inference API integration
├── templates/
│   └── index.html       → HTML testing interface
├── .env                 → API keys (Hidden by .gitignore file)
├── requirements.txt     → Project dependencies
└── README.md            → Project documentation
```

---

## ⚙️ Technical Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3 |
| API Framework | FastAPI + Uvicorn |
| AI Integration | Hugging Face Inference API |
| Models | Qwen/Qwen2.5-72B-Instruct, meta-llama/Llama-3.1-8B-Instruct |
| Frontend | HTML + JavaScript (Fetch API) |
| Cloud Platform | Oracle Cloud Infrastructure (OCI) |
| Secret Management | python-dotenv |

---

## 🔧 Arabic Text Processing

Implemented in `text_processing.py` using Python's `re` (Regular Expressions) module.

### Processing Steps

| Step | What it does | Example |
|------|-------------|---------|
| 1. Remove diacritics | Strips all harakat (tashkeel) using Unicode range `\u064B–\u0652` | كَتَبَ → كتب |
| 2. Normalize Alef | Converts أ إ آ → ا | انسان → إنسان |
| 3. Remove punctuation | Strips non-Arabic, non-space characters | removes ، . ! etc. |
| 4. Remove numbers | Removes Arabic (٠-٩) and Western (0-9) digits | |
| 5. Collapse whitespace | Replaces multiple spaces with single space | |

### Why Regular Expressions?

`re` is Python's built-in library for pattern matching. It was chosen over specialized Arabic NLP libraries (like camel-tools or farasa) because:
- No installation required beyond standard Python
- Sufficient for structural text cleaning tasks
- Lightweight and fast for deployment on a small OCI VM

---

## 🤖 AI Model Integration

Implemented in `model.py` using the Hugging Face Inference API via `requests`.

### Models Used & Why

**Qwen/Qwen2.5-72B-Instruct**
- Developed by Alibaba Cloud
- Strong multilingual capabilities with excellent Arabic support
- Handles both Modern Standard Arabic and dialects well
- Available on Hugging Face Inference API free tier

**meta-llama/Llama-3.1-8B-Instruct**
- Developed by Meta
- Lightweight (8B parameters), fast response
- Included for A/B testing and model comparison

### Why not ALLaM (علام)?

ALLaM-7B was tested but returned an error: `model too large to be loaded automatically`. Hugging Face restricts models larger than 10GB from the free Serverless Inference API unless individual permission is granted. This is a known limitation documented in the Hugging Face community forums.

### Model Evaluation Results

After testing both models on 6 Arabic texts (Formal Arabic, Riyadh dialect, Jeddah dialect):

| | Formal Arabic | Riyadh Dialect | Jeddah Dialect |
|---|---|---|---|
| **Qwen 2.5** | ✅ Excellent | ✅ Excellent | ✅ Excellent |
| **LLaMA 3.1** | ⚠️ Code-switching (mixed Polish/English words) | ⚠️ Hallucination (`_FOLLOW`) | ❌ Complete breakdown (Chinese characters appeared) |

**Conclusion:** Qwen 2.5 significantly outperforms LLaMA 3.1 on Arabic text, especially dialectal Arabic. This is likely due to larger Arabic training data in Qwen's pretraining corpus.

---

## 🚀 FastAPI Backend

Implemented in `main.py`.

### Endpoint

```
POST /summarize
```

**Request Body (JSON):**
```json
{
  "text": "النص العربي هنا",
  "model_choice": "qwen"
}
```

`model_choice` options: `"qwen"` (default) or `"llama"`

**Response (JSON):**
```json
{
  "original_text": "...",
  "cleaned_text": "...",
  "original_word_count": 95,
  "cleaned_word_count": 94,
  "summary": "...",
  "model_used": "qwen"
}
```

### Why FastAPI?

- Automatic documentation at `/docs` (Swagger UI)
- Built-in data validation via Pydantic
- High performance (async-capable)
- Industry standard for Python APIs

### CORS Middleware

`CORSMiddleware` is added to allow the HTML frontend (served from a different origin) to communicate with the API without being blocked by the browser's same-origin policy.

---

## 🌐 HTML Interface

Located in `templates/index.html`.

- Arabic text input (RTL layout)
- Model selector (A/B Testing between Qwen and LLaMA)
- Displays: summary, word counts before/after cleaning, cleaned text
- Communicates with FastAPI via JavaScript `fetch()` POST requests

---

## ☁️ Deployment on OCI

### VM Details
- **Provider:** Oracle Cloud Infrastructure (OCI)
- **Region:** Saudi Arabia Central (Riyadh)
- **OS:** Ubuntu (Linux)
- **Instance Name:** Abdulrahman test

### Deployment Steps

**1. Connect to VM:**
```bash
ssh -i ssh-key-2026-01-29.key opc@<PUBLIC_IP>
```

**2. Install dependencies:**
```bash
sudo apt update
sudo apt install python3-pip python3-venv -y
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn requests python-dotenv
```

**3. Upload project files and create `.env`:**
```bash
echo "HF_API_KEY=your_key_here" > .env
```

**4. Run the server:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

**5. Configure OCI Security List:**
Open port 8000 in the OCI Console → VCN → Security List → Add Ingress Rule.

**6. Access the app:**
```
http://<PUBLIC_IP>:8000/docs
```

---

## 🔒 Security Notes

- API keys are stored in `.env` and never hardcoded in source files
- `.env` is excluded from version control (add to `.gitignore`)
- SSH private key permissions are restricted using `icacls` on Windows to comply with OpenSSH requirements

---

## 📦 Installation (Local)

```bash
# Clone the project
git clone <repo-url>
cd arabic_summarizer

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo HF_API_KEY=your_key_here > .env

# Run
uvicorn main:app --reload
```

---

## 📚 References & Resources

### Official Documentation

| Resource | URL |
|----------|-----|
| Hugging Face Inference Providers Docs | https://huggingface.co/docs/inference-providers/providers/hf-inference |
| Python `re` Module Documentation | https://docs.python.org/3/library/re.html |
| Requests Library — POST Requests | https://requests.readthedocs.io/en/latest/user/quickstart/#more-complicated-post-requests |
| HTTP Status Codes — MDN | https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status |
| Unicode Arabic Block (U+0600–U+06FF) | https://unicode.org/charts/PDF/U0600.pdf |

### Arabic NLP References

| Resource | URL |
|----------|-----|
| Removing Arabic Diacritics using Python — Stack Overflow | https://stackoverflow.com/questions/66988153/removing-arabic-diacritics-using-python |
| Unicode Explorer (Arabic character lookup) | https://unicode-explorer.com/search/ |
| Arabic NLP Survey — MDPI Computers Journal | https://www.mdpi.com/2073-431X/14/11/497 |

### Tutorials & Guides

| Resource | URL |
|----------|-----|
| FastAPI Official Tutorial | https://fastapi.tiangolo.com/tutorial/ |
| FastAPI — Request Body with Pydantic | https://fastapi.tiangolo.com/tutorial/body/ |
| Hugging Face — Text Generation Task | https://huggingface.co/tasks/text-generation |
| OCI — Connect to Linux Instance via SSH | https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/accessinginstance.htm |
| OCI — Security Lists and Ingress Rules | https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/securitylists.htm |
| python-dotenv Documentation | https://pypi.org/project/python-dotenv/ |
| Pydantic V2 Documentation | https://docs.pydantic.dev/latest/ |
| Arabic NLP Challenges — Towards Data Science | https://towardsdatascience.com/arabic-nlp-unique-challenges-and-their-solutions |
| Qwen2.5 Model Card — Hugging Face | https://huggingface.co/Qwen/Qwen2.5-72B-Instruct |
| LLaMA 3.1 Model Card — Hugging Face | https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct |

---

*This project was developed as part of an AI internship at Innovation Team, Riyadh, Saudi Arabia.*