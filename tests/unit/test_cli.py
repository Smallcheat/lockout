"""CLI tests plus golden output on the reference model. Golden files change only on purpose."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from lockout.cli import app

ROOT = Path(__file__).parent.parent.parent
REFERENCE = ROOT / "models" / "reference-dc" / "model.yaml"
FIXTURES = ROOT / "tests" / "fixtures" / "models"
GOLDEN = ROOT / "tests" / "golden"

runner = CliRunner()


def test_analyze_reference_model_matches_golden() -> None:
    result = runner.invoke(app, ["analyze", str(REFERENCE)])
    assert result.exit_code == 0
    assert result.output == (GOLDEN / "analyze-reference-dc.txt").read_text(encoding="utf-8")


@pytest.mark.parametrize("scenario", ["idp-primary-down", "edr-content-update-failure"])
def test_simulate_reference_scenarios_match_golden(scenario: str) -> None:
    result = runner.invoke(
        app, ["simulate", str(REFERENCE), str(ROOT / "scenarios" / f"{scenario}.yaml")]
    )
    assert result.exit_code == 0
    assert result.output == (GOLDEN / f"simulate-{scenario}.txt").read_text(encoding="utf-8")


def test_analyze_reports_cycles_without_failing() -> None:
    result = runner.invoke(app, ["analyze", str(FIXTURES / "cycle.yaml")])
    assert result.exit_code == 0
    assert "  - a <-> b" in result.output
    assert "No valid start order exists" in result.output


def test_invalid_model_exits_with_code_2_and_readable_error() -> None:
    result = runner.invoke(app, ["analyze", str(FIXTURES / "invalid" / "missing-kind.yaml")])
    assert result.exit_code == 2
    assert 'node "idp"' in result.output


def test_simulate_with_unknown_node_exits_with_code_2(tmp_path: Path) -> None:
    scenario = tmp_path / "s.yaml"
    scenario.write_text("name: s\nfailed:\n  nodes: [ghost]\n", encoding="utf-8")
    result = runner.invoke(app, ["simulate", str(REFERENCE), str(scenario)])
    assert result.exit_code == 2
    assert 'unknown node "ghost"' in result.output
