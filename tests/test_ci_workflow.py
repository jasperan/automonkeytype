from pathlib import Path


WORKFLOW_PATH = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "tests.yml"


def test_ci_workflow_covers_required_triggers_and_steps():
    content = WORKFLOW_PATH.read_text()

    for snippet in (
        "push:",
        "pull_request:",
        "workflow_dispatch:",
        "run_live_smoke:",
        "type: boolean",
        "3.10",
        "3.11",
        "3.12",
        "playwright install --with-deps chromium",
        "pytest -v --tb=short",
        "AUTOMONKEYTYPE_RUN_LIVE=1 pytest -v --tb=short tests/test_live_smoke.py",
    ):
        assert snippet in content
