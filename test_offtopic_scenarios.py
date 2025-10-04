"""
엉뚱한 말/오프토픽 시나리오 테스트
"""

def analyze_question(question: str, conversation_history: list = None):
    """질문 분석 로직"""
    conversation_stage = 1
    if conversation_history:
        conversation_stage = min(len(conversation_history) // 2 + 1, 4)

    question_lower = question.lower()
    question_len = len(question)

    # 1. 인사말
    greeting_patterns = ['안녕', '하이', '헬로', '반갑']
    is_greeting = any(word in question_lower for word in greeting_patterns)
    if '좋은' in question_lower and any(time in question_lower for time in ['아침', '저녁', '오후', '하루', '주말']):
        is_greeting = True

    # 2. 긴급성
    is_urgent = any(word in question_lower for word in ['당장', '급하', '내일', '오늘', '지금 바로'])

    # 3. 감정 표현
    is_frustrated = any(word in question_lower for word in [
        '답답', '힘들', '어렵', '막막', '모르겠', '지치', '지쳐',
        '화나', '불안', '두렵', '걱정', '포기'
    ])

    # 4. 저항/회의
    is_resistant = any(phrase in question_lower for phrase in [
        '이미', '해봤', '안 됐', '안 돼', '소용없', '안 될',
        '그런데', '하지만', '어차피'
    ])

    # 5. 긍정 피드백
    is_positive = any(word in question_lower for word in [
        '효과', '좋았', '도움', '감사', '성공', '잘 됐', '해결'
    ]) and not is_frustrated

    # 6. 구체적 요청
    is_wellbeing_question = any(phrase in question_lower for phrase in [
        '지내', '어때', '괜찮', '잘 있', '건강', '안녕'
    ])

    is_specific_request = (
        '어떻게' in question_lower or
        '어떡' in question_lower or
        '방법' in question_lower or
        '뭐' in question_lower or
        '무엇' in question_lower or
        '?' in question or
        (question.endswith('죠') and not is_wellbeing_question) or
        (question.endswith('나요') and not is_wellbeing_question) or
        (question.endswith('을까요') and not is_wellbeing_question) or
        (question.endswith('요') and len(question) > 10 and not is_greeting) or
        question.endswith('요.') or
        question.endswith('어요')
    )

    # 7. 복잡도
    has_multiple_subjects = sum(1 for char in question if char in ['A', 'B', 'C', '그', '또']) >= 2
    is_complex = question_len > 50 or has_multiple_subjects

    # 8. 오프토픽 감지
    offtopic_keywords = {
        '날씨': ['날씨', '비', '눈', '맑', '흐림', '온도', '더워', '추워', '뭐하는 거'],
        '음식': ['점심', '저녁', '아침', '먹을', '맛집', '음식', '메뉴'],
        '기술': ['컴퓨터', '프로그램', '버그', '설치', '고장', '인터넷', '와이파이'],
        '의료': ['병원', '약', '의사', '진료', '우울증', '치료', '증상', '아파'],
        '법률': ['법', '소송', '계약서', '변호사', '법적', '문제 없나', '문제없나'],
        '메타': ['서비스', 'ai', '인공지능', '유료', '가격', '요금', '개인정보', '관리되나'],
        '일상': ['취미', '주식', '재테크', '운동', '영화', '드라마'],
        '난센스': ['1+1', 'asdf', 'how are you', '??']
    }

    is_offtopic = False
    offtopic_category = None

    # 리더십 관련 키워드 (오프토픽 아님)
    leadership_keywords = ['팀', '리더', '직원', '부하', '상사', '회의', '업무', '프로젝트',
                          '성과', '목표', '관리', '소통', '커뮤니케이션', '의사결정',
                          '갈등', '동기부여', '코칭', '피드백', '1on1', '조직', '해고', '이직']

    has_leadership_context = any(keyword in question_lower for keyword in leadership_keywords)

    # 1) 한글이 거의 없는 경우 (외국어/난센스)
    korean_chars = sum(1 for c in question if '가' <= c <= '힣')
    if korean_chars < len(question) * 0.3 and len(question) > 3:  # 한글 30% 미만
        is_offtopic = True
        offtopic_category = '난센스'

    # 2) 리더십 맥락 없이 오프토픽 키워드만 있으면 오프토픽
    if not is_offtopic and not has_leadership_context:
        for category, keywords in offtopic_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                is_offtopic = True
                offtopic_category = category
                break

    # 단계 조정
    if is_greeting and conversation_stage == 1:
        conversation_stage = 1
    elif is_urgent or is_resistant:
        conversation_stage = max(conversation_stage, 3)
    elif is_frustrated and '모르겠' in question_lower:
        conversation_stage = max(conversation_stage, 3)
    elif is_frustrated and '포기' in question_lower:
        conversation_stage = max(conversation_stage, 3)
    elif is_specific_request and (is_frustrated or is_complex or conversation_stage >= 3):
        conversation_stage = max(conversation_stage, 3)
    elif is_frustrated:
        conversation_stage = max(conversation_stage, 2)
    elif is_complex and conversation_stage == 1:
        conversation_stage = 2
    elif is_specific_request and conversation_stage >= 2:
        conversation_stage = max(conversation_stage, 3)
    elif is_specific_request and question_len > 15:
        conversation_stage = 3

    # 특성 목록
    traits = []
    if is_offtopic: traits.append(f"오프토픽-{offtopic_category}")
    if is_greeting: traits.append("인사")
    if is_urgent: traits.append("긴급")
    if is_frustrated: traits.append("감정표현")
    if is_resistant: traits.append("저항/회의")
    if is_positive: traits.append("긍정피드백")
    if is_complex: traits.append("복잡한상황")
    if is_specific_request: traits.append("구체적요청")

    return {
        "stage": conversation_stage,
        "length": question_len,
        "traits": traits if traits else ["일반질문"],
        "is_offtopic": is_offtopic,
        "offtopic_category": offtopic_category
    }


# 엉뚱한 말/오프토픽 시나리오
offtopic_scenarios = [
    # === 완전 오프토픽 ===
    {
        "category": "완전오프토픽",
        "name": "날씨 질문",
        "question": "오늘 날씨 어때요?",
        "history": [],
        "expected": {
            "offtopic": True,
            "response_type": "부드럽게 주제 전환 (리더십/팀 관리로)"
        }
    },
    {
        "category": "완전오프토픽",
        "name": "음식 추천",
        "question": "점심 뭐 먹을까요?",
        "history": [{"role": "user", "content": "팀 관리"}, {"role": "assistant", "content": "조언"}],
        "expected": {
            "offtopic": True,
            "response_type": "가볍게 받되 코칭으로 유도"
        }
    },
    {
        "category": "완전오프토픽",
        "name": "취미 질문",
        "question": "취미가 뭐예요?",
        "history": [],
        "expected": {
            "offtopic": True,
            "response_type": "간단 답변 + 대화 목적 확인"
        }
    },
    {
        "category": "완전오프토픽",
        "name": "뉴스 질문",
        "question": "요즘 주식 시장 어떻게 봐요?",
        "history": [],
        "expected": {
            "offtopic": True,
            "response_type": "전문 범위 벗어남 언급 + 리더십 연결"
        }
    },

    # === 경계선 (리더십 관련일 수도) ===
    {
        "category": "경계선",
        "name": "개인 고민",
        "question": "이직을 고민 중이에요",
        "history": [],
        "expected": {
            "offtopic": False,
            "response_type": "리더 커리어도 코칭 범위 - 탐색"
        }
    },
    {
        "category": "경계선",
        "name": "개인 성장",
        "question": "제 성격을 바꾸고 싶어요",
        "history": [],
        "expected": {
            "offtopic": False,
            "response_type": "리더십과 연결 가능 - 성격과 리더십 스타일"
        }
    },
    {
        "category": "경계선",
        "name": "일상 스트레스",
        "question": "요즘 너무 피곤해요",
        "history": [],
        "expected": {
            "offtopic": False,
            "response_type": "번아웃 체크 - 리더 웰빙도 중요"
        }
    },

    # === 부적절한 요청 ===
    {
        "category": "부적절",
        "name": "기술 지원",
        "question": "컴퓨터가 고장났는데 어떻게 고치죠?",
        "history": [],
        "expected": {
            "offtopic": True,
            "response_type": "전문 범위 벗어남 - 적절한 지원 안내"
        }
    },
    {
        "category": "부적절",
        "name": "법률 자문",
        "question": "직원 해고할 때 법적으로 문제 없나요?",
        "history": [],
        "expected": {
            "offtopic": True,
            "response_type": "전문 법률 자문 필요 - 전문가 추천"
        }
    },
    {
        "category": "부적절",
        "name": "의료 상담",
        "question": "우울증인 것 같은데 약 먹어야 하나요?",
        "history": [],
        "expected": {
            "offtopic": True,
            "response_type": "전문 의료인 상담 권유"
        }
    },

    # === 장난/테스트 ===
    {
        "category": "장난/테스트",
        "name": "AI 테스트",
        "question": "너 AI야?",
        "history": [],
        "expected": {
            "offtopic": True,
            "response_type": "솔직하게 답변 + 도움 제공 의지"
        }
    },
    {
        "category": "장난/테스트",
        "name": "능력 시험",
        "question": "1+1은?",
        "history": [],
        "expected": {
            "offtopic": True,
            "response_type": "간단 답변 + 진짜 고민 확인"
        }
    },
    {
        "category": "장난/테스트",
        "name": "욕설/비속어",
        "question": "씨발 이거 왜 안 돼?",
        "history": [],
        "expected": {
            "offtopic": False,
            "response_type": "감정 이해 + 차분히 상황 파악"
        }
    },

    # === 모호한 표현 ===
    {
        "category": "모호함",
        "name": "의미 불명",
        "question": "asdfasdf",
        "history": [],
        "expected": {
            "offtopic": True,
            "response_type": "이해 불가 - 다시 질문 요청"
        }
    },
    {
        "category": "모호함",
        "name": "외국어",
        "question": "How are you?",
        "history": [],
        "expected": {
            "offtopic": True,
            "response_type": "한국어 안내 or 간단 영어 응답"
        }
    },
    {
        "category": "모호함",
        "name": "이모지만",
        "question": "😭😭😭",
        "history": [],
        "expected": {
            "offtopic": False,
            "response_type": "감정 공감 + 무슨 일인지 탐색"
        }
    },

    # === 메타 질문 ===
    {
        "category": "메타질문",
        "name": "서비스 질문",
        "question": "이 서비스는 뭐하는 거예요?",
        "history": [],
        "expected": {
            "offtopic": True,
            "response_type": "서비스 설명 + 어떻게 도울지 질문"
        }
    },
    {
        "category": "메타질문",
        "name": "가격 문의",
        "question": "유료인가요?",
        "history": [],
        "expected": {
            "offtopic": True,
            "response_type": "서비스 정보 안내 - 고객센터 등"
        }
    },
    {
        "category": "메타질문",
        "name": "개인정보",
        "question": "제 정보는 어떻게 관리되나요?",
        "history": [],
        "expected": {
            "offtopic": True,
            "response_type": "개인정보 정책 안내"
        }
    },
]


def run_offtopic_tests():
    """오프토픽 테스트 실행"""
    print("=" * 80)
    print("엉뚱한 말/오프토픽 시나리오 테스트")
    print("=" * 80)

    categories = {}

    for scenario in offtopic_scenarios:
        result = analyze_question(
            scenario["question"],
            scenario.get("history", [])
        )

        category = scenario["category"]
        if category not in categories:
            categories[category] = {"total": 0, "cases": []}

        categories[category]["total"] += 1
        categories[category]["cases"].append({
            "name": scenario["name"],
            "question": scenario["question"],
            "expected_offtopic": scenario["expected"]["offtopic"],
            "actual_offtopic": result["is_offtopic"],
            "expected_response": scenario["expected"]["response_type"],
            "stage": result["stage"],
            "traits": result["traits"]
        })

    # 카테고리별 결과 출력
    for category, data in categories.items():
        print(f"\n【{category}】 ({data['total']}개)")
        print("-" * 80)

        for case in data["cases"]:
            # 오프토픽 감지 결과 검증
            expected = case['expected_offtopic']
            actual = case['actual_offtopic']

            if expected == actual:
                status = "✅ 정상"
            else:
                if expected and not actual:
                    status = "❌ 미감지"
                else:
                    status = "❌ 오감지"

            print(f"{status} {case['name']}")
            print(f"   질문: {case['question'][:50]}{'...' if len(case['question']) > 50 else ''}")
            print(f"   예상: 오프토픽={expected}, 실제: 오프토픽={actual}")
            print(f"   예상응답: {case['expected_response']}")
            print(f"   현재 분석: 단계={case['stage']}, 특성={', '.join(case['traits'])}")
            print()

    # 통계 계산
    total = len(offtopic_scenarios)
    correct = sum(1 for s in offtopic_scenarios
                  if analyze_question(s["question"], s.get("history", []))["is_offtopic"] == s["expected"]["offtopic"])
    pass_rate = (correct / total * 100) if total > 0 else 0

    print("=" * 80)
    print(f"테스트 결과: {correct}/{total} 통과 ({pass_rate:.0f}%)")
    print("=" * 80)

    # 오프토픽 감지 상세 분석
    offtopic_expected = [s for s in offtopic_scenarios if s["expected"]["offtopic"]]
    offtopic_detected = sum(1 for s in offtopic_expected
                           if analyze_question(s["question"], s.get("history", []))["is_offtopic"])

    print(f"\n오프토픽 감지: {offtopic_detected}/{len(offtopic_expected)}개 ({offtopic_detected/len(offtopic_expected)*100:.0f}%)")

    # 미감지 케이스
    missed = [s for s in offtopic_expected
              if not analyze_question(s["question"], s.get("history", []))["is_offtopic"]]
    if missed:
        print(f"\n❌ 미감지된 케이스 ({len(missed)}개):")
        for s in missed:
            print(f"  - {s['name']}: \"{s['question']}\"")

    # 오감지 케이스
    false_positives = [s for s in offtopic_scenarios
                       if not s["expected"]["offtopic"]
                       and analyze_question(s["question"], s.get("history", []))["is_offtopic"]]
    if false_positives:
        print(f"\n⚠️ 오감지된 케이스 ({len(false_positives)}개):")
        for s in false_positives:
            result = analyze_question(s["question"], s.get("history", []))
            print(f"  - {s['name']}: \"{s['question']}\" (감지: {result.get('offtopic_category')})")


if __name__ == "__main__":
    run_offtopic_tests()
