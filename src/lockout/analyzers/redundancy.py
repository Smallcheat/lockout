"""Redundancy groups: shared single points of failure and group state under a failure set."""

from dataclasses import dataclass

from lockout.graph import ChainLink, build_graph, dependents_of, find_chain
from lockout.schema import Model


@dataclass(frozen=True)
class SinglePoint:
    """One node whose failure leaves fewer than ``min_available`` members of a group.

    ``chains`` holds, per impacted member, the dependency chain from the member to the node.
    """

    node: str
    impacted: list[str]
    chains: list[tuple[str, list[ChainLink]]]


@dataclass(frozen=True)
class GroupFinding:
    group: str
    members: list[str]
    min_available: int
    single_points: list[SinglePoint]

    @property
    def is_false_redundancy(self) -> bool:
        """True when a single failure defeats the group, so the redundancy exists on paper."""
        return bool(self.single_points)


@dataclass(frozen=True)
class GroupStatus:
    group: str
    members: list[str]
    available: list[str]
    required: int

    @property
    def satisfied(self) -> bool:
        return len(self.available) >= self.required


def check_redundancy(model: Model) -> list[GroupFinding]:
    """For each group, find every node whose single failure leaves too few members.

    Failing a member itself is covered too: it counts only if other members depend on it.
    """
    graph = build_graph(model)
    findings: list[GroupFinding] = []
    for group in model.redundancy_groups:
        members = set(group.members)
        points: list[SinglePoint] = []
        for node in sorted(graph.nodes):
            impacted = sorted(members & dependents_of(graph, [node]))
            if len(members) - len(impacted) >= group.min_available:
                continue
            chains: list[tuple[str, list[ChainLink]]] = []
            for member in impacted:
                chain = find_chain(graph, [member], {node})
                if chain is not None:
                    chains.append((member, chain))
            points.append(SinglePoint(node, impacted, chains))
        findings.append(GroupFinding(group.id, sorted(members), group.min_available, points))
    return findings


def evaluate_groups(model: Model, failed: frozenset[str]) -> list[GroupStatus]:
    """Members still available under ``failed`` and whether ``min_available`` holds."""
    graph = build_graph(model)
    impacted = dependents_of(graph, failed)
    return [
        GroupStatus(
            g.id,
            sorted(g.members),
            sorted(m for m in g.members if m not in impacted),
            g.min_available,
        )
        for g in model.redundancy_groups
    ]
