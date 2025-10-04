"""
리더십 유형 분류 로직
실제 비즈니스 규칙에 따른 리더십 유형 결정
"""
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


# 리더십 유형 정의
LEADERSHIP_TYPES = {
    "참여코칭형": {
        "conditions": {"공유및참여": 4.5, "상호작용": 4.5, "성장지향": 4.5},
        "operator": "all_gte",
        "description": "공유 및 참여, 상호작용, 성장지향 모두 높음"
    },
    "참여실무형": {
        "conditions": {"공유및참여": 4.5, "상호작용": 4.5, "성장지향": 4.5},
        "operator": "공유및참여_gte_others_lt",
        "description": "공유 및 참여는 높으나, 상호작용과 성장지향이 낮음"
    },
    "참여비전형": {
        "conditions": {"공유및참여": 4.5, "상호작용": 4.5, "성장지향": 4.5},
        "operator": "공유및참여_성장지향_gte_상호작용_lt",
        "description": "공유 및 참여와 성장지향은 높으나, 상호작용이 낮음"
    },
    "참여친밀형": {
        "conditions": {"공유및참여": 4.5, "상호작용": 4.5, "성장지향": 4.5},
        "operator": "공유및참여_상호작용_gte_성장지향_lt",
        "description": "공유 및 참여와 상호작용은 높으나, 성장지향이 낮음"
    },
    "개별코칭형": {
        "conditions": {"공유및참여": 4.5, "상호작용": 4.5, "성장지향": 4.5},
        "operator": "상호작용_성장지향_gte_공유및참여_lt",
        "description": "상호작용과 성장지향은 높으나, 공유 및 참여가 낮음"
    },
    "개별비전형": {
        "conditions": {"공유및참여": 4.5, "상호작용": 4.5, "성장지향": 4.5},
        "operator": "성장지향_gte_others_lt",
        "description": "성장지향만 높고, 공유 및 참여와 상호작용이 낮음",
        "strengths": "미래 비전과 성장에 강점. 새로운 관점으로 프레임을 바꾸지만 산출물 정의가 팀과 어긋나면 재작업 위험",
        "best_situations": ["신사업/전략 기획", "문제 재정의", "혁신 아이디어 도출", "방향 전환이 필요한 초기 단계 검증 시"]
    },
    "개별친밀형": {
        "conditions": {"공유및참여": 4.5, "상호작용": 4.5, "성장지향": 4.5},
        "operator": "상호작용_gte_others_lt",
        "description": "상호작용만 높고, 공유 및 참여와 성장지향이 낮음"
    },
    "과도기형": {
        "conditions": {"공유및참여": 4.5, "상호작용": 4.5, "성장지향": 4.5},
        "operator": "all_lt",
        "description": "공유 및 참여, 상호작용, 성장지향 모두 낮음"
    }
}


# 팔로워십 유형 정의
FOLLOWERSHIP_TYPES = {
    "Driver": {
        "description": "팀원은 리더가 제안한 내용 뿐 아니라 내용을 발전시켜오는 적극적인 업무 참여 태도를 보인다. 문제가 발생할때에는 원인에 대한 분석 뿐만 아니라 해결책을 모색한다.",
        "characteristics": ["적극적 참여", "문제 해결 지향", "발전적 사고"]
    },
    "Thinker": {
        "description": "한가지 일에 대한 몰입이 높은편이고 여러가지 일에 대해 정신 에너지를 전환하는 것을 어려워한다. 새로운 아이디어를 많이 내는 편이지만, 실행을 위한 행동은 느린편이다.",
        "characteristics": ["높은 몰입도", "아이디어 생성", "실행 느림"]
    },
    "Supporter": {
        "description": "리더의 업무 지시에 빠르게 순응하고 업무를 처리한다. 리더를 포함한 팀 구성원의 업무를 지원하는 역할을 편안해한다. 주도적으로 나서서 업무를 진행하는 것에 부담이 있는 편이라, 리더로서 팀원의 리더십 개발이 고민이 된다.",
        "characteristics": ["빠른 순응", "지원 역할 선호", "주도성 부족"]
    },
    "Doer": {
        "description": "R&R이 분명할 경우 업무에 대한 이해가 빠르고 정확도 높게 업무를 처리한다. 다만 새로운 아이디어가 필요하거나 개념 수준에서 논의가 필요한 상황일 때 혼란스러워한다.",
        "characteristics": ["정확한 실행", "명확한 R&R 선호", "개념 논의 어려움"]
    },
    "Follower": {
        "description": "업무 동기가 떨어져 보이고, 업무 실수 및 업무 몰입도가 많이 떨어져 있다. 최근들어 이 팀원의 업무 몰입을 높이기 위해 어떻게 접근해야 할지에 대한 고민이 깊어졌다.",
        "characteristics": ["낮은 동기", "낮은 몰입도", "업무 실수 증가"]
    }
}


def classify_leadership_type(
    sharing_participation: float,
    interaction: float,
    growth_orientation: float
) -> str:
    """
    리더십 유형 분류

    Args:
        sharing_participation: 공유및참여 점수 (0-5)
        interaction: 상호작용 점수 (0-5)
        growth_orientation: 성장지향 점수 (0-5)

    Returns:
        str: 리더십 유형
    """
    threshold = 4.5

    # 각 차원이 임계값 이상인지 확인
    sp_high = sharing_participation >= threshold
    ia_high = interaction >= threshold
    go_high = growth_orientation >= threshold

    # 분류 로직
    if sp_high and ia_high and go_high:
        return "참여코칭형"
    elif sp_high and not ia_high and not go_high:
        return "참여실무형"
    elif sp_high and not ia_high and go_high:
        return "참여비전형"
    elif sp_high and ia_high and not go_high:
        return "참여친밀형"
    elif not sp_high and ia_high and go_high:
        return "개별코칭형"
    elif not sp_high and not ia_high and go_high:
        return "개별비전형"
    elif not sp_high and ia_high and not go_high:
        return "개별친밀형"
    else:  # not sp_high and not ia_high and not go_high
        return "과도기형"


def get_leadership_info(leadership_type: str) -> Dict[str, Any]:
    """리더십 유형 정보 조회"""
    return LEADERSHIP_TYPES.get(leadership_type, {})


def get_followership_info(followership_type: str) -> Dict[str, Any]:
    """팔로워십 유형 정보 조회"""
    return FOLLOWERSHIP_TYPES.get(followership_type, {})


def analyze_collaboration_compatibility(
    leadership_type: str,
    followership_type: str
) -> Dict[str, Any]:
    """
    리더십-팔로워십 협업 궁합 분석

    Returns:
        dict: 궁합 분석 결과
            - compatibility_score: 궁합 점수 (0-100)
            - strengths: 강점 리스트
            - challenges: 어려움 리스트
            - recommendations: 권장사항 리스트
    """
    # TODO: 실제 궁합 매트릭스 구현
    # 현재는 기본 구조만 반환
    return {
        "compatibility_score": 75,
        "strengths": ["상호 보완적 강점"],
        "challenges": ["의사소통 방식 차이"],
        "recommendations": ["정기적인 1:1 미팅"]
    }
