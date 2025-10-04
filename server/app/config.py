"""
애플리케이션 설정 관리
환경 변수를 로드하고 타입 안전한 설정 객체 제공
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # 앱 기본 설정
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # 데이터베이스
    DATABASE_URL: str = "postgresql://linkcoach_user:linkcoach_pass@localhost:5432/linkcoach"

    # ChromaDB
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_COLLECTION_NAME: str = "leadership_clinical_data"

    # JWT 보안
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Google Gemini API
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 2048

    # ML 모델
    ML_MODEL_PATH: str = "models/leadership_classifier.pkl"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:5183", "http://localhost:3000"]

    # RAG 설정
    RAG_TOP_K: int = 5  # Vector DB에서 검색할 문서 수
    RAG_SIMILARITY_THRESHOLD: float = 0.7  # 유사도 임계값

    # 캐싱
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 3600  # 1시간

    # 스트리밍
    STREAMING_CHUNK_SIZE: int = 10  # 토큰 단위

    # 개발 모드
    USE_MOCK_DATA: bool = False  # 더미 데이터 사용 여부

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )

    @property
    def chroma_url(self) -> str:
        """ChromaDB URL"""
        return f"http://{self.CHROMA_HOST}:{self.CHROMA_PORT}"

    @property
    def is_production(self) -> bool:
        """프로덕션 환경 여부"""
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        """개발 환경 여부"""
        return self.APP_ENV == "development"


# 싱글톤 인스턴스
settings = Settings()
