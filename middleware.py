import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        
        try:
            response = await call_next(request)
        except Exception as exc:
            logger.error(f"Unhandled exception in {request.method} {request.url.path}", exc_info=exc)
            raise
        
        process_time = time.time() - start_time
        client_ip = request.client.host if request.client else "unknown"
        
        logger.info(
            f"{request.method} {request.url.path} | "
            f"status={response.status_code} | "
            f"time={process_time:.3f}s | "
            f"ip={client_ip}"
        )
        return response