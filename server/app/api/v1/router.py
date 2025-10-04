"""
API v1 라우터 통합
모든 v1 엔드포인트를 하나의 라우터로 통합
"""
from fastapi import APIRouter

from app.api.v1.endpoints import coaching

# v1 API 라우터
api_router = APIRouter(prefix="/v1")

# 엔드포인트 라우터 등록
api_router.include_router(coaching.router, tags=["Coaching"])

# 향후 추가될 라우터들
# api_router.include_router(users.router, tags=["Users"])
# api_router.include_router(analytics.router, tags=["Analytics"])
