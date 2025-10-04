"""
대화 모델
"""
from pydantic import BaseModel, Field
from typing import Literal


class ConversationMessage(BaseModel):
    """대화 메시지"""
    role: Literal["user", "assistant"] = Field(..., description="메시지 역할")
    content: str = Field(..., description="메시지 내용")
