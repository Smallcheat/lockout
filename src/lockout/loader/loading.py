"""Load a model from YAML. File access is only in :func:`load_model`."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from lockout.loader.issues import Issue, ModelError, Severity
from lockout.loader.lint import lint_model
from lockout.schema import Model

_SECTION_LABELS = {
    "nodes": "node",
    "edges": "edge",
    "capabilities": "capability",
    "break_glass_paths": "break-glass path",
    "redundancy_groups": "redundancy group",
}


@dataclass(frozen=True)
class LoadedModel:
    model: Model
    warnings: list[Issue]


def load_model(path: Path) -> LoadedModel:
    """Read ``path`` and parse it. Raises :class:`ModelError` on any error."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ModelError(
            [Issue(Severity.ERROR, path.name, "", f"cannot read file: {exc.strerror}")]
        ) from exc
    return parse_model(text, source=path.name)


def parse_model(text: str, source: str = "<string>") -> LoadedModel:
    """Parse YAML text, validate the schema, then lint. Raises :class:`ModelError` on errors."""
    try:
        raw = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ModelError([Issue(Severity.ERROR, source, "", f"invalid YAML: {exc}")]) from exc
    if not isinstance(raw, dict):
        raise ModelError(
            [Issue(Severity.ERROR, source, "", "top level must be a mapping with model fields")]
        )

    name = raw.get("name")
    model_name = name if isinstance(name, str) and name else source
    try:
        model = Model.model_validate(raw)
    except ValidationError as exc:
        raise ModelError(_schema_issues(exc, raw, model_name)) from exc

    found = lint_model(model)
    errors = [i for i in found if i.severity is Severity.ERROR]
    if errors:
        raise ModelError(errors)
    return LoadedModel(model, [i for i in found if i.severity is Severity.WARNING])


def _schema_issues(exc: ValidationError, raw: dict[str, Any], model_name: str) -> list[Issue]:
    issues: list[Issue] = []
    for err in exc.errors():
        loc = list(err["loc"])
        location = ""
        if len(loc) >= 2 and loc[0] in _SECTION_LABELS and isinstance(loc[1], int):
            label = _SECTION_LABELS[str(loc[0])]
            location = _item_label(raw, str(loc[0]), loc[1], label)
            loc = loc[2:]
        field = ".".join(str(p) for p in loc)
        if err["type"] == "extra_forbidden":
            message = f'unknown field "{field}"'
        else:
            message = err["msg"]
            if field:
                location = f'{location}, field "{field}"' if location else f'field "{field}"'
        issues.append(Issue(Severity.ERROR, model_name, location, message))
    return issues


def _item_label(raw: dict[str, Any], section: str, index: int, label: str) -> str:
    items = raw.get(section)
    if isinstance(items, list) and index < len(items):
        item = items[index]
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            return f'{label} "{item["id"]}"'
    return f"{label} #{index}"
