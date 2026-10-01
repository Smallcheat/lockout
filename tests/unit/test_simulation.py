"""Lockout and break-glass analyses on the hand-built chain fixture."""

from pathlib import Path

from lockout.analyzers import check_break_glass, simulate, simulate_lockout
from lockout.loader import load_model

CHAIN = Path(__file__).parent.parent / "fixtures" / "models" / "chain.yaml"


def test_failed_dependency_loses_dependent_capabilities_only() -> None:
    model = load_model(CHAIN).model
    result = simulate_lockout(model, frozenset({"dns"}))
    assert result.failed == ["dns"]
    assert result.impacted == ["console", "dns", "human", "idp", "vpn"]
    assert [c.capability for c in result.lost] == ["login", "remote"]
    assert [link.node for link in result.lost[0].chain] == ["console", "idp", "dns"]


def test_no_failure_loses_nothing() -> None:
    result = simulate_lockout(load_model(CHAIN).model, frozenset())
    assert result.lost == []
    assert result.impacted == []


def test_false_break_glass_is_flagged_with_chain_and_valid_one_passes() -> None:
    verdicts = {v.path: v for v in check_break_glass(load_model(CHAIN).model, frozenset({"idp"}))}
    assert verdicts["bg-key"].valid
    assert verdicts["bg-key"].chain == []
    false = verdicts["bg-remote"]
    assert not false.valid
    assert [link.node for link in false.chain] == ["human", "vpn", "idp"]


def test_break_glass_is_valid_when_nothing_failed() -> None:
    assert all(v.valid for v in check_break_glass(load_model(CHAIN).model, frozenset()))


def test_unrecoverable_means_lost_without_valid_break_glass() -> None:
    result = simulate(load_model(CHAIN).model, frozenset({"idp"}))
    assert [c.capability for c in result.lockout.lost] == ["login", "remote"]
    assert result.unrecoverable == ["remote"]
    assert [v.path for v in result.false_break_glass] == ["bg-remote"]
