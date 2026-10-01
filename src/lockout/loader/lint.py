"""Semantic lint: checks that the schema alone cannot express. Pure, no I/O."""

from collections import Counter
from collections.abc import Iterable

from lockout.loader.issues import Issue, Severity
from lockout.schema import Model


def lint_model(model: Model) -> list[Issue]:
    """Return errors (dangling references, duplicates, bad groups) and warnings."""
    issues: list[Issue] = []

    def add(severity: Severity, location: str, message: str) -> None:
        issues.append(Issue(severity, model.name, location, message))

    sections: dict[str, list[str]] = {
        "node": [n.id for n in model.nodes],
        "capability": [c.id for c in model.capabilities],
        "break-glass path": [b.id for b in model.break_glass_paths],
        "redundancy group": [g.id for g in model.redundancy_groups],
    }
    for label, ids in sections.items():
        for item_id, count in Counter(ids).items():
            if count > 1:
                add(Severity.ERROR, f'{label} "{item_id}"', f"duplicate {label} id ({count}x)")

    node_ids = set(sections["node"])
    capability_ids = set(sections["capability"])

    def check_nodes(location: str, field: str, refs: Iterable[str]) -> None:
        for ref in refs:
            if ref not in node_ids:
                add(Severity.ERROR, f'{location}, field "{field}"', f'unknown node "{ref}"')

    for i, edge in enumerate(model.edges):
        where = f"edge #{i} ({edge.source} -> {edge.target})"
        check_nodes(where, "from", [edge.source])
        check_nodes(where, "to", [edge.target])
    for cap in model.capabilities:
        check_nodes(f'capability "{cap.id}"', "requires", cap.requires)
    for path in model.break_glass_paths:
        where = f'break-glass path "{path.id}"'
        check_nodes(where, "requires", path.requires)
        if path.capability not in capability_ids:
            add(
                Severity.ERROR,
                f'{where}, field "capability"',
                f'unknown capability "{path.capability}"',
            )
    for group in model.redundancy_groups:
        where = f'redundancy group "{group.id}"'
        check_nodes(where, "members", group.members)
        if group.min_available >= len(group.members):
            add(
                Severity.ERROR,
                f'{where}, field "min_available"',
                f"must be smaller than the number of members ({len(group.members)}), "
                f"otherwise no member may ever fail",
            )

    for edge_key, count in Counter((e.source, e.target, e.type) for e in model.edges).items():
        if count > 1:
            source, target, edge_type = edge_key
            add(
                Severity.WARNING,
                f"edge ({source} -> {target})",
                f"{edge_type.value} is declared {count} times",
            )

    for cap in model.capabilities:
        if not cap.requires:
            add(
                Severity.WARNING,
                f'capability "{cap.id}"',
                'field "requires" is empty, so no failure can ever make it unreachable',
            )

    referenced = {r for e in model.edges for r in (e.source, e.target)}
    referenced |= {r for c in model.capabilities for r in c.requires}
    referenced |= {r for b in model.break_glass_paths for r in b.requires}
    referenced |= {r for g in model.redundancy_groups for r in g.members}
    for node in model.nodes:
        if node.id not in referenced:
            add(
                Severity.WARNING,
                f'node "{node.id}"',
                "is not used by any edge, capability, break-glass path or redundancy group",
            )

    return issues
