"""Loader tests: valid fixture loads, invalid fixtures give readable errors."""

from pathlib import Path

import pytest

from lockout.loader import ModelError, load_model, parse_model

FIXTURES = Path(__file__).parent.parent / "fixtures" / "models"


def test_valid_minimal_model_loads_without_warnings() -> None:
    loaded = load_model(FIXTURES / "valid-minimal.yaml")
    assert loaded.model.name == "minimal"
    assert [n.id for n in loaded.model.nodes] == ["idp", "vault", "keysafe"]
    assert loaded.warnings == []


@pytest.mark.parametrize(
    ("fixture", "expected"),
    [
        ("missing-kind.yaml", ['model "broken"', 'node "idp"', 'field "kind"']),
        ("unknown-edge-type.yaml", ['model "broken"', "edge #0", 'field "type"']),
        (
            "dangling.yaml",
            [
                'edge #0 (a -> ghost), field "to": unknown node "ghost"',
                'capability "cap", field "requires": unknown node "phantom"',
                'break-glass path "bg", field "capability": unknown capability "nocap"',
            ],
        ),
        ("duplicates.yaml", ['node "a": duplicate node id (2x)']),
    ],
)
def test_invalid_fixtures_report_model_item_and_field(fixture: str, expected: list[str]) -> None:
    with pytest.raises(ModelError) as info:
        load_model(FIXTURES / "invalid" / fixture)
    message = str(info.value)
    for part in expected:
        assert part in message


def test_unknown_field_is_named() -> None:
    with pytest.raises(ModelError, match='node "a".*unknown field "colour"'):
        parse_model("name: m\nnodes:\n  - {id: a, kind: x, colour: red}\n")


def test_non_mapping_and_invalid_yaml_are_reported() -> None:
    with pytest.raises(ModelError, match="top level must be a mapping"):
        parse_model("- just\n- a list\n", source="list.yaml")
    with pytest.raises(ModelError, match="invalid YAML"):
        parse_model("name: [unclosed\n", source="bad.yaml")


def test_missing_file_is_reported(tmp_path: Path) -> None:
    with pytest.raises(ModelError, match="cannot read file"):
        load_model(tmp_path / "nope.yaml")


def test_model_name_falls_back_to_source() -> None:
    with pytest.raises(ModelError, match='model "anon.yaml"'):
        parse_model("nodes: []\n", source="anon.yaml")
