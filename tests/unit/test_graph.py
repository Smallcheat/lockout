"""Graph helper tests on the hand-built chain fixture."""

from pathlib import Path

from lockout.graph import build_graph, dependencies_of, dependents_of, find_chain
from lockout.loader import load_model
from lockout.schema import EdgeType

CHAIN = Path(__file__).parent.parent / "fixtures" / "models" / "chain.yaml"


def test_dependencies_and_dependents_are_transitive() -> None:
    graph = build_graph(load_model(CHAIN).model)
    assert dependencies_of(graph, ["console"]) == {"console", "idp", "dns"}
    assert dependents_of(graph, ["dns"]) == {"dns", "idp", "console", "vpn", "human"}


def test_find_chain_is_shortest_and_typed() -> None:
    graph = build_graph(load_model(CHAIN).model)
    chain = find_chain(graph, ["human"], {"dns"})
    assert chain is not None
    assert [(link.node, link.via) for link in chain] == [
        ("human", None),
        ("vpn", EdgeType.REACH),
        ("idp", EdgeType.AUTHENTICATE),
        ("dns", EdgeType.START),
    ]
    assert find_chain(graph, ["keysafe"], {"dns"}) is None
