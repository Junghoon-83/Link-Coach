"""
AI 서비스 통합 레이어
ML 모델, RAG 엔진, LLM을 통합하여 고수준 API 제공
"""
from typing import Dict, Any, Optional, AsyncGenerator, List
from datetime import datetime
import uuid
import logging

from app.services.ml_model import ml_model_service
from app.services.rag_engine import rag_engine
from app.services.llm_service import llm_service
from app.services.prompt_templates import get_context_string, build_final_prompt
from app.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """AI 서비스 통합"""

    def __init__(self):
        self.ml_model = ml_model_service
        self.rag = rag_engine
        self.llm = llm_service
        # TODO: PostgreSQL 캐시 구현 시 연결
        self.cache: Dict[str, Dict] = {}  # 임시 메모리 캐시

    async def initialize(self) -> None:
        """모든 AI 서비스 초기화"""
        logger.info("AI 서비스 초기화 중...")

        try:
            # ML 모델 로드
            await self.ml_model.load_model()

            # Vector DB 연결
            await self.rag.vector_db.connect()

            # LLM 초기화
            await self.llm.initialize()

            logger.info("✅ AI 서비스 초기화 완료")

        except Exception as e:
            logger.error(f"AI 서비스 초기화 실패: {e}", exc_info=True)
            raise

    async def generate_interpretation(
        self,
        user_id: str,
        leadership_type: str,
        assessment_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        AI 심층 해석 리포트 생성

        Args:
            user_id: 사용자 ID
            leadership_type: 리더십 유형
            assessment_data: 진단 원본 데이터

        Returns:
            dict: 생성된 리포트
                - report_id: 리포트 ID
                - user_id: 사용자 ID
                - leadership_type: 리더십 유형
                - interpretation: 해석 텍스트
                - created_at: 생성 시간
        """
        try:
            logger.info(f"해석 리포트 생성: user={user_id}, type={leadership_type}")

            # 개발 모드에서 더미 데이터 사용
            if settings.USE_MOCK_DATA:
                report_id = f"rpt_{uuid.uuid4().hex[:12]}"
                mock_report = {
                    "report_id": report_id,
                    "user_id": user_id,
                    "leadership_type": leadership_type,
                    "interpretation": f"""# {leadership_type} 리더십 분석 리포트

## 주요 특성
당신은 {leadership_type} 리더십 스타일을 가지고 계십니다. 이는 조직 내에서 독특한 강점을 발휘할 수 있는 유형입니다.

## 강점
- 명확한 비전 제시 능력
- 팀원들과의 원활한 소통
- 변화에 대한 적응력

## 개발 영역
- 위임 능력 향상
- 갈등 관리 기술 개발
- 데이터 기반 의사결정 강화

## 실천 제안
1. 매주 팀과 정기적인 1:1 미팅 진행
2. 분기별 리더십 스타일 자가 점검
3. 멘토링 프로그램 참여

이 리포트는 개발 모드 더미 데이터입니다.""",
                    "created_at": datetime.now().isoformat()
                }

                # 캐시 저장
                cache_key = f"{user_id}:{report_id}"
                self.cache[cache_key] = mock_report
                logger.info(f"✅ [MOCK] 리포트 생성 완료: {report_id}")

                return mock_report

            # 1. ML 모델로 리더십 유형 검증 (선택적)
            if assessment_data:
                is_valid = await self.ml_model.validate_leadership_type(
                    leadership_type=leadership_type,
                    features=assessment_data
                )
                if not is_valid:
                    logger.warning(f"리더십 유형 검증 실패: {leadership_type}")

            # 2. LLM으로 해석 생성
            prompt = f"""당신은 리더십 전문 코치입니다. 다음 리더십 유형에 대한 심층 해석 리포트를 작성하세요.

리더십 유형: {leadership_type}

다음 내용을 포함하여 전문적이고 통찰력 있는 해석을 제공하세요:
1. 이 리더십 유형의 핵심 특징
2. 강점과 성장 가능성
3. 주의해야 할 점
4. 발전 방향 제안

500-800자 내외로 작성하세요."""

            interpretation = await self.llm.generate_text(prompt)

            # 3. 리포트 데이터 구성
            report_id = f"rpt_{uuid.uuid4().hex[:12]}"
            created_at = datetime.utcnow().isoformat() + "Z"

            report = {
                "report_id": report_id,
                "user_id": user_id,
                "leadership_type": leadership_type,
                "interpretation": interpretation,
                "created_at": created_at
            }

            # 4. 캐시 저장
            if settings.CACHE_ENABLED:
                cache_key = f"{user_id}:{report_id}"
                self.cache[cache_key] = report
                logger.info(f"리포트 캐시 저장: {cache_key}")

            logger.info(f"✅ 리포트 생성 완료: {report_id}")
            return report

        except Exception as e:
            logger.error(f"리포트 생성 실패: {e}", exc_info=True)
            raise



    async def query_non_streaming(
        self,
        user_id: str,
        report_id: str,
        question: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        맥락 기반 Q&A (비-스트리밍)
        나중에 스트리밍으로 전환 가능하도록 구조화
        """
        try:
            logger.info(f"Q&A 요청 (Non-Streaming): user={user_id}, report={report_id}, question={question[:50]}...")

            # 1. 리포트 조회
            report = await self.get_cached_report(report_id, user_id)
            if not report:
                logger.error(f"리포트를 찾을 수 없음: {report_id}")
                return "죄송합니다. 리포트를 찾을 수 없습니다."

            leadership_type = report.get("leadership_type")
            interpretation = report.get("interpretation", "")

            # 2. 대화 히스토리 구성 (Pydantic 객체 → dict 변환)
            history_dicts = []
            if conversation_history:
                for msg in conversation_history[-5:]:  # 최근 5개만
                    history_dicts.append({
                        "role": msg.role,
                        "content": msg.content
                    })

            # 3. 시스템 프롬프트 정의
            system_prompt = """당신은 전문 리더십 코치입니다. 사용자의 리더십 리포트를 바탕으로 질문에 답변하세요.

답변 가이드라인:
1. 리포트 내용을 바탕으로 구체적으로 답변하세요
2. 공감하고 격려하는 톤으로 작성하세요
3. 실용적인 조언을 제공하세요
4. 200-400자 내외로 간결하게 답변하세요"""

            # 4. 컨텍스트 문자열 생성 (prompt_templates 활용)
            context_string = get_context_string(
                leadership_type=leadership_type,
                report_context=interpretation
            )

            # 5. 최종 프롬프트 메시지 리스트 생성 (prompt_templates 활용)
            messages = build_final_prompt(
                question=question,
                system_prompt=system_prompt,
                context_string=context_string,
                conversation_history=history_dicts
            )

            # 6. LLM 호출 (메시지 리스트 기반)
            answer = await self.llm.generate_from_messages(messages)

            logger.info(f"✅ Q&A 완료: {len(answer)} chars")
            return answer

        except Exception as e:
            logger.error(f"Q&A 실패 (Non-Streaming): {e}", exc_info=True)
            return "죄송합니다. 답변 생성 중 오류가 발생했습니다. 다시 시도해주세요."

    async def get_cached_report(
        self,
        report_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        캐시된 리포트 조회

        Args:
            report_id: 리포트 ID
            user_id: 사용자 ID

        Returns:
            dict | None: 리포트 데이터
        """
        try:
            # 임시 메모리 캐시에서 조회
            cache_key = f"{user_id}:{report_id}"
            report = self.cache.get(cache_key)

            if report:
                logger.info(f"캐시에서 리포트 조회: {cache_key}")
                return report

            # TODO: PostgreSQL에서 조회
            logger.info(f"리포트를 찾을 수 없음: {report_id}")
            return None

        except Exception as e:
            logger.error(f"리포트 조회 실패: {e}", exc_info=True)
            return None


# 싱글톤 인스턴스
ai_service = AIService()
