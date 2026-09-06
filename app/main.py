import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.routers import data, chat, conversations

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Personal electricity-consumption AI assistant API"
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,                             # 브라우저의 cross-origin 요청을 허용/제어하는 미들웨어
    allow_origins=settings.cors_origins,        # 이 주소들에서 오는 요청만 브라우저가 허용
    allow_credentials=True,
    allow_methods=["*"],                        # 모든 HTTP 메서드(GET, POST, PUT, DELETE, OPTIONS 등)를 허용
    allow_headers=["*"],
)

# Include Routers
app.include_router(data.router)                 # routers/data.py에 정의된 API들을 메인 앱에 연결
app.include_router(chat.router)
app.include_router(conversations.router)

# Health Check Endpoint
@app.get("/health", tags=["Health"])            # /health 경로에 대한 GET 요청 처리; /health는 백엔드가 정상적으로 동작 중인가?를 빠르게 확인하는 API
async def health_check():                       # 서버 상태 확인용
    """Health check endpoint to verify backend service status."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

# Static Files for Frontend (serves index.html, style.css, app.js, etc. directly at root)
if os.path.exists("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
else:
    @app.get("/", tags=["Root"])
    async def root():
        return {
            "message": f"Welcome to {settings.PROJECT_NAME} API. Visit /docs for documentation.",
            "health": "/health",
            "docs": "/docs"
        }

