import httpx
from app.core.config import get_settings

settings = get_settings()

if not settings.gemini_api_key:
    raise RuntimeError("❌ DeepSeek API key missing")

DEEPSEEK_API_KEY = settings.gemini_api_key.strip()
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"


async def get_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=45.0,
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
    )
