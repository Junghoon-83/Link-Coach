"""
Link-Coach FastAPI Application
AI 기반 개인화 코칭 서비스 백엔드
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.core.logging import setup_logging
from app.api.v1.router import api_router

# 로깅 설정
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행되는 로직"""
    # 시작 시
    logger.info("🚀 Link-Coach 서버 시작 중...")
    logger.info(f"환경: {settings.APP_ENV}")
    logger.info(f"데이터베이스: {settings.DATABASE_URL}")

    # ML 모델 로드 (비동기, 실패해도 서버는 시작)
    try:
        from app.services.ml_model import ml_model_service
        # 백그라운드에서 로드 (블로킹 방지)
        logger.info("ML 모델 로드 시작...")
        # await ml_model_service.load_model()  # 임시 비활성화
        logger.info("⏩ ML 모델 로드 스킵 (백그라운드 처리)")
    except Exception as e:
        logger.warning(f"⚠️ ML 모델 로드 실패 (계속 진행): {e}")

    # Vector DB 연결 확인 (비동기, 실패해도 서버는 시작)
    try:
        from app.services.vector_db import vector_db_service
        logger.info("ChromaDB 연결 확인 중...")
        # await vector_db_service.health_check()  # 임시 비활성화
        logger.info("⏩ ChromaDB 연결 스킵 (첫 요청 시 연결)")
    except Exception as e:
        logger.warning(f"⚠️ ChromaDB 연결 실패 (계속 진행): {e}")

    logger.info("✅ 서버 시작 완료 - 요청 대기 중...")

    yield

    # 종료 시
    logger.info("🛑 Link-Coach 서버 종료 중...")


# FastAPI 앱 생성
app = FastAPI(
    title="Link-Coach API",
    description="AI 기반 리더십 개인화 코칭 서비스",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url="/redoc" if settings.APP_ENV != "production" else None,
)


# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)


# 전역 예외 처리
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """모든 예외를 처리하는 글로벌 핸들러"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.APP_ENV != "production" else "An error occurred"
        }
    )


# 헬스체크 엔드포인트
@app.get("/health", tags=["Health"])
async def health_check():
    """서버 헬스체크"""
    return {
        "status": "healthy",
        "service": "Link-Coach API",
        "version": "0.1.0",
        "environment": settings.APP_ENV
    }


# API 라우터 등록
app.include_router(api_router, prefix="/api")


# 루트 엔드포인트
@app.get("/", tags=["Root"])
async def root():
    """API 루트"""
    return {
        "message": "Link-Coach API",
        "docs": "/docs",
        "health": "/health"
    }


# 개발 전용: 테스트 토큰 생성
@app.get("/dev/token", tags=["Development"])
async def get_dev_token():
    """개발용 임시 JWT 토큰 생성 (프로덕션에서는 비활성화)"""
    if settings.APP_ENV != "development":
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only available in development mode"
        )

    from app.core.security import create_jwt_token

    token = create_jwt_token({
        "user_id": "dev_user_123",
        "email": "dev@example.com",
        "role": "user"
    })

    return {
        "token": token,
        "user_id": "dev_user_123",
        "usage": "Add this token to Authorization header as 'Bearer <token>'"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.APP_ENV == "development" else False,
        log_level=settings.LOG_LEVEL.lower()
    )
