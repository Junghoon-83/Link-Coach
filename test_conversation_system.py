"""
대화 정교화 고도화 시스템 테스트
- 오프토픽 감지
- 대화 단계 판단
- 응답 전략 선택
"""
import sys
import os

# 서버 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from app.services.conversation_analyzer import conversation_analyzer


def print_section(title: str):
    """섹션 헤더 출력"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_analysis(question: str, history: list = None):
    """질문 분석 결과 출력"""
    analysis = conversation_analyzer.analyze(question, history)
    strategy = conversation_analyzer.get_response_strategy(analysis)

    print(f"\n📝 질문: {question}")
    if history:
        print(f"   대화 기록: {len(history)}개 메시지")

    print(f"\n분석 결과:")
    print(f"  • 대화 단계: {analysis['stage']} ({['인사', '탐색', '심층코칭', '실행계획'][analysis['stage']-1]})")
    print(f"  • 오프토픽: {'예 (' + analysis['offtopic_category'] + ')' if analysis['is_offtopic'] else '아니오'}")
    print(f"  • 특성: {', '.join(analysis['traits'])}")
    print(f"  • 감정: {', '.join([k for k, v in analysis['emotion'].items() if v]) or '중립'}")
    print(f"  • 컨텍스트 필요: {'예' if analysis['requires_context'] else '아니오'}")
    print(f"\n응답 전략: {strategy}")
    print("-" * 80)


def test_offtopic_detection():
    """오프토픽 감지 테스트"""
    print_section("오프토픽 감지 테스트")

    test_cases = [
        ("오늘 날씨 어때요?", None, True, "날씨"),
        ("점심 뭐 먹을까요?", None, True, "음식"),
        ("컴퓨터가 고장났어요", None, True, "기술"),
        ("직원 해고할 때 법적으로 문제 없나요?", None, True, "법률"),
        ("이 서비스는 뭐하는 거예요?", None, True, "메타"),
        ("asdfasdf", None, True, "난센스"),
        ("팀원과 소통이 어려워요", None, False, None),
        ("이직을 고민 중이에요", None, False, None),
    ]

    correct = 0
    total = len(test_cases)

    for question, history, expected_offtopic, expected_category in test_cases:
        analysis = conversation_analyzer.analyze(question, history)

        is_correct = analysis['is_offtopic'] == expected_offtopic
        if is_correct and expected_offtopic:
            is_correct = analysis['offtopic_category'] == expected_category

        if is_correct:
            correct += 1
            status = "✅"
        else:
            status = "❌"

        print(f"{status} {question[:40]:40} | 예상: {expected_offtopic} | 실제: {analysis['is_offtopic']}")

    print(f"\n정확도: {correct}/{total} ({correct/total*100:.1f}%)")


def test_conversation_stages():
    """대화 단계 판단 테스트"""
    print_section("대화 단계 판단 테스트")

    # 1. 인사 단계
    print("\n1️⃣ 인사 단계")
    print_analysis("안녕하세요!")
    print_analysis("좋은 아침이에요")

    # 2. 탐색 단계
    print("\n2️⃣ 탐색 단계")
    history = [
        {"role": "user", "content": "안녕하세요"},
        {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"}
    ]
    print_analysis("팀 관리에 대해 궁금해요", history)

    # 3. 심층 코칭 단계
    print("\n3️⃣ 심층 코칭 단계")
    history = [
        {"role": "user", "content": "팀 관리에 대해 궁금해요"},
        {"role": "assistant", "content": "어떤 부분이 궁금하신가요?"},
        {"role": "user", "content": "팀원들이 제 말을 안 들어요"},
        {"role": "assistant", "content": "구체적으로 어떤 상황인가요?"}
    ]
    print_analysis("정말 답답해요. 이미 다 해봤는데 안 돼요", history)

    # 4. 실행 계획 단계
    print("\n4️⃣ 실행 계획 단계")
    long_history = history + [
        {"role": "user", "content": "정말 답답해요"},
        {"role": "assistant", "content": "그동안 어떤 시도를 하셨나요?"},
        {"role": "user", "content": "1on1도 하고 피드백도 줬어요"},
        {"role": "assistant", "content": "조금 더 구체적인 방법을 같이 찾아볼까요?"}
    ]
    print_analysis("구체적인 실행 계획을 세우고 싶어요", long_history)


def test_emotion_detection():
    """감정 감지 테스트"""
    print_section("감정 감지 테스트")

    print("\n😤 좌절/답답함")
    print_analysis("팀 관리가 너무 힘들어요. 뭘 해도 안 되네요.")

    print("\n🤔 저항/회의")
    print_analysis("이미 다 해봤는데 소용없었어요. 어차피 안 될 거예요.")

    print("\n🚨 긴급")
    print_analysis("내일 회의인데 당장 어떻게 해야 할지 모르겠어요")

    print("\n😊 긍정")
    print_analysis("지난번 조언이 정말 도움이 됐어요. 팀 분위기가 좋아졌어요!")


def test_response_strategies():
    """응답 전략 테스트"""
    print_section("응답 전략 매핑 테스트")

    test_cases = [
        ("안녕하세요!", None, "warm_welcome"),
        ("팀 관리에 대해 궁금해요", [{"role": "user", "content": "안녕"}], "open_exploration"),
        ("너무 답답해요", [{"role": "user", "content": "팀 문제"}], "empathetic_exploration"),
        ("이미 다 해봤는데 안 돼요", [{"role": "user", "content": "고민"}] * 2, "gentle_challenge"),
        ("내일까지 급해요", None, "immediate_action"),
        ("오늘 날씨 어때요?", None, "gentle_redirect"),
        ("직원 해고 법적 문제", None, "redirect_to_expert"),
        ("이 서비스 뭐예요?", None, "service_info"),
        ("asdfasdf", None, "clarify_question"),
    ]

    correct = 0
    for question, history, expected_strategy in test_cases:
        analysis = conversation_analyzer.analyze(question, history)
        actual_strategy = conversation_analyzer.get_response_strategy(analysis)

        is_correct = actual_strategy == expected_strategy
        if is_correct:
            correct += 1
            status = "✅"
        else:
            status = "❌"

        print(f"{status} {question[:40]:40} | 예상: {expected_strategy:25} | 실제: {actual_strategy}")

    print(f"\n정확도: {correct}/{len(test_cases)} ({correct/len(test_cases)*100:.1f}%)")


def test_complex_scenarios():
    """복잡한 시나리오 테스트"""
    print_section("복잡한 시나리오 테스트")

    print("\n📌 시나리오 1: 오프토픽에서 리더십으로 자연스럽게 전환")
    print_analysis("요즘 날씨가 너무 더워요")
    print_analysis("네, 그래서 팀원들도 지쳐 보이는 것 같아요. 어떻게 동기부여 해야 할까요?")

    print("\n📌 시나리오 2: 감정 고조 상황")
    history = [
        {"role": "user", "content": "팀원이 말을 안 들어요"},
        {"role": "assistant", "content": "어떤 상황인가요?"}
    ]
    print_analysis("정말 화가 나요. 도대체 왜 이러는 거죠?", history)

    print("\n📌 시나리오 3: 경계선 케이스 (리더십 vs 개인 고민)")
    print_analysis("제 성격이 너무 급해서 팀원들과 자주 부딪혀요")

    print("\n📌 시나리오 4: 복잡한 상황 설명")
    long_question = """
    저희 팀에서 A직원과 B직원이 계속 갈등을 빚고 있어요.
    프로젝트 마감은 다음 주인데, 둘이 협업을 거부하고 있습니다.
    제가 중재를 시도했지만 오히려 상황이 악화됐어요.
    어떻게 해야 할까요?
    """
    print_analysis(long_question.strip())


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "🚀" * 40)
    print("  대화 정교화 고도화 시스템 테스트 시작")
    print("🚀" * 40)

    test_offtopic_detection()
    test_conversation_stages()
    test_emotion_detection()
    test_response_strategies()
    test_complex_scenarios()

    print("\n" + "✅" * 40)
    print("  테스트 완료")
    print("✅" * 40)
    print()


if __name__ == "__main__":
    run_all_tests()
