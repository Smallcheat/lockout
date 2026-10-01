"""Typed dependency graph. Edge direction: source requires target (source -> target)."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass

import networkx as nx

from lockout.schema import EdgeType, Model


@dataclass(frozen=True)
class ChainLink:
    """One step of a dependency chain. ``via`` is the edge type used to arrive at ``node``."""

    node: str
    via: EdgeType | None = None


def build_graph(model: Model) -> nx.MultiDiGraph[str]:
    """Build a multigraph with one edge per declared dependency, keyed by its type."""
    graph: nx.MultiDiGraph[str] = nx.MultiDiGraph()
    for node in model.nodes:
        graph.add_node(node.id, kind=node.kind, tags=tuple(node.tags))
    for edge in model.edges:
        graph.add_edge(edge.source, edge.target, key=edge.type.value, type=edge.type)
    return graph


def subgraph_by_types(graph: nx.MultiDiGraph[str], types: Iterable[EdgeType]) -> nx.DiGraph[str]:
    """Simple digraph with all nodes but only the edges of the given types."""
    wanted = set(types)
    sub: nx.DiGraph[str] = nx.DiGraph()
    sub.add_nodes_from(graph.nodes)
    for source, target, data in graph.edges(data=True):
        if data["type"] in wanted:
            sub.add_edge(source, target)
    return sub


def dependencies_of(graph: nx.MultiDiGraph[str], nodes: Iterable[str]) -> set[str]:
    """The nodes plus everything they transitively require."""
    result = set(nodes)
    for node in list(result):
        result |= nx.descendants(graph, node)
    return result


def dependents_of(graph: nx.MultiDiGraph[str], nodes: Iterable[str]) -> set[str]:
    """The nodes plus everything that transitively requires them."""
    result = set(nodes)
    for node in list(result):
        result |= nx.ancestors(graph, node)
    return result


def find_chain(
    graph: nx.MultiDiGraph[str], starts: Iterable[str], targets: set[str]
) -> list[ChainLink] | None:
    """Shortest dependency chain from any start node to any target node, or None.

    Breadth-first with sorted neighbours, so the result is deterministic.
    """
    parents: dict[str, ChainLink | None] = {}
    queue: deque[str] = deque()
    for start in sorted(set(starts)):
        parents[start] = None
        queue.append(start)
    while queue:
        node = queue.popleft()
        if node in targets:
            chain: list[ChainLink] = []
            cursor: str | None = node
            while cursor is not None:
                link = parents[cursor]
                chain.append(ChainLink(cursor, link.via if link else None))
                cursor = link.node if link else None
            chain.reverse()
            return chain
        for neighbour in sorted(graph.successors(node)):
            if neighbour not in parents:
                edge_type = min(d["type"] for d in graph[node][neighbour].values())
                parents[neighbour] = ChainLink(node, edge_type)
                queue.append(neighbour)
    return None
