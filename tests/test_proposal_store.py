import os
import tempfile
from unittest.mock import patch
from app.services.storage.proposal_store import (
    save_proposals,
    load_proposals,
    save_analysis,
    load_analysis,
    clear_analysis,
)


def test_save_and_load_proposals():
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("app.services.storage.proposal_store.STORE_DIR", tmpdir), \
             patch("app.services.storage.proposal_store.PROPOSALS_FILE", os.path.join(tmpdir, "proposals.json")):
            save_proposals(["proposal 1", "proposal 2"])
            result = load_proposals()
            assert result == ["proposal 1", "proposal 2"]


def test_load_proposals_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("app.services.storage.proposal_store.PROPOSALS_FILE", os.path.join(tmpdir, "nonexistent.json")):
            result = load_proposals()
            assert result == []


def test_save_and_load_analysis():
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("app.services.storage.proposal_store.STORE_DIR", tmpdir), \
             patch("app.services.storage.proposal_store.ANALYSIS_FILE", os.path.join(tmpdir, "analysis.json")):
            save_analysis("tone is formal")
            result = load_analysis()
            assert result == "tone is formal"


def test_load_analysis_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("app.services.storage.proposal_store.ANALYSIS_FILE", os.path.join(tmpdir, "nonexistent.json")):
            result = load_analysis()
            assert result is None


def test_clear_analysis():
    with tempfile.TemporaryDirectory() as tmpdir:
        analysis_file = os.path.join(tmpdir, "analysis.json")
        with patch("app.services.storage.proposal_store.STORE_DIR", tmpdir), \
             patch("app.services.storage.proposal_store.ANALYSIS_FILE", analysis_file):
            save_analysis("cached analysis")
            assert os.path.exists(analysis_file)
            clear_analysis()
            assert not os.path.exists(analysis_file)
