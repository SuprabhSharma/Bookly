from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.requests import Request
import logging
import time

from .config import Config

logger = logging.getLogger("uvicorn.access")
logger.disabled = True


def register_middleware(app: FastAPI):

    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        processing_time = time.time() - start_time
        client = request.client
        client_address = (
            f"{client.host}:{client.port}" if client is not None else "unknown"
        )
        message = (
            f"{client_address} - {request.method} - {request.url.path} - "
            f"{response.status_code} completed after {processing_time:.4f}s"
        )
        print(message)
        return response

    # Values are loaded from backend/.env through Config.
    # Do not combine allow_origins=["*"] with allow_credentials=True.
    cors_origins: List[str] = [
        origin.strip()
        for origin in Config.CORS_ORIGINS.split(",")
        if origin.strip()
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    trusted_hosts: List[str] = [
        host.strip()
        for host in Config.TRUSTED_HOSTS.split(",")
        if host.strip()
    ]

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=trusted_hosts,
    )