"""
RAG 엔진 (단순화된 MVP 버전)
"""
from app.services.llm_service import llm_service

def build_prompt(question: str) -> str:
    # MVP에서는 가장 기본적인 프롬프트만 사용
    return f"""당신은 친절한 AI 어시스턴트입니다. 다음 질문에 간결하게 답변해주세요.

질문: {question}
답변:"""

class RAGEngine:
    async def generate_answer_non_streaming(self, question: str) -> str:
        prompt = build_prompt(question)
        response = await llm_service.generate_text(prompt)
        return response

rag_engine = RAGEngine()