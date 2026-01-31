from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

settings = get_settings()
GEMINI_API_KEY = settings.gemini_api_key
