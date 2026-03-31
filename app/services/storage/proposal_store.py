import json
import os
import logging

logger = logging.getLogger(__name__)

STORE_DIR = os.environ.get("PROPOSAL_STORE_DIR", "data/proposals")
PROPOSALS_FILE = os.path.join(STORE_DIR, "proposals.json")
ANALYSIS_FILE = os.path.join(STORE_DIR, "analysis.json")


def _ensure_dir():
    os.makedirs(STORE_DIR, exist_ok=True)


def save_proposals(texts: list[str]):
    _ensure_dir()
    data = {"proposals": texts}
    with open(PROPOSALS_FILE, "w") as f:
        json.dump(data, f, indent=2)
    logger.info("Saved %d proposals to store", len(texts))


def load_proposals() -> list[str]:
    if not os.path.exists(PROPOSALS_FILE):
        return []
    with open(PROPOSALS_FILE) as f:
        data = json.load(f)
    return data.get("proposals", [])


def save_analysis(analysis: str):
    _ensure_dir()
    with open(ANALYSIS_FILE, "w") as f:
        json.dump({"analysis": analysis}, f, indent=2)
    logger.info("Cached style analysis to store")


def load_analysis() -> str | None:
    if not os.path.exists(ANALYSIS_FILE):
        return None
    with open(ANALYSIS_FILE) as f:
        data = json.load(f)
    return data.get("analysis")


def clear_analysis():
    if os.path.exists(ANALYSIS_FILE):
        os.remove(ANALYSIS_FILE)
