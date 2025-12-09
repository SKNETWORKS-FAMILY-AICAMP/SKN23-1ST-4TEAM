# utils/log_utils.py
import logging
from logging.handlers import RotatingFileHandler
from config import LOG_LEVEL, LOGGING_ENABLED

LOG_FILE = "logs/app.log"

# 로그 파일 핸들러 설정
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=1_000_000,    # 1MB 넘어가면 자동 회전
    backupCount=5
)

formatter = logging.Formatter(
    '[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

file_handler.setFormatter(formatter)

# 로거 생성
logger = logging.getLogger("backend_logger")
logger.setLevel(LOG_LEVEL)
logger.addHandler(file_handler)


# -------------------------
#  로그 함수 (프로젝트 전체에서 사용)
# -------------------------

def log_info(message: str):
    """일반 정보 로그"""
    if LOGGING_ENABLED:
        logger.info(message)

def log_error(message: str):
    """에러 로그"""
    if LOGGING_ENABLED:
        logger.error(message)

def log_warning(message: str):
    """경고 로그"""
    if LOGGING_ENABLED:
        logger.warning(message)

def log_debug(message: str):
    """디버깅용"""
    if LOGGING_ENABLED:
        logger.debug(message)