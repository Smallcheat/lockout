"""Scenario parsing and failure-set resolution, including the tag selector."""

from pathlib import Path

import pytest

from lockout.loader import ModelError, load_model
from lockout.scenarios import parse_scenario, resolve_failure_set

CHAIN = Path(__file__).parent.parent / "fixtures" / "models" / "chain.yaml"


def _resolve(text: str) -> frozenset[str]:
    return resolve_failure_set(load_model(CHAIN).model, parse_scenario(text))


def test_names_and_selector_are_unioned() -> None:
    failed = _resolve(
        "name: s\nfailed:\n  nodes: [dns]\n  select:\n    tags_all: [os:windows, agent:edr]\n"
    )
    assert failed == {"dns", "console"}


def test_selector_requires_all_tags() -> None:
    assert _resolve("name: s\nfailed:\n  select:\n    tags_all: [os:windows]\n") == {
        "console",
        "vpn",
    }


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("name: s\nfailed:\n  nodes: [ghost]\n", 'unknown node "ghost" in model "chain"'),
        ("name: s\nfailed:\n  select:\n    tags_all: [os:solaris]\n", "carries all tags"),
        ("name: s\nfailed: {}\n", "the failure set is empty"),
    ],
)
def test_unresolvable_scenarios_name_scenario_and_problem(text: str, expected: str) -> None:
    with pytest.raises(ModelError, match=expected) as info:
        _resolve(text)
    assert 'scenario "s"' in str(info.value)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("name: s\n", 'scenario "s", field "failed": Field required'),
        ("name: s\nfailed:\n  select:\n    tags_all: []\n", 'field "failed.select.tags_all"'),
        ("name: s\nfailed:\n  nodes: [a]\n  colour: red\n", 'unknown field "failed.colour"'),
        ("- list\n", "top level must be a mapping"),
        ("name: [broken\n", "invalid YAML"),
    ],
)
def test_invalid_scenarios_give_readable_errors(text: str, expected: str) -> None:
    with pytest.raises(ModelError, match=expected):
        parse_scenario(text)
