"""
코칭 API 엔드포인트
"""
import logging
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.core.security import verify_jwt_token
from app.services.ai_service import ai_service
from app.models.conversation import ConversationMessage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/coaching", tags=["Coaching"])


# ==================== Request/Response Models ====================

class InterpretationRequest(BaseModel):
    """AI 심층 해석 리포트 생성 요청"""
    user_id: str = Field(..., description="사용자 ID")
    leadership_type: str = Field(..., description="리더십 유형")
    assessment_data: Optional[dict] = Field(None, description="진단 원본 데이터")


class InterpretationResponse(BaseModel):
    """AI 심층 해석 리포트 응답"""
    report_id: str = Field(..., description="리포트 ID")
    interpretation: str = Field(..., description="AI 생성 해석 내용")


class QueryRequest(BaseModel):
    """맥락 기반 Q&A 요청"""
    user_id: str = Field(..., description="사용자 ID")
    report_id: str = Field(..., description="리포트 ID")
    question: str = Field(..., max_length=500, description="질문 내용")
    conversation_history: Optional[List[dict]] = Field(None, description="대화 히스토리")


class QueryResponse(BaseModel):
    """맥락 기반 Q&A 응답 (Non-streaming)"""
    answer: str = Field(..., description="AI 생성 답변")


# ==================== Endpoints ====================

@router.post("/interpretation", response_model=InterpretationResponse)
async def generate_interpretation(
    request: InterpretationRequest,
    token_data: dict = Depends(verify_jwt_token)
):
    """
    AI 심층 해석 리포트 생성

    사용자의 리더십 유형과 진단 데이터를 기반으로 AI 심층 해석 리포트를 생성합니다.
    """
    try:
        logger.info(f"리포트 생성 요청: user_id={request.user_id}, type={request.leadership_type}")

        # 리포트 생성
        report = await ai_service.generate_interpretation(
            user_id=request.user_id,
            leadership_type=request.leadership_type,
            assessment_data=request.assessment_data
        )

        return InterpretationResponse(
            report_id=report["report_id"],
            interpretation=report["interpretation"]
        )

    except Exception as e:
        logger.error(f"리포트 생성 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"리포트 생성 중 오류가 발생했습니다: {str(e)}")


@router.post("/query")
async def query_with_streaming(
    request: QueryRequest,
    token_data: dict = Depends(verify_jwt_token)
):
    """
    맥락 기반 Q&A (스트리밍)

    리포트 내용을 기반으로 사용자의 질문에 대해 스트리밍 방식으로 답변합니다.
    """
    try:
        logger.info(f"Q&A 요청: user_id={request.user_id}, report_id={request.report_id}")

        # 대화 히스토리를 ConversationMessage 리스트로 변환
        conversation_history = None
        if request.conversation_history:
            conversation_history = [
                ConversationMessage(**msg) if isinstance(msg, dict) else msg
                for msg in request.conversation_history
            ]

        # 스트리밍 응답 생성
        async def generate():
            try:
                async for chunk in ai_service.generate_answer_streaming(
                    user_id=request.user_id,
                    report_id=request.report_id,
                    question=request.question,
                    conversation_history=conversation_history
                ):
                    # SSE 형식으로 전송
                    yield f"data: {chunk}\n\n"

                # 완료 신호
                yield "data: [DONE]\n\n"

            except Exception as e:
                logger.error(f"스트리밍 중 오류: {e}", exc_info=True)
                error_message = f"답변 생성 중 오류가 발생했습니다: {str(e)}"
                yield f'data: {{"error": "{error_message}"}}\n\n'

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Nginx 버퍼링 비활성화
            }
        )

    except Exception as e:
        logger.error(f"Q&A 요청 처리 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Q&A 처리 중 오류가 발생했습니다: {str(e)}")


@router.post("/query-non-streaming", response_model=QueryResponse)
async def query_non_streaming(
    request: QueryRequest,
    token_data: dict = Depends(verify_jwt_token)
):
    """
    맥락 기반 Q&A (Non-streaming)

    리포트 내용을 기반으로 사용자의 질문에 대해 한 번에 답변합니다.
    """
    try:
        logger.info(f"Q&A 요청 (Non-streaming): user_id={request.user_id}, report_id={request.report_id}")

        # 대화 히스토리를 ConversationMessage 리스트로 변환
        conversation_history = None
        if request.conversation_history:
            conversation_history = [
                ConversationMessage(**msg) if isinstance(msg, dict) else msg
                for msg in request.conversation_history
            ]

        # 답변 생성
        answer = await ai_service.query_non_streaming(
            user_id=request.user_id,
            report_id=request.report_id,
            question=request.question,
            conversation_history=conversation_history
        )

        return QueryResponse(answer=answer)

    except Exception as e:
        logger.error(f"Q&A 처리 실패: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Q&A 처리 중 오류가 발생했습니다: {str(e)}")
