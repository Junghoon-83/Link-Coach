"""
로깅 설정
구조화된 로깅 및 포맷 설정
"""
import logging
import sys
from typing import Any
from pythonjsonlogger import jsonlogger

from app.config import settings


def setup_logging():
    """
    애플리케이션 로깅 설정

    - 개발 환경: 사람이 읽기 쉬운 포맷
    - 프로덕션: JSON 구조화 로그
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 기존 핸들러 제거
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 콘솔 핸들러 생성
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    if settings.is_production:
        # 프로덕션: JSON 포맷
        json_formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(json_formatter)
    else:
        # 개발: 사람이 읽기 쉬운 포맷
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)

    # 외부 라이브러리 로그 레벨 조정
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    로거 인스턴스 반환

    Args:
        name: 로거 이름 (보통 __name__)

    Returns:
        logging.Logger: 로거 인스턴스
    """
    return logging.getLogger(name)
