import logging

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def setup_exception_handlers(app, templates: Jinja2Templates):
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        is_api = (
            request.url.path.startswith("/api/")
            or request.headers.get("accept") == "application/json"
        )
        
        if is_api:
            return JSONResponse(
                status_code=exc.status_code, content={"detail": exc.detail}
            )
        
        titles = {
            400: "Некорректный запрос",
            401: "Требуется авторизация",
            404: "Страница не найдена",
            500: "Ошибка сервера",
        }
        
        if exc.status_code >= 400:
            logger.warning(
                "HTTP Ошибка %d: %s (URL: %s)", 
                exc.status_code, 
                str(exc.detail), 
                request.url.path
            )

        return templates.TemplateResponse(
            request,
            "error.html",
            {
                "request": request,
                "status_code": exc.status_code,
                "title": titles.get(exc.status_code, "Ошибка"),
                "message": str(exc.detail),
            },
            status_code=exc.status_code,
        )

    @app.exception_handler(HTTPException)
    async def admin_auth_handler(request: Request, exc: HTTPException):
        if exc.status_code == 401 and request.url.path.startswith("/admin"):
            logger.info("Редирект неавторизованного пользователя на /admin -> /login")
            return RedirectResponse(
                url=f"/login?next={request.url.path}", status_code=302
            )
        
        logger.warning("HTTPException %d: %s", exc.status_code, exc.detail)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})