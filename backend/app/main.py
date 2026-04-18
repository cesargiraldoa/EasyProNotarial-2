import os
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
from dotenv import load_dotenv

load_dotenv()
settings = get_settings()


class FlexibleCORSMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.allowed_origins = self._load_allowed_origins()
        print(f"[CORS DEBUG] Allowed origins loaded: {sorted(self.allowed_origins)}")

    def _load_allowed_origins(self) -> set[str]:
        origins = {
            "https://easypro-notarial-2.vercel.app",
            "http://127.0.0.1:5179",
            "http://localhost:5179",
            "http://localhost:3000",
        }

        env_values = [
            settings.frontend_url,
            os.getenv("FRONTEND_URL", ""),
            os.getenv("FRONTEND_URLS", ""),
            os.getenv("CORS_ALLOWED_ORIGINS", ""),
        ]
        for value in env_values:
            if not value:
                continue
            for origin in value.split(","):
                cleaned = origin.strip().rstrip("/")
                if cleaned:
                    origins.add(cleaned)
        return origins

    def _is_allowed_origin(self, origin: str) -> bool:
        normalized = origin.rstrip("/")
        if normalized in self.allowed_origins:
            return True
        return normalized.startswith("https://easypro-notarial-2-pr") and normalized.endswith(".vercel.app")

    async def dispatch(self, request: StarletteRequest, call_next):
        origin = request.headers.get("origin", "").rstrip("/")
        is_allowed = self._is_allowed_origin(origin)
        cors_headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
            "Access-Control-Allow-Headers": "Authorization,Content-Type,Accept,Origin,X-Requested-With",
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
