"""Semantic lint tests on small hand-built models."""

import yaml

from lockout.loader import Severity, lint_model, parse_model
from lockout.schema import Model

BASE = """\
name: m
nodes:
  - {id: a, kind: x}
  - {id: b, kind: x}
"""


def _lint(extra: str) -> list[str]:
    # parse_model raises on lint errors, so build the Model through the schema only.
    return [str(i) for i in lint_model(Model.model_validate(yaml.safe_load(BASE + extra)))]


def test_duplicate_ids_in_every_section() -> None:
    out = _lint(
        "capabilities:\n  - {id: c, requires: [a]}\n  - {id: c, requires: [b]}\n"
        "redundancy_groups:\n  - {id: g, members: [a, b]}\n  - {id: g, members: [a, b]}\n"
    )
    assert any('capability "c": duplicate capability id' in m for m in out)
    assert any('redundancy group "g": duplicate redundancy group id' in m for m in out)


def test_redundancy_group_must_allow_a_failure() -> None:
    out = _lint("redundancy_groups:\n  - {id: g, members: [a, b], min_available: 2}\n")
    assert any('redundancy group "g", field "min_available"' in m for m in out)


def test_unknown_group_member_is_dangling() -> None:
    out = _lint("redundancy_groups:\n  - {id: g, members: [a, zzz]}\n")
    assert any('field "members": unknown node "zzz"' in m for m in out)


def test_warnings_for_duplicate_edge_empty_capability_and_orphan() -> None:
    out = _lint(
        "edges:\n  - {from: a, to: b, type: requires_to_start}\n"
        "  - {from: a, to: b, type: requires_to_start}\n"
        "capabilities:\n  - {id: c}\n"
    )
    assert any("requires_to_start is declared 2 times" in m for m in out)
    assert any('capability "c": field "requires" is empty' in m for m in out)
    assert all(m.startswith("warning") for m in out)


def test_orphan_node_is_a_warning() -> None:
    loaded = parse_model(BASE + "capabilities:\n  - {id: c, requires: [a]}\n")
    assert [str(w) for w in loaded.warnings] == [
        'warning: model "m", node "b": is not used by any edge, capability, '
        "break-glass path or redundancy group"
    ]
    assert loaded.warnings[0].severity is Severity.WARNING
