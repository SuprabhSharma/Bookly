import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.requests import Request
import logging
import time

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

    # CORS — read from env; do NOT combine allow_origins=["*"] with allow_credentials=True
    cors_origins_raw = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
    cors_origins: List[str] = [o.strip() for o in cors_origins_raw.split(",") if o.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    # Trusted hosts — read from env
    trusted_hosts_raw = os.getenv("TRUSTED_HOSTS", "localhost,127.0.0.1")
    trusted_hosts: List[str] = [h.strip() for h in trusted_hosts_raw.split(",") if h.strip()]

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=trusted_hosts,
    )