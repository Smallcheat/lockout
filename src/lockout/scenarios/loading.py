"""Load scenarios and resolve their failure set against a model."""

from pathlib import Path

import yaml
from pydantic import ValidationError

from lockout.loader import Issue, ModelError, Severity
from lockout.scenarios.model import Scenario
from lockout.schema import Model

_SUBJECT = "scenario"


def load_scenario(path: Path) -> Scenario:
    """Read ``path`` and parse it. Raises :class:`ModelError` on any error."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ModelError(
            [Issue(Severity.ERROR, path.name, "", f"cannot read file: {exc.strerror}", _SUBJECT)]
        ) from exc
    return parse_scenario(text, source=path.name)


def parse_scenario(text: str, source: str = "<string>") -> Scenario:
    """Parse YAML text into a :class:`Scenario`. Raises :class:`ModelError` on errors."""
    try:
        raw = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ModelError(
            [Issue(Severity.ERROR, source, "", f"invalid YAML: {exc}", _SUBJECT)]
        ) from exc
    if not isinstance(raw, dict):
        raise ModelError(
            [Issue(Severity.ERROR, source, "", "top level must be a mapping", _SUBJECT)]
        )
    name = raw.get("name")
    label = name if isinstance(name, str) and name else source
    try:
        return Scenario.model_validate(raw)
    except ValidationError as exc:
        issues = []
        for err in exc.errors():
            field = ".".join(str(p) for p in err["loc"])
            message = f'unknown field "{field}"' if err["type"] == "extra_forbidden" else err["msg"]
            location = f'field "{field}"' if field and err["type"] != "extra_forbidden" else ""
            issues.append(Issue(Severity.ERROR, label, location, message, _SUBJECT))
        raise ModelError(issues) from exc


def resolve_failure_set(model: Model, scenario: Scenario) -> frozenset[str]:
    """Union of the named nodes and the nodes matched by the tag selector.

    Raises :class:`ModelError` for unknown nodes, a selector that matches nothing, or an
    empty failure set.
    """
    known = {n.id for n in model.nodes}
    issues: list[Issue] = []

    def error(location: str, message: str) -> None:
        issues.append(Issue(Severity.ERROR, scenario.name, location, message, _SUBJECT))

    failed: set[str] = set()
    for node_id in scenario.failed.nodes:
        if node_id in known:
            failed.add(node_id)
        else:
            error('field "failed.nodes"', f'unknown node "{node_id}" in model "{model.name}"')
    selector = scenario.failed.select
    if selector is not None:
        wanted = set(selector.tags_all)
        matched = {n.id for n in model.nodes if wanted <= set(n.tags)}
        if not matched:
            error(
                'field "failed.select.tags_all"',
                f'no node in model "{model.name}" carries all tags {sorted(wanted)}',
            )
        failed |= matched
    if not failed and not issues:
        error('field "failed"', "the failure set is empty; name nodes or give a tag selector")
    if issues:
        raise ModelError(issues)
    return frozenset(failed)
