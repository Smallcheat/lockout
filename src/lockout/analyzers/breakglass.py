"""Break-glass validity: does an alternative path survive a failure set?"""

from dataclasses import dataclass

from lockout.graph import ChainLink, build_graph, find_chain
from lockout.schema import Model


@dataclass(frozen=True)
class BreakGlassVerdict:
    """``valid`` is False for a false break-glass; ``chain`` then explains why."""

    path: str
    capability: str
    valid: bool
    chain: list[ChainLink]


def check_break_glass(model: Model, failed: frozenset[str]) -> list[BreakGlassVerdict]:
    """A path is valid when its transitive dependencies do not intersect ``failed``."""
    graph = build_graph(model)
    verdicts: list[BreakGlassVerdict] = []
    for path in model.break_glass_paths:
        chain = find_chain(graph, path.requires, set(failed))
        verdicts.append(BreakGlassVerdict(path.id, path.capability, chain is None, chain or []))
    return verdicts
