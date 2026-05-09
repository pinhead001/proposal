import os
import logging

logger = logging.getLogger(__name__)

LLM_PROVIDER: str = os.environ.get("LLM_PROVIDER", "claude").lower()
CORS_ORIGINS: list[str] = os.environ.get("CORS_ORIGINS", "*").split(",")
API_KEY: str | None = os.environ.get("PROPOSAL_API_KEY")


def _safe_int(name: str, default: int) -> int:
    raw = os.environ.get(name, str(default))
    try:
        return int(raw)
    except ValueError:
        logger.warning("Invalid %s=%r, using default %d", name, raw, default)
        return default


def _safe_float(name: str, default: float) -> float:
    raw = os.environ.get(name, str(default))
    try:
        return float(raw)
    except ValueError:
        logger.warning("Invalid %s=%r, using default %s", name, raw, default)
        return default


LLM_MAX_TOKENS: int = _safe_int("LLM_MAX_TOKENS", 2048)
LLM_TEMPERATURE: float = _safe_float("LLM_TEMPERATURE", 0.3)
MAX_UPLOAD_SIZE_MB: int = _safe_int("MAX_UPLOAD_SIZE_MB", 10)
MAX_RFP_LENGTH: int = _safe_int("MAX_RFP_LENGTH", 100000)
