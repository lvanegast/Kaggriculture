"""Integration test verifying submission contract and end-to-end execution."""

from pathlib import Path
import pytest
import kaggle_environments as ke

ROOT = Path(__file__).resolve().parent.parent


def test_submission_file_exists():
    sub_file = ROOT / "submission.py"
    assert sub_file.exists(), "submission.py must exist. Run scripts/build_submission.py first."


def test_submission_runs_against_starter():
    sub_file = ROOT / "submission.py"
    env = ke.make("kaggriculture", configuration={"episodeSteps": 48})
    env.run([str(sub_file), "starter"])

    assert len(env.steps) >= 48
    status0 = env.steps[-1][0]["status"]
    status1 = env.steps[-1][1]["status"]
    assert status0 in ("ACTIVE", "DONE")
    assert status1 in ("ACTIVE", "DONE")
