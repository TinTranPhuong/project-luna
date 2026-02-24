from fastapi import Request, status
from fastapi.responses import JSONResponse

# ==============================================================================
# GLOBAL EXCEPTION HANDLERS
# ==============================================================================

async def global_exception_handler(request: Request, exc: Exception):
    """
    Intercepts all unhandled server exceptions and formats them into standard 
    JSON responses to prevent the client UI from breaking.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "path": request.url.path
        },
    )