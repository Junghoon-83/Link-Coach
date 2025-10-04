"""
Pydantic 스키마 정의
API 요청/응답 데이터 모델
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== 리더십 유형 ====================

class LeadershipType(str, Enum):
    """리더십 유형 (3차원 기반 8가지 유형)"""
    PARTICIPATIVE_COACHING = "참여코칭형"
    PARTICIPATIVE_TASK = "참여실무형"
    PARTICIPATIVE_VISION = "참여비전형"
    PARTICIPATIVE_RELATIONAL = "참여친밀형"
    INDIVIDUAL_COACHING = "개별코칭형"
    INDIVIDUAL_VISION = "개별비전형"
    INDIVIDUAL_RELATIONAL = "개별친밀형"
    TRANSITIONAL = "과도기형"


# ==================== 해석 리포트 관련 ====================

class InterpretationRequest(BaseModel):
    """AI 심층 해석 리포트 요청"""
    user_id: str = Field(..., description="사용자 ID", example="user_12345")
    leadership_type: str = Field(..., description="리더십 유형", example="개별비전형")
    assessment_data: Optional[Dict[str, Any]] = Field(
        None,
        description="진단 원본 데이터 (선택사항)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_12345",
                "leadership_type": "개별비전형",
                "assessment_data": {
                    "scores": {
                        "공유및참여": 3.5,
                        "상호작용": 3.8,
                        "성장지향": 4.8
                    }
                }
            }
        }


class InterpretationResponse(BaseModel):
    """AI 심층 해석 리포트 응답"""
    report_id: str = Field(..., description="리포트 고유 ID")
    user_id: str = Field(..., description="사용자 ID")
    leadership_type: str = Field(..., description="리더십 유형")
    interpretation: str = Field(..., description="AI 생성 해석 텍스트")
    created_at: str = Field(..., description="생성 시간 (ISO 8601)")

    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "rpt_abc123",
                "user_id": "user_12345",
                "leadership_type": "개별비전형",
                "interpretation": "당신의 개별비전형 리더십은...",
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


# ==================== Q&A 관련 ====================

class ConversationMessage(BaseModel):
    """대화 메시지"""
    role: str = Field(..., description="메시지 역할 (user/assistant)", example="user")
    content: str = Field(..., description="메시지 내용", example="이 유형의 강점은 무엇인가요?")
    timestamp: Optional[str] = Field(None, description="메시지 시간")


class QueryRequest(BaseModel):
    """Q&A 질문 요청"""
    user_id: str = Field(..., description="사용자 ID", example="user_12345")
    report_id: str = Field(..., description="참조할 리포트 ID", example="rpt_abc123")
    question: str = Field(
        ...,
        description="사용자 질문",
        max_length=500,
        example="이 리더십 유형의 강점은 무엇인가요?"
    )
    conversation_history: Optional[List[ConversationMessage]] = Field(
        None,
        description="대화 히스토리 (최근 5개 권장)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_12345",
                "report_id": "rpt_abc123",
                "question": "이 리더십 유형의 강점은 무엇인가요?",
                "conversation_history": [
                    {
                        "role": "user",
                        "content": "제 유형에 대해 알려주세요"
                    },
                    {
                        "role": "assistant",
                        "content": "개별비전형 리더십은..."
                    }
                ]
            }
        }


class QueryResponse(BaseModel):
    """Q&A 응답 (스트리밍이 아닌 경우)"""
    answer: str = Field(..., description="AI 생성 답변")
    sources: Optional[List[str]] = Field(
        None,
        description="참조된 소스 문서 ID"
    )


# ==================== RAG 관련 ====================

class RAGDocument(BaseModel):
    """RAG 검색 결과 문서"""
    document_id: str = Field(..., description="문서 ID")
    content: str = Field(..., description="문서 내용")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="문서 메타데이터")
    similarity_score: float = Field(..., description="유사도 점수", ge=0, le=1)


class RAGSearchResult(BaseModel):
    """RAG 검색 결과"""
    query: str = Field(..., description="검색 쿼리")
    documents: List[RAGDocument] = Field(..., description="검색된 문서 목록")
    total_results: int = Field(..., description="전체 결과 수")


# ==================== 에러 응답 ====================

class ErrorResponse(BaseModel):
    """에러 응답"""
    detail: str = Field(..., description="에러 상세 메시지")
    error_code: Optional[str] = Field(None, description="에러 코드")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Report not found",
                "error_code": "REPORT_NOT_FOUND",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


# ==================== 헬스체크 ====================

class HealthCheckResponse(BaseModel):
    """헬스체크 응답"""
    status: str = Field(..., description="서비스 상태", example="healthy")
    service: str = Field(..., description="서비스 이름")
    version: str = Field(..., description="서비스 버전")
    environment: str = Field(..., description="실행 환경")
