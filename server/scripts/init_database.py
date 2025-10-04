"""
데이터베이스 초기화 스크립트
PostgreSQL 테이블 생성 및 초기 데이터 설정
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from sqlalchemy import text
import logging

from app.db.session import async_engine, create_tables_async, check_db_connection
from app.models.database import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_database():
    """데이터베이스 초기화"""
    try:
        logger.info("데이터베이스 연결 확인 중...")

        # 연결 확인
        is_connected = await check_db_connection()
        if not is_connected:
            logger.error("❌ 데이터베이스 연결 실패")
            logger.info("다음을 확인하세요:")
            logger.info("1. PostgreSQL 컨테이너가 실행 중인가? (docker-compose ps)")
            logger.info("2. .env 파일의 DATABASE_URL이 올바른가?")
            return

        logger.info("✅ 데이터베이스 연결 성공")

        # 테이블 생성
        logger.info("테이블 생성 중...")
        await create_tables_async()

        # 테이블 확인
        async with async_engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))

            tables = [row[0] for row in result]
            logger.info(f"생성된 테이블: {', '.join(tables)}")

        logger.info("✅ 데이터베이스 초기화 완료!")
        logger.info("""
생성된 테이블:
- reports: AI 생성 리포트 저장
- conversations: Q&A 대화 로그
- vector_documents: ChromaDB 문서 메타데이터
- api_logs: API 요청 로그
        """)

    except Exception as e:
        logger.error(f"❌ 데이터베이스 초기화 실패: {e}", exc_info=True)
        raise
    finally:
        await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_database())
