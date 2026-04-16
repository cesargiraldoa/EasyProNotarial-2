from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response

from app.api.router import api_router
from app.core.config import get_settings
from app.db.init_db import init_db
from app.db.session import SessionLocal

settings = get_settings()


class FlexibleCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        origin = request.headers.get("origin", "")
        allowed = {
            settings.frontend_url.rstrip("/"),
            "http://localhost:5179",
            "http://127.0.0.1:5179",
        }
        is_allowed = (
            origin in allowed
            or origin.endswith(".vercel.app")
            or origin.endswith(".railway.app")
            or origin.endswith(".easypro.co")
        )
        cors_headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Authorization, Content-Type, Accept, Origin, X-Requested-With",
            "Access-Control-Max-Age": "600",
        }
        if request.method == "OPTIONS":
            if is_allowed:
                return Response(status_code=200, headers=cors_headers)
            return Response(status_code=400)
        response = await call_next(request)
        if is_allowed:
            for key, value in cors_headers.items():
                response.headers[key] = value
        return response


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(FlexibleCORSMiddleware)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health")
def health():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
    finally:
        db.close()
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
    }