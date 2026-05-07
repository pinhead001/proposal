import json
import logging
import os
import threading
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

DATA_DIR = os.environ.get("PROPOSAL_DATA_DIR", "data")
PROPOSALS_FILE = os.path.join(DATA_DIR, "proposals.json")
ANALYSIS_FILE = os.path.join(DATA_DIR, "analysis.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
MAX_HISTORY = 20

_lock = threading.Lock()


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def save_proposals(texts: list[str]):
    _ensure_dir()
    with _lock:
        with open(PROPOSALS_FILE, "w") as f:
            json.dump(texts, f)
    logger.info("Saved %d proposal texts", len(texts))


def load_proposals() -> list[str]:
    if not os.path.exists(PROPOSALS_FILE):
        return []
    with _lock:
        with open(PROPOSALS_FILE) as f:
            return json.load(f)


def save_analysis(analysis: str):
    _ensure_dir()
    with _lock:
        with open(ANALYSIS_FILE, "w") as f:
            json.dump({"analysis": analysis}, f)


def load_analysis() -> str | None:
    if not os.path.exists(ANALYSIS_FILE):
        return None
    with _lock:
        with open(ANALYSIS_FILE) as f:
            data = json.load(f)
            return data.get("analysis")


def clear_analysis():
    if os.path.exists(ANALYSIS_FILE):
        os.remove(ANALYSIS_FILE)


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
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f)
    return entry_id


def load_history() -> list[dict]:
    with _lock:
        return _load_history_unlocked()


def _load_history_unlocked() -> list[dict]:
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE) as f:
        return json.load(f)
