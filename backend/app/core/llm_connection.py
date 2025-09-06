import google.generativeai as genai
import logging
import inspect
from functools import lru_cache

from app.core.config import settings
from app.core.logger import logs

@lru_cache(maxsize=1) # Cache the client instance
def get_gemini_client():
    """
    Initializes and returns a Google Gemini client instance.
    The client is cached to avoid re-initialization on every call.
    """
    log_name = inspect.stack()[0]
    if not settings.GEMINI_API_KEY:
        logs.define_logger(logging.CRITICAL, None, log_name, message="FATAL: GEMINI_API_KEY is not set in environment variables.")
        raise ValueError("GEMINI_API_KEY is not configured.")

    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Optional: Test a simple model listing to verify connection
        # for m in genai.list_models():
        #     if 'generateContent' in m.supported_generation_methods:
        #         logs.define_logger(logging.INFO, None, log_name, message=f"Found Gemini model: {m.name}")
        logs.define_logger(logging.INFO, None, log_name, message="Gemini API client configured successfully.")
        return genai
    except Exception as e:
        logs.define_logger(logging.CRITICAL, None, log_name, message=f"FATAL: Failed to configure Gemini API client: {e}")
        raise ConnectionError(f"Failed to configure Gemini API client: {e}")