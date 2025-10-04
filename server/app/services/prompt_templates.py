"""
AI 코칭 프롬프트 템플릿
"""
from typing import Dict, Any, Optional, List


def get_interpretation_prompt(
    leadership_type: str,
    leadership_info: Dict[str, Any],
    followership_types: Optional[list] = None,
    assessment_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    리더십 해석 리포트 생성 프롬프트
    """
    # (기존 코드와 동일, 변경 없음)
    description = leadership_info.get("description", "")
    strengths = leadership_info.get("strengths", "")
    best_situations = leadership_info.get("best_situations", [])
    follower_context = ""
    if followership_types:
        follower_context = "\n\n**팀원의 팔로워십 유형:**\n" + "\n".join([
            f"- {ftype}" for ftype in followership_types
        ])
    prompt = f"""당신은 리더십 코칭 전문가입니다. 다음 리더에 대한 심층 분석 리포트를 작성해주세요.

리더십 유형: {leadership_type}
{follower_context}

다음과 같은 전문 보고서 형식으로 작성해주세요. 마크다운 기호(#, *, -, 등)를 사용하지 말고 순수 텍스트로 작성하되, 섹션 제목은 명확히 구분해주세요:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
리더십 분석 보고서
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[개요]

리더십 유형: {leadership_type}

{strengths if strengths else description}

이럴 때 강하다: {', '.join(best_situations) if best_situations else '다양한 상황에서 강점을 발휘합니다'}


[1. 팀 운영의 어려움]

{leadership_type} 리더가 팀을 운영할 때 흔히 겪는 3-4가지 주요 어려움을 구체적인 상황 예시와 함께 설명해주세요. 각 어려움이 왜 발생하는지 리더십 유형 특성과 연결하여 분석해주세요.


[2. 팔로워와의 협업 궁합]

각 팔로워십 유형(Driver, Thinker, Supporter, Doer, Follower)과의 협업 시 다음 내용을 포함해주세요:
- 궁합 점수 (상/중/하)
- 시너지 포인트 (어떤 점에서 잘 맞는가)
- 주의 포인트 (어떤 점에서 충돌할 수 있는가)
- 효과적인 협업 방법 1-2가지


[3. 코칭팁]

《시니어 리더일 때》 (5년 이상 경력)
리더십 강화를 위한 3가지 핵심 조언, 조직 영향력을 높이는 방법, 후배 리더 육성 시 주의점을 제시해주세요.

《주니어 리더일 때》 (5년 미만 경력)
리더십 기반을 다지기 위한 3가지 핵심 조언, 팀원 신뢰 구축 방법, 초기 리더로서 피해야 할 실수를 제시해주세요.


[4. 리더십 개발 성과지표]

{leadership_type} 리더가 성장하고 있다는 것을 보여주는 5가지 구체적인 지표와 각 지표를 측정하고 추적하는 방법을 제시해주세요. 3개월, 6개월, 1년 단위 마일스톤도 포함해주세요.


[5. 리더십 리스크 신호]

{leadership_type} 리더가 주의해야 할 5가지 위험 신호와 각 신호가 나타날 때의 구체적인 상황, 그리고 신호 감지 시 즉시 취해야 할 조치를 설명해주세요.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

작성 가이드라인:
1. 마크다운 기호를 사용하지 말고 순수 텍스트로 작성
2. 섹션은 [ ] 로 표시하고, 하위 항목은 《 》 로 표시
3. 전문적이면서도 이해하기 쉬운 언어 사용
4. 구체적이고 실행 가능한 조언 제공
5. 긍정적이고 성장 지향적인 톤 유지
6. 한국 기업 문화에 적합한 예시 사용

위 형식으로 리포트를 작성해주세요:"""

    return prompt


def get_context_string(
    leadership_type: str,
    report_context: Optional[str] = None,
    retrieved_context: Optional[str] = None,
) -> str:
    """
    Q&A에 필요한 컨텍스트 문자열을 조합하는 함수
    """
    context_parts = [f"리더의 리더십 유형은 {leadership_type}입니다."]

    if report_context:
        context_parts.append(f"\n[리포트 요약]\n{report_context}")

    if retrieved_context:
        context_parts.append(f"\n[관련 참고자료]\n{retrieved_context}")

    return "\n".join(context_parts)


def build_final_prompt(
    question: str,
    system_prompt: str,
    context_string: str,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> List[Dict[str, str]]:
    """
    최종적으로 LLM에 전달될 메시지 리스트를 구성
    """
    messages = [{"role": "system", "content": system_prompt}]

    # 이전 대화 내역 추가 (최근 3개)
    if conversation_history:
        for message in conversation_history[-3:]:
            messages.append({
                "role": "user" if message["role"] == "user" else "assistant",
                "content": message["content"]
            })
    
    # 컨텍스트와 현재 질문을 포함한 사용자 메시지 구성
    user_message_content = f"[현재 대화의 전체 맥락]\n{context_string}\n\n[리더의 질문]\n{question}"
    messages.append({"role": "user", "content": user_message_content})

    return messages