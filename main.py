from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

from text_processing import process_text
from model import summarize_text, get_metadata

app = FastAPI(title="Smart Arabic Summarizer API")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Added 'model_choice' to allow dynamic model selection from the frontend
class TextRequest(BaseModel):
    text: str
    model_choice: str = "qwen" 

class MetadataRequest(BaseModel):
    text: str

@app.post("/summarize")
def summarize_arabic_text(request: TextRequest):
    try:
        input_text = request.text
        model_choice = request.model_choice
        
        cleaned_text, original_word_count, cleaned_word_count = process_text(input_text)
        
        # Pass the selected model to the summarization function
        summary_tokens = 400 if cleaned_word_count >= 1500 else 200
        summary = summarize_text(cleaned_text, model_choice, max_tokens=summary_tokens)
        
        return {
            "original_text": input_text,
            "cleaned_text": cleaned_text,
            "original_word_count": original_word_count,
            "cleaned_word_count": cleaned_word_count,
            "summary": summary,
            "model_used": model_choice
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/metadata")
def extract_arabic_metadata(request: MetadataRequest):
    try:
        input_text = request.text
        
        cleaned_text, original_word_count, cleaned_word_count = process_text(input_text)
        
        metadata = get_metadata(cleaned_text, cleaned_word_count)
        
        return {
            "original_word_count": original_word_count,
            "cleaned_word_count": cleaned_word_count,
            "method_used": "direct" if cleaned_word_count < 1500 else "chunking",
            "metadata": metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))