"""Bootstrap analysis: cycles in the start and authenticate dependencies."""

from dataclasses import dataclass

import networkx as nx

from lockout.graph import build_graph, subgraph_by_types
from lockout.schema import EdgeType, Model

BOOTSTRAP_EDGE_TYPES = (EdgeType.START, EdgeType.AUTHENTICATE)


@dataclass(frozen=True)
class BootstrapResult:
    """``cycles`` lists strongly connected groups (sorted); ``order`` lists start tiers.

    Tier 0 needs nothing from the others and starts first. When cycles exist, every cycle is
    one tier of its own, and the order shows only how the rest depends on it.
    """

    cycles: list[list[str]]
    order: list[list[str]]

    @property
    def has_valid_start_order(self) -> bool:
        return not self.cycles


def analyze_bootstrap(model: Model) -> BootstrapResult:
    """Find bootstrap cycles (SCCs larger than one node, or a node requiring itself)."""
    sub = subgraph_by_types(build_graph(model), BOOTSTRAP_EDGE_TYPES)
    components = [sorted(c) for c in nx.strongly_connected_components(sub)]
    cycles = sorted(c for c in components if len(c) > 1 or sub.has_edge(c[0], c[0]))

    condensed = nx.condensation(sub)
    # Edges point from dependents to dependencies, so reverse them: dependencies come first.
    tiers: list[list[str]] = []
    for generation in nx.topological_generations(condensed.reverse(copy=False)):
        members = sorted(n for c in generation for n in condensed.nodes[c]["members"])
        tiers.append(members)
    return BootstrapResult(cycles=cycles, order=tiers)
