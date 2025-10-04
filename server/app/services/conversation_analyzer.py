"""
대화 분석 및 오프토픽 감지 서비스
사용자 질문의 의도, 감정, 단계를 분석하고 오프토픽 여부를 판단
"""
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ConversationStage(int, Enum):
    """대화 단계"""
    GREETING = 1  # 인사/초기 접근
    EXPLORATION = 2  # 탐색/정보수집
    DEEP_COACHING = 3  # 심층 코칭
    ACTION_PLAN = 4  # 실행계획


class OffTopicCategory(str, Enum):
    """오프토픽 카테고리"""
    WEATHER = "날씨"
    FOOD = "음식"
    TECH = "기술"
    MEDICAL = "의료"
    LEGAL = "법률"
    META = "메타"
    DAILY = "일상"
    NONSENSE = "난센스"
    NONE = "없음"


class ConversationAnalyzer:
    """대화 분석기"""

    def __init__(self):
        # 리더십 관련 키워드
        self.leadership_keywords = [
            '팀', '리더', '직원', '부하', '상사', '회의', '업무', '프로젝트',
            '성과', '목표', '관리', '소통', '커뮤니케이션', '의사결정',
            '갈등', '동기부여', '코칭', '피드백', '1on1', '조직', '해고', '이직'
        ]

        # 오프토픽 키워드
        self.offtopic_keywords = {
            OffTopicCategory.WEATHER: ['날씨', '비', '눈', '맑', '흐림', '온도', '더워', '추워'],
            OffTopicCategory.FOOD: ['점심', '저녁', '아침', '먹을', '맛집', '음식', '메뉴'],
            OffTopicCategory.TECH: ['컴퓨터', '프로그램', '버그', '설치', '고장', '인터넷', '와이파이'],
            OffTopicCategory.MEDICAL: ['병원', '약', '의사', '진료', '우울증', '치료', '증상', '아파'],
            OffTopicCategory.LEGAL: ['법', '소송', '계약서', '변호사', '법적', '문제 없나', '문제없나', '법률'],
            OffTopicCategory.META: ['서비스', 'ai', '인공지능', '유료', '가격', '요금', '개인정보', '뭐하는', '뭐 하는'],
            OffTopicCategory.DAILY: ['취미', '주식', '재테크', '운동', '영화', '드라마'],
            OffTopicCategory.NONSENSE: ['1+1', 'asdf', 'how are you', '??']
        }

        # 인사말 패턴
        self.greeting_patterns = ['안녕', '하이', '헬로', '반갑']

        # 감정 표현 키워드
        self.emotion_keywords = {
            'frustrated': ['답답', '힘들', '어렵', '막막', '모르겠', '지치', '지쳐', '화나', '불안', '두렵', '걱정', '포기'],
            'resistant': ['이미', '해봤', '안 됐', '안 돼', '소용없', '안 될', '그런데', '하지만', '어차피'],
            'positive': ['효과', '좋았', '도움', '감사', '성공', '잘 됐', '해결'],
            'urgent': ['당장', '급하', '내일', '오늘', '지금 바로']
        }

    def analyze(
        self,
        question: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        질문 종합 분석

        Args:
            question: 사용자 질문
            conversation_history: 대화 히스토리

        Returns:
            dict: 분석 결과
                - stage: 대화 단계
                - is_offtopic: 오프토픽 여부
                - offtopic_category: 오프토픽 카테고리
                - traits: 질문 특성 목록
                - emotion: 감정 상태
                - requires_context: 컨텍스트 필요 여부
        """
        question_lower = question.lower()

        # 1. 대화 단계 계산
        stage = self._calculate_stage(conversation_history)

        # 2. 오프토픽 감지
        is_offtopic, offtopic_category = self._detect_offtopic(question, question_lower)

        # 3. 질문 특성 분석
        traits = self._analyze_traits(question, question_lower)

        # 4. 감정 상태 분석
        emotion = self._analyze_emotion(question_lower)

        # 5. 단계 조정 (감정, 긴급성 등에 따라)
        stage = self._adjust_stage(stage, traits, emotion)

        # 6. 컨텍스트 필요 여부
        requires_context = self._check_context_requirement(traits, stage)

        result = {
            "stage": stage,
            "is_offtopic": is_offtopic,
            "offtopic_category": offtopic_category.value if offtopic_category else None,
            "traits": traits,
            "emotion": emotion,
            "requires_context": requires_context,
            "question_length": len(question)
        }

        logger.info(f"대화 분석 완료: {result}")
        return result

    def _calculate_stage(self, conversation_history: Optional[List[Dict]]) -> ConversationStage:
        """대화 단계 계산"""
        if not conversation_history:
            return ConversationStage.GREETING

        # 대화 턴 수로 단계 추정 (2턴당 1단계 증가)
        turns = len(conversation_history)
        stage_num = min(turns // 2 + 1, 4)
        return ConversationStage(stage_num)

    def _detect_offtopic(self, question: str, question_lower: str) -> Tuple[bool, Optional[OffTopicCategory]]:
        """오프토픽 감지"""
        # 1. 한글 비율 체크 (외국어/난센스)
        korean_chars = sum(1 for c in question if '가' <= c <= '힣')
        if korean_chars < len(question) * 0.3 and len(question) > 3:
            return True, OffTopicCategory.NONSENSE

        # 2. 리더십 컨텍스트 확인
        has_leadership_context = any(
            keyword in question_lower for keyword in self.leadership_keywords
        )

        # 3. 오프토픽 키워드 매칭
        if not has_leadership_context:
            for category, keywords in self.offtopic_keywords.items():
                if any(keyword in question_lower for keyword in keywords):
                    return True, category

        return False, None

    def _analyze_traits(self, question: str, question_lower: str) -> List[str]:
        """질문 특성 분석"""
        traits = []

        # 인사말
        if any(word in question_lower for word in self.greeting_patterns):
            traits.append("인사")

        if '좋은' in question_lower and any(
            time in question_lower for time in ['아침', '저녁', '오후', '하루', '주말']
        ):
            traits.append("인사")

        # 구체적 요청
        is_wellbeing = any(
            phrase in question_lower for phrase in ['지내', '어때', '괜찮', '잘 있', '건강', '안녕']
        )

        if any([
            '어떻게' in question_lower,
            '어떡' in question_lower,
            '방법' in question_lower,
            '뭐' in question_lower,
            '무엇' in question_lower,
            '?' in question,
            (question.endswith('죠') and not is_wellbeing),
            (question.endswith('나요') and not is_wellbeing),
            (question.endswith('을까요') and not is_wellbeing),
            (question.endswith('요') and len(question) > 10 and '인사' not in traits),
            question.endswith('요.'),
            question.endswith('어요')
        ]):
            traits.append("구체적요청")

        # 복잡도
        has_multiple_subjects = sum(1 for char in question if char in ['A', 'B', 'C', '그', '또']) >= 2
        if len(question) > 50 or has_multiple_subjects:
            traits.append("복잡한상황")

        return traits if traits else ["일반질문"]

    def _analyze_emotion(self, question_lower: str) -> Dict[str, bool]:
        """감정 상태 분석"""
        emotions = {}

        for emotion_type, keywords in self.emotion_keywords.items():
            emotions[emotion_type] = any(keyword in question_lower for keyword in keywords)

        return emotions

    def _adjust_stage(
        self,
        stage: ConversationStage,
        traits: List[str],
        emotion: Dict[str, bool]
    ) -> ConversationStage:
        """단계 조정"""
        # 인사말은 항상 GREETING (대화 히스토리가 없을 때)
        if "인사" in traits and stage == ConversationStage.GREETING:
            return ConversationStage.GREETING

        # 긴급성/저항 → DEEP_COACHING
        if emotion.get('urgent') or emotion.get('resistant'):
            return ConversationStage(max(stage, ConversationStage.DEEP_COACHING))

        # 좌절감 강함 → DEEP_COACHING
        if emotion.get('frustrated'):
            if '모르겠' in traits or '포기' in traits:
                return ConversationStage(max(stage, ConversationStage.DEEP_COACHING))
            return ConversationStage(max(stage, ConversationStage.EXPLORATION))

        # 구체적 요청 + 복잡함 → DEEP_COACHING
        if "구체적요청" in traits and ("복잡한상황" in traits or stage >= ConversationStage.DEEP_COACHING):
            return ConversationStage(max(stage, ConversationStage.DEEP_COACHING))

        # 구체적 요청 + 대화 진행 중 → EXPLORATION 이상
        if "구체적요청" in traits and stage >= ConversationStage.EXPLORATION:
            return ConversationStage(max(stage, ConversationStage.EXPLORATION))

        # 구체적 요청만 있고 히스토리 없음 → GREETING 유지 (warm_welcome)
        if "구체적요청" in traits and stage == ConversationStage.GREETING:
            return ConversationStage.GREETING

        return stage

    def _check_context_requirement(self, traits: List[str], stage: ConversationStage) -> bool:
        """컨텍스트 필요 여부 확인"""
        # 인사말은 컨텍스트 불필요
        if "인사" in traits:
            return False

        # EXPLORATION 이상은 컨텍스트 필요
        if stage >= ConversationStage.EXPLORATION:
            return True

        # 구체적 요청은 컨텍스트 필요
        if "구체적요청" in traits:
            return True

        return False

    def get_response_strategy(self, analysis: Dict) -> str:
        """
        분석 결과에 따른 응답 전략 반환

        Args:
            analysis: analyze() 결과

        Returns:
            str: 응답 전략 키워드
        """
        # 오프토픽 처리
        if analysis["is_offtopic"]:
            category = analysis["offtopic_category"]

            if category in ["의료", "법률"]:
                return "redirect_to_expert"
            elif category == "메타":
                return "service_info"
            elif category == "난센스":
                return "clarify_question"
            else:
                return "gentle_redirect"

        # 단계별 전략
        stage = analysis["stage"]
        emotion = analysis["emotion"]
        traits = analysis["traits"]

        if stage == ConversationStage.GREETING:
            # 인사만 있으면 warm_welcome
            if "인사" in traits:
                return "warm_welcome"
            # 구체적 요청이 있으면 open_exploration으로 시작
            if "구체적요청" in traits:
                return "open_exploration"
            return "warm_welcome"
        elif stage == ConversationStage.EXPLORATION:
            if emotion.get("frustrated"):
                return "empathetic_exploration"
            return "open_exploration"
        elif stage == ConversationStage.DEEP_COACHING:
            if emotion.get("resistant"):
                return "gentle_challenge"
            elif emotion.get("urgent"):
                return "immediate_action"
            return "deep_insight"
        else:  # ACTION_PLAN
            return "action_oriented"


# 싱글톤 인스턴스
conversation_analyzer = ConversationAnalyzer()
