import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.config import settings
from src.router.login import login_router
from src.router.register import register_router
from src.router.router import router
from src.utils.exceptions import AppError, app_error_handler, unhandled_exception_handler

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

file_handler = RotatingFileHandler(
    LOG_DIR / "app.log",
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8",
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[file_handler, logging.StreamHandler()],
)

app = FastAPI(title="Code generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allow_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(router=router, prefix="/api")
app.include_router(router=login_router, prefix="/api")
app.include_router(router=register_router, prefix="/api")
