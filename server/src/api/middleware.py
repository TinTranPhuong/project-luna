import time
import logging
import os
from fastapi import Request, HTTPException, status, Security
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware

# ==============================================================================
# SECURITY & ENVIRONMENT CONFIGURATION
# ==============================================================================
API_KEY_NAME = "X-LUNA-KEY"
LUNA_API_KEY = os.getenv("LUNA_API_KEY", "luna-super-secret-api-uwu")

# --- LOGGER SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("luna.api")

# ==============================================================================
# MIDDLEWARE COMPONENTS
# ==============================================================================
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Intercepts incoming HTTP requests to measure and log execution times.
    Helps monitor API performance and trace failures.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        logger.info(f"{request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            
            logger.info(
                f"{response.status_code} | {process_time:.2f}ms | {request.url.path}"
            )
            return response
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise e

# ==============================================================================
# AUTHENTICATION
# ==============================================================================
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Validates incoming requests against the configured master API key.
    """
    if api_key != LUNA_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key",
        )
    return api_key