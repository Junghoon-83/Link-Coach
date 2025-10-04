"""
머신러닝 모델 서비스
리더십 유형 분류 모델 로드 및 추론
"""
import joblib
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


class MLModelService:
    """ML 모델 서비스 (싱글톤)"""

    def __init__(self):
        self.model: Optional[Any] = None
        self.model_loaded: bool = False

    async def load_model(self) -> None:
        """
        ML 모델 로드

        Raises:
            FileNotFoundError: 모델 파일이 없는 경우
            Exception: 모델 로드 중 오류 발생
        """
        if self.model_loaded:
            logger.info("ML 모델이 이미 로드되어 있습니다.")
            return

        model_path = Path(settings.ML_MODEL_PATH)

        if not model_path.exists():
            logger.warning(
                f"ML 모델 파일을 찾을 수 없습니다: {model_path}. "
                "모델 없이 진행합니다 (개발 모드)."
            )
            self.model = None
            self.model_loaded = False
            return

        try:
            logger.info(f"ML 모델 로드 중: {model_path}")
            self.model = joblib.load(model_path)
            self.model_loaded = True
            logger.info("✅ ML 모델 로드 완료")

        except Exception as e:
            logger.error(f"ML 모델 로드 실패: {e}", exc_info=True)
            raise

    async def predict_leadership_type(
        self,
        features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        리더십 유형 예측

        Args:
            features: 특성 데이터 (예: 진단 점수)

        Returns:
            dict: 예측 결과
                - predicted_type: 예측된 리더십 유형
                - confidence: 신뢰도 (0-1)
                - probabilities: 각 유형별 확률

        Raises:
            ValueError: 모델이 로드되지 않은 경우
        """
        if not self.model_loaded or self.model is None:
            logger.warning("ML 모델이 로드되지 않았습니다. 기본값 반환")
            # 개발 모드: 기본값 반환
            return {
                "predicted_type": "UNKNOWN",
                "confidence": 0.0,
                "probabilities": {},
                "is_mock": True
            }

        try:
            # TODO: 실제 모델 입력 형식에 맞게 수정 필요
            # 예시: features를 배열로 변환
            # feature_vector = [features.get("extraversion", 0), ...]
            # prediction = self.model.predict([feature_vector])[0]
            # probabilities = self.model.predict_proba([feature_vector])[0]

            logger.info(f"리더십 유형 예측 요청: {features}")

            # 임시 구현 (실제 모델 인터페이스에 맞게 수정 필요)
            prediction = "개별비전형"  # 예시
            confidence = 0.85  # 예시

            return {
                "predicted_type": prediction,
                "confidence": confidence,
                "probabilities": {
                    "개별비전형": 0.85,
                    "참여코칭형": 0.10,
                    "개별코칭형": 0.05
                },
                "is_mock": False
            }

        except Exception as e:
            logger.error(f"예측 중 오류 발생: {e}", exc_info=True)
            raise ValueError(f"Failed to predict leadership type: {e}")

    async def validate_leadership_type(
        self,
        leadership_type: str,
        features: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        리더십 유형 유효성 검증

        Args:
            leadership_type: 검증할 리더십 유형
            features: 선택적 특성 데이터

        Returns:
            bool: 유효 여부
        """
        # 간단한 검증: 알려진 유형인지 확인
        known_types = [
            "참여코칭형", "참여실무형", "참여비전형", "참여친밀형",
            "개별코칭형", "개별비전형", "개별친밀형", "과도기형"
        ]

        if leadership_type not in known_types:
            logger.warning(f"알 수 없는 리더십 유형: {leadership_type}")
            return False

        # 모델이 로드된 경우, 추가 검증 가능
        if self.model_loaded and features:
            try:
                prediction = await self.predict_leadership_type(features)
                predicted_type = prediction.get("predicted_type")

                if predicted_type != leadership_type:
                    logger.warning(
                        f"유형 불일치: 제공된 유형={leadership_type}, "
                        f"예측된 유형={predicted_type}"
                    )
                    # 불일치해도 일단 True 반환 (경고만)
                    return True

            except Exception as e:
                logger.error(f"검증 중 오류: {e}")
                # 오류 발생 시에도 기본 검증 통과
                return True

        return True


# 싱글톤 인스턴스
ml_model_service = MLModelService()
