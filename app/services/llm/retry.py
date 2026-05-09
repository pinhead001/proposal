import logging
import time
from typing import Callable, TypeVar

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_BASE_DELAY = 2

T = TypeVar("T")


def with_retries(
    fn: Callable[[], T],
    retryable_exceptions: tuple[type[BaseException], ...],
    label: str = "LLM",
) -> T:
    for attempt in range(MAX_RETRIES + 1):
        try:
            return fn()
        except retryable_exceptions as e:
            if attempt == MAX_RETRIES:
                raise
            delay = RETRY_BASE_DELAY * (2 ** attempt)
            logger.warning(
                "%s call attempt %d failed (%s), retrying in %ds",
                label, attempt + 1, type(e).__name__, delay,
            )
            time.sleep(delay)
    raise RuntimeError("Unreachable")
