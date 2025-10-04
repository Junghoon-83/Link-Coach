"""
개발용 샘플 ML 모델 생성 스크립트
실제 프로덕션에서는 학습된 모델을 사용해야 합니다
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_dummy_model():
    """
    개발용 더미 ML 모델 생성

    실제 모델은 다음과 같은 특성을 가져야 합니다:
    - 입력: 리더십 진단 점수 (예: extraversion, thinking, judging 등)
    - 출력: 리더십 유형 (ENTJ, INTJ, ENFJ 등)
    """
    try:
        logger.info("샘플 ML 모델 생성 중...")

        # 샘플 학습 데이터 생성
        # 특성: [extraversion, thinking, judging, sensing]
        # 레이블: 0=ENTJ, 1=INTJ, 2=ENFJ, 3=INFJ
        np.random.seed(42)

        X_train = np.random.rand(100, 4) * 100  # 100개 샘플, 4개 특성
        y_train = np.random.randint(0, 4, 100)  # 4개 클래스

        # RandomForest 모델 학습
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X_train, y_train)

        # 모델 저장
        model_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
        os.makedirs(model_dir, exist_ok=True)

        model_path = os.path.join(model_dir, 'leadership_classifier.pkl')
        joblib.dump(model, model_path)

        logger.info(f"✅ 샘플 모델 저장: {model_path}")

        # 모델 검증
        logger.info("모델 검증 중...")
        loaded_model = joblib.load(model_path)

        test_input = np.array([[80, 75, 70, 60]])  # 샘플 입력
        prediction = loaded_model.predict(test_input)
        probabilities = loaded_model.predict_proba(test_input)

        logger.info(f"테스트 예측: {prediction[0]}")
        logger.info(f"확률 분포: {probabilities[0]}")

        logger.info("""
⚠️  주의: 이것은 개발용 더미 모델입니다!
실제 프로덕션 환경에서는 다음을 수행해야 합니다:
1. 실제 리더십 진단 데이터로 모델 학습
2. 교차 검증 및 성능 평가
3. 학습된 모델을 models/ 디렉토리에 배치
4. 모델 버전 관리
        """)

    except Exception as e:
        logger.error(f"❌ 모델 생성 실패: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    create_dummy_model()
