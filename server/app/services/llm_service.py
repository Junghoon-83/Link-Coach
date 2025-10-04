"""
LLM 서비스 - Gemini API 통합
"""
import logging
from typing import AsyncGenerator, Optional, Union, List, Dict
import google.generativeai as genai

from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    Google Gemini API를 활용한 LLM 서비스
    """

    def __init__(self):
        """
        Gemini API 클라이언트 초기화
        """
        self.model = None
        self.is_initialized = False

    async def initialize(self):
        """
        Gemini API 초기화 (lazy loading)
        """
        if self.is_initialized:
            return

        try:
            logger.info("Gemini API 초기화 중...")

            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")

            # API 키 설정
            genai.configure(api_key=settings.GEMINI_API_KEY)

            # Safety settings - 코칭 대화가 안전 필터에 걸리지 않도록 설정
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE",
                },
            ]

            # 모델 초기화
            self.model = genai.GenerativeModel(
                model_name=settings.GEMINI_MODEL,
                generation_config={
                    "temperature": settings.GEMINI_TEMPERATURE,
                    "max_output_tokens": settings.GEMINI_MAX_TOKENS,
                },
                safety_settings=safety_settings
            )

            self.is_initialized = True
            logger.info("✅ Gemini API 초기화 완료")

        except Exception as e:
            logger.error(f"Gemini API 초기화 실패: {e}")
            raise

    async def generate_text(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        텍스트 생성 (Non-streaming)

        Args:
            prompt: 프롬프트
            temperature: 온도 (기본값: settings.GEMINI_TEMPERATURE)
            max_tokens: 최대 토큰 수 (기본값: settings.GEMINI_MAX_TOKENS)

        Returns:
            생성된 텍스트
        """
        await self.initialize()

        try:
            logger.info(f"텍스트 생성 요청 (길이: {len(prompt)} chars)")

            # 설정 생성
            generation_config = {
                "temperature": temperature or settings.GEMINI_TEMPERATURE,
                "max_output_tokens": max_tokens or settings.GEMINI_MAX_TOKENS,
            }

            # 텍스트 생성
            response = await self.model.generate_content_async(
                prompt,
                generation_config=generation_config
            )

            result = response.text
            logger.info(f"텍스트 생성 완료 (길이: {len(result)} chars)")
            return result

        except Exception as e:
            logger.error(f"텍스트 생성 실패: {e}")
            raise

    async def generate_from_messages(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        메시지 리스트 기반 텍스트 생성 (역할 기반 대화)

        Args:
            messages: 메시지 리스트 [{"role": "system/user/assistant", "content": "..."}]
            temperature: 온도
            max_tokens: 최대 토큰 수

        Returns:
            생성된 텍스트
        """
        await self.initialize()

        try:
            logger.info(f"메시지 기반 텍스트 생성 요청 (메시지 수: {len(messages)})")

            # Gemini API는 system role을 직접 지원하지 않으므로 변환
            # system 메시지를 첫 user 메시지에 포함
            converted_messages = []
            system_content = ""

            for msg in messages:
                if msg["role"] == "system":
                    system_content = msg["content"]
                elif msg["role"] == "user":
                    # system content가 있으면 첫 user 메시지에 포함
                    if system_content:
                        content = f"{system_content}\n\n{msg['content']}"
                        system_content = ""  # 한 번만 포함
                    else:
                        content = msg["content"]
                    converted_messages.append({"role": "user", "parts": [content]})
                elif msg["role"] == "assistant":
                    converted_messages.append({"role": "model", "parts": [msg["content"]]})

            # 설정 생성
            generation_config = {
                "temperature": temperature or settings.GEMINI_TEMPERATURE,
                "max_output_tokens": max_tokens or settings.GEMINI_MAX_TOKENS,
            }

            # 텍스트 생성
            response = await self.model.generate_content_async(
                converted_messages,
                generation_config=generation_config
            )

            result = response.text
            logger.info(f"메시지 기반 텍스트 생성 완료 (길이: {len(result)} chars)")
            return result

        except Exception as e:
            logger.error(f"메시지 기반 텍스트 생성 실패: {e}")
            raise

    async def generate_text_streaming(
        self,
        prompt: Union[str, dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """
        스트리밍 텍스트 생성

        Args:
            prompt: 프롬프트 (문자열 또는 딕셔너리)
            temperature: 온도 (기본값: settings.GEMINI_TEMPERATURE)
            max_tokens: 최대 토큰 수 (기본값: settings.GEMINI_MAX_TOKENS)

        Yields:
            텍스트 청크 (델타)
        """
        await self.initialize()

        try:
            # 프롬프트 타입 확인
            if isinstance(prompt, dict):
                # 딕셔너리인 경우: 구조화된 프롬프트
                full_prompt = prompt.get("text", "") or prompt.get("content", "")
                logger.info(f"스트리밍 텍스트 생성 요청 (딕셔너리, 길이: {len(str(full_prompt))} chars)")
            else:
                # 문자열인 경우
                full_prompt = prompt
                logger.info(f"스트리밍 텍스트 생성 요청 (문자열, 길이: {len(full_prompt)} chars)")

            # 설정 생성
            generation_config = genai.types.GenerationConfig(
                temperature=temperature or settings.GEMINI_TEMPERATURE,
                max_output_tokens=max_tokens or settings.GEMINI_MAX_TOKENS,
            )

            # 스트리밍 응답 생성
            response = await self.model.generate_content_async(
                full_prompt,
                stream=True,
                generation_config=generation_config
            )

            # 델타 추출을 위한 변수
            total_length = 0
            chunk_count = 0
            full_response = ""

            # 청크 단위로 전송
            async for chunk in response:
                try:
                    # 1. 텍스트 속성 확인
                    if hasattr(chunk, 'text') and chunk.text:
                        # Gemini는 누적 텍스트를 반환하므로 델타만 추출
                        current_text = chunk.text
                        full_response = current_text  # 전체 텍스트 저장

                        if len(current_text) > total_length:
                            delta = current_text[total_length:]
                            total_length = len(current_text)
                            chunk_count += 1
                            logger.debug(f"청크 {chunk_count}: delta={repr(delta[:50])}... (길이: {len(delta)})")
                            yield delta

                    # 2. parts 속성 확인 (백업)
                    elif hasattr(chunk, 'parts'):
                        for part in chunk.parts:
                            if hasattr(part, 'text') and part.text:
                                yield part.text
                                chunk_count += 1

                except Exception as e:
                    logger.warning(f"청크 처리 중 오류 (무시): {e}")
                    continue

            logger.info(f"스트리밍 텍스트 생성 완료 (청크: {chunk_count}, 총 길이: {total_length})")
            logger.info(f"Gemini 전체 응답: {repr(full_response)}")

        except Exception as e:
            logger.error(f"스트리밍 텍스트 생성 실패: {e}", exc_info=True)
            raise


# 싱글톤 인스턴스
llm_service = LLMService()
