"""The reference model loads cleanly and keeps its intended shape."""

from collections import Counter
from pathlib import Path

from lockout.analyzers import simulate
from lockout.loader import load_model
from lockout.schema import EdgeType

REFERENCE = Path(__file__).parent.parent.parent / "models" / "reference-dc" / "model.yaml"


def test_reference_model_loads_without_warnings() -> None:
    loaded = load_model(REFERENCE)
    assert loaded.warnings == []


def test_reference_model_size_and_coverage() -> None:
    model = load_model(REFERENCE).model
    assert 40 <= len(model.nodes) <= 60
    assert {e.type for e in model.edges} == set(EdgeType)
    assert len({n.kind for n in model.nodes}) >= 20
    assert len(model.capabilities) >= 8
    assert {b.capability for b in model.break_glass_paths} <= {c.id for c in model.capabilities}
    assert model.redundancy_groups


def test_reference_model_has_common_mode_tags() -> None:
    tags = Counter(t for n in load_model(REFERENCE).model.nodes for t in n.tags)
    assert tags["agent:edr"] >= 3
    assert tags["os:windows"] >= 3


def test_directory_failure_makes_onsite_engineer_break_glass_paths_false() -> None:
    """The on-site engineer's entry is authorized by access control, which needs the directory.

    The tool reports this finding; the model is not edited to hide it.
    """
    model = load_model(REFERENCE).model
    result = simulate(model, frozenset({"directory-service"}))
    false_paths = {v.path for v in result.false_break_glass}
    assert {"bg-console-local-account", "bg-physical-key", "bg-offline-restore"} <= false_paths
    assert "bg-emergency-approval" not in false_paths
