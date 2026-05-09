import json
from pathlib import Path
from unittest.mock import patch
from app.services.storage.proposal_store import (
    save_proposals,
    load_proposals,
    save_analysis,
    load_analysis,
    clear_analysis,
    save_to_history,
    load_history,
)


def test_proposals_roundtrip(tmp_path):
    with patch("app.services.storage.proposal_store.DATA_DIR", tmp_path), \
         patch("app.services.storage.proposal_store.PROPOSALS_FILE", tmp_path / "proposals.json"):
        save_proposals(["proposal 1", "proposal 2"])
        result = load_proposals()
        assert result == ["proposal 1", "proposal 2"]


def test_load_proposals_empty(tmp_path):
    with patch("app.services.storage.proposal_store.PROPOSALS_FILE", tmp_path / "nope.json"):
        assert load_proposals() == []


def test_analysis_roundtrip(tmp_path):
    with patch("app.services.storage.proposal_store.DATA_DIR", tmp_path), \
         patch("app.services.storage.proposal_store.ANALYSIS_FILE", tmp_path / "analysis.json"):
        save_analysis("style analysis text")
        result = load_analysis()
        assert result == "style analysis text"


def test_load_analysis_empty(tmp_path):
    with patch("app.services.storage.proposal_store.ANALYSIS_FILE", tmp_path / "nope.json"):
        assert load_analysis() is None


def test_clear_analysis(tmp_path):
    path = tmp_path / "analysis.json"
    path.write_text(json.dumps({"analysis": "test"}))
    with patch("app.services.storage.proposal_store.ANALYSIS_FILE", path):
        clear_analysis()
        assert not path.exists()


def test_history_roundtrip(tmp_path):
    with patch("app.services.storage.proposal_store.DATA_DIR", tmp_path), \
         patch("app.services.storage.proposal_store.HISTORY_FILE", tmp_path / "history.json"):
        entry_id = save_to_history("rfp text", [{"title": "S1", "content": "C1"}])
        assert entry_id == 1

        history = load_history()
        assert len(history) == 1
        assert history[0]["rfp_preview"] == "rfp text"
        assert len(history[0]["sections"]) == 1
