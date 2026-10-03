"""Bootstrap cycle analysis on hand-built models and the reference model."""

from pathlib import Path

from lockout.analyzers import analyze_bootstrap
from lockout.loader import load_model

MODELS = Path(__file__).parent.parent / "fixtures" / "models"
REFERENCE = Path(__file__).parent.parent.parent / "models" / "reference-dc" / "model.yaml"


def test_cycles_include_pairs_and_self_loops_but_not_reach_cycles() -> None:
    result = analyze_bootstrap(load_model(MODELS / "cycle.yaml").model)
    assert result.cycles == [["a", "b"], ["d"]]
    assert not result.has_valid_start_order


def test_cycle_members_share_a_tier_and_dependents_come_later() -> None:
    order = analyze_bootstrap(load_model(MODELS / "cycle.yaml").model).order
    tier_of = {n: i for i, tier in enumerate(order) for n in tier}
    assert tier_of["a"] == tier_of["b"]
    assert tier_of["c"] > tier_of["a"]


def test_acyclic_model_has_start_order_with_dependencies_first() -> None:
    result = analyze_bootstrap(load_model(MODELS / "chain.yaml").model)
    assert result.cycles == []
    assert result.has_valid_start_order
    tier_of = {n: i for i, tier in enumerate(result.order) for n in tier}
    assert tier_of["dns"] < tier_of["idp"] < tier_of["console"]


def test_reference_model_has_no_bootstrap_cycle() -> None:
    """Replaces the temporary guard from PR 3: the reference model must be bootstrappable."""
    result = analyze_bootstrap(load_model(REFERENCE).model)
    assert result.cycles == []
