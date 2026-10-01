"""Lockout simulation: which capabilities are lost when a set of nodes fails."""

from dataclasses import dataclass

from lockout.graph import ChainLink, build_graph, dependents_of, find_chain
from lockout.schema import Model


@dataclass(frozen=True)
class LostCapability:
    """A capability that cannot be exercised. ``chain`` runs from a required node to a failure."""

    capability: str
    chain: list[ChainLink]


@dataclass(frozen=True)
class LockoutResult:
    failed: list[str]
    impacted: list[str]
    lost: list[LostCapability]


def simulate_lockout(model: Model, failed: frozenset[str]) -> LockoutResult:
    """Remove ``failed``; every node that depends on them is impacted too.

    A capability is lost when any node it requires is impacted.
    """
    graph = build_graph(model)
    impacted = dependents_of(graph, failed)
    lost: list[LostCapability] = []
    for capability in model.capabilities:
        chain = find_chain(graph, capability.requires, set(failed))
        if chain is not None:
            lost.append(LostCapability(capability.id, chain))
    return LockoutResult(sorted(failed), sorted(impacted), lost)
