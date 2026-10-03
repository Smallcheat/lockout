"""Redundancy group analysis on a hand-built fixture."""

from pathlib import Path

from lockout.analyzers import check_redundancy, evaluate_groups, simulate
from lockout.loader import load_model

MODELS = Path(__file__).parent.parent / "fixtures" / "models"


def _findings() -> dict[str, list[str]]:
    model = load_model(MODELS / "redundancy.yaml").model
    return {f.group: [p.node for p in f.single_points] for f in check_redundancy(model)}


def test_shared_dependency_is_a_single_point_and_independent_group_is_clean() -> None:
    findings = _findings()
    assert findings["shared"] == ["s"]
    assert findings["independent"] == []


def test_min_available_decides_what_counts_as_a_single_point() -> None:
    """x takes down c1 and c2, leaving 1 of 3 (needs 2). y takes down only c1, leaving 2."""
    findings = _findings()
    assert findings["quorum"] == ["x"]


def test_single_point_lists_impacted_members_with_chains() -> None:
    model = load_model(MODELS / "redundancy.yaml").model
    shared = next(f for f in check_redundancy(model) if f.group == "shared")
    assert shared.is_false_redundancy
    point = shared.single_points[0]
    assert point.impacted == ["a1", "a2"]
    assert [(m, [link.node for link in chain]) for m, chain in point.chains] == [
        ("a1", ["a1", "s"]),
        ("a2", ["a2", "s"]),
    ]


def test_group_status_under_failure_set() -> None:
    model = load_model(MODELS / "redundancy.yaml").model
    status = {s.group: s for s in evaluate_groups(model, frozenset({"p1"}))}
    assert status["shared"].available == ["a2"]
    assert status["shared"].satisfied
    status = {s.group: s for s in evaluate_groups(model, frozenset({"s"}))}
    assert status["shared"].available == []
    assert not status["shared"].satisfied
    assert status["independent"].satisfied


def test_quorum_group_is_not_satisfied_when_too_few_members_remain() -> None:
    model = load_model(MODELS / "redundancy.yaml").model
    status = {s.group: s for s in evaluate_groups(model, frozenset({"y"}))}
    assert status["quorum"].available == ["c2", "c3"]
    assert status["quorum"].satisfied
    status = {s.group: s for s in evaluate_groups(model, frozenset({"x"}))}
    assert status["quorum"].available == ["c3"]
    assert not status["quorum"].satisfied


def test_simulation_result_includes_redundancy_status() -> None:
    result = simulate(load_model(MODELS / "redundancy.yaml").model, frozenset({"s"}))
    assert [s.group for s in result.redundancy if not s.satisfied] == ["shared"]


def test_models_without_groups_report_nothing() -> None:
    model = load_model(MODELS / "chain.yaml").model
    assert check_redundancy(model) == []
    assert evaluate_groups(model, frozenset({"dns"})) == []
