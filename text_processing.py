import re

def clean_arabic_text(text):
    # 1. Remove diacritics (harakat) from the text
    # Using Unicode
    text = re.sub(r'[\u064B-\u0652]', '', text)
    
    # 2. Normalize characters
    text = re.sub(r'[أإآ]', 'ا', text)
    
    # 3. Remove punctuation and symbols
    text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
    text = re.sub(r'[0-9٠-٩]', '', text)
    
    # 4. Remove redundant spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def process_text(text):
    # Computes word counts before and after cleaning
    
    # Count words in the original text
    original_word_count = len(text.split())
    
    # Apply the cleaning function
    cleaned_text = clean_arabic_text(text)
    
    # Count words in the cleaned text
    cleaned_word_count = len(cleaned_text.split())
    
    return cleaned_text, original_word_count, cleaned_word_count

