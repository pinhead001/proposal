import json
import logging
import threading
from pathlib import Path
from datetime import datetime, timezone
from typing import Callable

import os

logger = logging.getLogger(__name__)

DATA_DIR = Path(os.environ.get("PROPOSAL_DATA_DIR", "data"))
PROPOSALS_FILE = DATA_DIR / "proposals.json"
ANALYSIS_FILE = DATA_DIR / "analysis.json"
HISTORY_FILE = DATA_DIR / "history.json"
MAX_HISTORY = 20

_lock = threading.Lock()


def _ensure_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def save_proposals(texts: list[str]) -> None:
    _ensure_dir()
    with _lock:
        try:
            PROPOSALS_FILE.write_text(json.dumps(texts))
        except OSError as e:
            logger.error("Failed to save proposals: %s", e)
            raise
    logger.info("Saved %d proposal texts", len(texts))


def load_proposals() -> list[str]:
    if not PROPOSALS_FILE.exists():
        return []
    with _lock:
        try:
            return json.loads(PROPOSALS_FILE.read_text())
        except (json.JSONDecodeError, OSError) as e:
            logger.error("Failed to load proposals: %s", e)
            return []


def save_analysis(analysis: str) -> None:
    _ensure_dir()
    with _lock:
        try:
            ANALYSIS_FILE.write_text(json.dumps({"analysis": analysis}))
        except OSError as e:
            logger.error("Failed to save analysis: %s", e)
            raise


def load_analysis() -> str | None:
    if not ANALYSIS_FILE.exists():
        return None
    with _lock:
        try:
            data = json.loads(ANALYSIS_FILE.read_text())
            return data.get("analysis")
        except (json.JSONDecodeError, OSError) as e:
            logger.error("Failed to load analysis: %s", e)
            return None


def clear_analysis() -> None:
    try:
        ANALYSIS_FILE.unlink(missing_ok=True)
    except OSError as e:
        logger.error("Failed to clear analysis cache: %s", e)


def save_to_history(rfp_text: str, sections: list[dict]) -> int:
    _ensure_dir()
    with _lock:
        history = _load_history_unlocked()
        entry_id = len(history) + 1
        history.append({
            "id": entry_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rfp_preview": rfp_text[:200],
            "rfp_text": rfp_text,
            "sections": sections,
        })
        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]
        try:
            HISTORY_FILE.write_text(json.dumps(history))
        except OSError as e:
            logger.error("Failed to save history: %s", e)
            raise
    return entry_id


def load_history() -> list[dict]:
    with _lock:
        return _load_history_unlocked()


def _load_history_unlocked() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text())
    except (json.JSONDecodeError, OSError) as e:
        logger.error("Failed to load history: %s", e)
        return []
