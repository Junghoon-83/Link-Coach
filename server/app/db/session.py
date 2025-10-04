"""
데이터베이스 세션 관리
SQLAlchemy 엔진 및 세션 설정
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
import logging

from app.config import settings
from app.models.database import Base

logger = logging.getLogger(__name__)

# 동기 엔진 (마이그레이션 등에 사용)
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.is_development,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# 동기 세션
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 비동기 엔진 (FastAPI에서 사용)
async_database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
async_engine = create_async_engine(
    async_database_url,
    echo=settings.is_development,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# 비동기 세션
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


def create_tables():
    """
    모든 테이블 생성 (동기)
    프로덕션에서는 Alembic 마이그레이션 사용 권장
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ 데이터베이스 테이블 생성 완료")
    except Exception as e:
        logger.error(f"❌ 테이블 생성 실패: {e}", exc_info=True)
        raise


async def create_tables_async():
    """모든 테이블 생성 (비동기)"""
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ 데이터베이스 테이블 생성 완료 (비동기)")
    except Exception as e:
        logger.error(f"❌ 테이블 생성 실패: {e}", exc_info=True)
        raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI Dependency로 사용할 비동기 DB 세션

    Usage:
        @app.get("/items")
        async def read_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_db_sync() -> Session:
    """동기 DB 세션 (스크립트 등에서 사용)"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def check_db_connection() -> bool:
    """데이터베이스 연결 확인"""
    try:
        async with async_engine.connect() as conn:
            await conn.execute("SELECT 1")
        logger.info("✅ 데이터베이스 연결 확인")
        return True
    except Exception as e:
        logger.error(f"❌ 데이터베이스 연결 실패: {e}")
        return False
