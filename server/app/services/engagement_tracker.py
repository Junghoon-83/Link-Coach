"""
사용자 참여도(Engagement) 추적 및 전문 상담사 연결 판단
"""
from typing import List, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)


class EngagementTracker:
    """사용자 참여도 추적 - 정교화된 분석"""

    # 감정적 투자를 나타내는 키워드 (심화)
    EMOTIONAL_KEYWORDS = {
        "high": ["힘들", "막막", "답답", "불안", "혼란", "스트레스", "갈등", "고통"],
        "medium": ["고민", "어려움", "어렵", "걱정", "문제", "부담"],
        "low": ["어떻게", "모르겠", "잘 안", "안 될 때", "조언", "어색"]
    }

    # 실행 의지를 나타내는 키워드 (심화)
    ACTION_KEYWORDS = {
        "high": ["실행", "실천", "시작", "바로", "당장", "오늘", "내일"],
        "medium": ["해보고 싶", "시도해보", "적용해보", "바꿔보", "해야"],
        "low": ["개선", "발전", "성장", "변화", "계획", "준비", "하면"]
    }

    # 심화 주제 키워드 (전문성)
    ADVANCED_KEYWORDS = {
        "high": ["조직 개편", "전략 수립", "비전 설정", "문화 혁신", "성과 체계"],
        "medium": ["팀 갈등", "조직 문화", "성과 관리", "성과 평가", "리더십 개발", "소통", "면담"],
        "low": ["경력", "커리어", "승진", "전략", "비전", "목표", "코칭", "멘토링", "1:1", "팀원", "팀", "업무", "지시"]
    }

    # 대화 질을 나타내는 패턴
    QUALITY_PATTERNS = [
        r"예를 들어",  # 구체화
        r"왜냐하면",    # 설명
        r"사실은",      # 심층
        r"\d+명",       # 구체적 숫자
        r"\d+년",       # 시간 맥락
        r"처음에는.*지금은",  # 변화 인식
    ]

    def __init__(self):
        self.engagement_scores = {}

    def analyze_engagement(
        self,
        user_id: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        대화 기록을 분석하여 참여도 점수 계산

        Args:
            user_id: 사용자 ID
            conversation_history: 대화 히스토리

        Returns:
            dict: 참여도 분석 결과
                - total_score: 총점 (0-100)
                - conversation_depth: 대화 깊이 점수
                - emotional_investment: 감정적 투자 점수
                - action_intent: 실행 의지 점수
                - advanced_topics: 심화 주제 점수
                - should_suggest_consultation: 전문 상담사 제안 여부
        """
        if not conversation_history:
            return self._default_result()

        # 사용자 메시지만 추출
        user_messages = [
            msg['content'] for msg in conversation_history
            if msg.get('role') == 'user'
        ]

        if len(user_messages) < 2:
            return self._default_result()

        # 1. 대화 깊이 점수 (0-30점)
        conversation_depth_score = self._calculate_conversation_depth(user_messages)

        # 2. 감정적 투자 점수 (0-25점)
        emotional_score = self._calculate_emotional_investment(user_messages)

        # 3. 실행 의지 점수 (0-25점)
        action_score = self._calculate_action_intent(user_messages)

        # 4. 심화 주제 점수 (0-20점)
        advanced_score = self._calculate_advanced_topics(user_messages)

        # 총점 계산
        total_score = (
            conversation_depth_score +
            emotional_score +
            action_score +
            advanced_score
        )

        # 전문 상담사 제안 여부 (40점 이상)
        should_suggest = total_score >= 40

        result = {
            "total_score": total_score,
            "conversation_depth": conversation_depth_score,
            "emotional_investment": emotional_score,
            "action_intent": action_score,
            "advanced_topics": advanced_score,
            "should_suggest_consultation": should_suggest
        }

        logger.info(f"User {user_id} engagement score: {total_score}/100 (suggest: {should_suggest})")

        return result

    def _calculate_conversation_depth(self, user_messages: List[str]) -> int:
        """대화 깊이 점수 계산 (0-30점)"""
        message_count = len(user_messages)

        # 메시지 수에 따른 점수
        if message_count >= 5:
            count_score = 15
        elif message_count >= 4:
            count_score = 12
        elif message_count >= 3:
            count_score = 8
        else:
            count_score = 4

        # 평균 메시지 길이에 따른 점수
        avg_length = sum(len(msg) for msg in user_messages) / len(user_messages)
        if avg_length >= 100:
            length_score = 15
        elif avg_length >= 50:
            length_score = 10
        elif avg_length >= 30:
            length_score = 5
        else:
            length_score = 2

        return count_score + length_score

    def _calculate_emotional_investment(self, user_messages: List[str]) -> int:
        """감정적 투자 점수 계산 (0-25점) - 가중치 적용"""
        combined_text = " ".join(user_messages)

        score = 0
        # high 키워드: 10점씩
        for keyword in self.EMOTIONAL_KEYWORDS["high"]:
            if keyword in combined_text:
                score += 10

        # medium 키워드: 5점씩
        for keyword in self.EMOTIONAL_KEYWORDS["medium"]:
            if keyword in combined_text:
                score += 5

        # low 키워드: 2점씩
        for keyword in self.EMOTIONAL_KEYWORDS["low"]:
            if keyword in combined_text:
                score += 2

        return min(score, 25)  # 최대 25점

    def _calculate_action_intent(self, user_messages: List[str]) -> int:
        """실행 의지 점수 계산 (0-25점) - 가중치 적용"""
        combined_text = " ".join(user_messages)

        score = 0
        # high 키워드: 10점씩
        for keyword in self.ACTION_KEYWORDS["high"]:
            if keyword in combined_text:
                score += 10

        # medium 키워드: 5점씩
        for keyword in self.ACTION_KEYWORDS["medium"]:
            if keyword in combined_text:
                score += 5

        # low 키워드: 2점씩
        for keyword in self.ACTION_KEYWORDS["low"]:
            if keyword in combined_text:
                score += 2

        return min(score, 25)  # 최대 25점

    def _calculate_advanced_topics(self, user_messages: List[str]) -> int:
        """심화 주제 점수 계산 (0-20점) - 가중치 적용"""
        combined_text = " ".join(user_messages)

        score = 0
        # high 키워드: 15점씩
        for keyword in self.ADVANCED_KEYWORDS["high"]:
            if keyword in combined_text:
                score += 15

        # medium 키워드: 8점씩
        for keyword in self.ADVANCED_KEYWORDS["medium"]:
            if keyword in combined_text:
                score += 8

        # low 키워드: 3점씩
        for keyword in self.ADVANCED_KEYWORDS["low"]:
            if keyword in combined_text:
                score += 3

        # 대화 질 패턴 보너스 (각 5점)
        for pattern in self.QUALITY_PATTERNS:
            if re.search(pattern, combined_text):
                score += 5

        return min(score, 20)  # 최대 20점

    def _default_result(self) -> Dict[str, Any]:
        """기본 결과 반환"""
        return {
            "total_score": 0,
            "conversation_depth": 0,
            "emotional_investment": 0,
            "action_intent": 0,
            "advanced_topics": 0,
            "should_suggest_consultation": False
        }


# 싱글톤 인스턴스
engagement_tracker = EngagementTracker()
