from app.core.config import get_settings
from google import genai

settings = get_settings()

if not settings.gemini_api_key:
    raise RuntimeError("GEMINI_API_KEY is missing from configuration")

client = genai.Client(
    api_key=settings.gemini_api_key
)
