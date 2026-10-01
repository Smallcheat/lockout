"""Schema tests: valid models parse, tags exist, the JSON Schema file is up to date."""

import json

import pytest
from pydantic import ValidationError

from lockout.schema import EdgeType, Model
from lockout.schema.export import SCHEMA_FILE, model_json_schema_text


def _model(**extra: object) -> dict[str, object]:
    return {"name": "m", "nodes": [{"id": "a", "kind": "x"}], **extra}


def test_node_tags_default_to_empty_and_are_kept() -> None:
    model = Model.model_validate(
        _model(nodes=[{"id": "a", "kind": "x"}, {"id": "b", "kind": "x", "tags": ["os:windows"]}])
    )
    assert model.nodes[0].tags == []
    assert model.nodes[1].tags == ["os:windows"]


def test_edge_uses_from_and_to_keys() -> None:
    model = Model.model_validate(
        _model(edges=[{"from": "a", "to": "b", "type": "requires_to_reach"}])
    )
    assert model.edges[0].source == "a"
    assert model.edges[0].target == "b"
    assert model.edges[0].type is EdgeType.REACH


def test_there_are_exactly_four_edge_types() -> None:
    assert {t.value for t in EdgeType} == {
        "requires_to_start",
        "requires_to_authenticate",
        "requires_to_reach",
        "requires_to_authorize",
    }


@pytest.mark.parametrize(
    "bad",
    [
        _model(edges=[{"from": "a", "to": "b", "type": "crash_coupled"}]),
        _model(nodes=[{"id": "A B", "kind": "x"}]),
        _model(nodes=[{"id": "a", "kind": "x", "tags": ["Bad Tag"]}]),
        _model(nodes=[{"id": "a", "kind": "x", "colour": "red"}]),
        _model(nodes=[]),
        _model(redundancy_groups=[{"id": "g", "members": ["a"]}]),
    ],
)
def test_invalid_models_are_rejected(bad: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        Model.model_validate(bad)


def test_committed_json_schema_matches_models() -> None:
    assert SCHEMA_FILE.read_text(encoding="utf-8") == model_json_schema_text(), (
        "Schema changed: run `python -m lockout.schema.export` and explain it in the PR."
    )
    assert json.loads(model_json_schema_text())["title"] == "Model"
