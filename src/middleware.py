import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.requests import Request

logger = logging.getLogger('uvicorn.access')
logger.disabled = True


def register_middleware(app:FastAPI):
    
    
    
    @app.middleware('http')
    async def custom_login(request:Request, call_next):
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
        
        
        
    app.add_middleware(
        CORSMiddleware,
        allow_origins = ["*"],
        allow_methods = ["*"] ,
        allow_headers = ["*"],
        allow_credentials = True,
        
        
        )
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost","127.0.0.1"]
    )