"""
SQLAlchemy 데이터베이스 모델
PostgreSQL 테이블 정의
"""
from sqlalchemy import Column, String, Text, DateTime, JSON, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class Report(Base):
    """리포트 테이블 - AI 생성 해석 리포트 저장"""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    report_id = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    leadership_type = Column(String(50), nullable=False)
    interpretation = Column(Text, nullable=False)
    assessment_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Report(report_id='{self.report_id}', user_id='{self.user_id}')>"


class Conversation(Base):
    """대화 테이블 - Q&A 대화 로그 저장"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(String(50), unique=True, nullable=False, index=True)
    report_id = Column(String(50), nullable=False, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Conversation(conversation_id='{self.conversation_id}', role='{self.role}')>"


class VectorDocument(Base):
    """벡터 문서 메타데이터 테이블 - ChromaDB 문서 추적"""
    __tablename__ = "vector_documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(String(100), unique=True, nullable=False, index=True)
    leadership_type = Column(String(50), nullable=True, index=True)
    content = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True)
    embedding_model = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<VectorDocument(document_id='{self.document_id}')>"


class APILog(Base):
    """API 요청 로그 테이블 - 모니터링 및 분석용"""
    __tablename__ = "api_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(100), nullable=True, index=True)
    endpoint = Column(String(200), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<APILog(endpoint='{self.endpoint}', status={self.status_code})>"
