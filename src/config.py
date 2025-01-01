import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

GEMINI_CONFIG = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

STORAGE_BASE_URL = "http://127.0.0.1:54321/storage/v1/object/public/screens" 