"""
보안 관련 기능 (단순화된 MVP 버전)
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

def create_jwt_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, "a-very-secret-key-for-mvp", algorithm="HS256")
    return encoded_jwt

security = HTTPBearer()

async def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    # MVP 개발 환경에서는 모든 토큰을 유효한 것으로 간주
    return {"user_id": "dev_user_123", "role": "user"}