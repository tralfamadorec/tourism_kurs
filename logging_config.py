import json
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import settings

def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_obj = {
                "timestamp": self.formatTime(record),
                "level": record.levelname,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }
            if record.exc_info:
                log_obj["exception"] = self.formatException(record.exc_info)
            return json.dumps(log_obj, ensure_ascii=False)

    formatter = JsonFormatter() if not settings.DEBUG else logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    app_handler = RotatingFileHandler(
        log_dir / "app.log", maxBytes=10*1024*1024, backupCount=5, encoding="utf-8"
    )
    app_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    app_handler.setFormatter(formatter)
    root_logger.addHandler(app_handler)

    error_handler = RotatingFileHandler(
        log_dir / "error.log", maxBytes=10*1024*1024, backupCount=5, encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING if not settings.DEBUG else logging.INFO)

    logging.info("Логирование настроено")