"""Failure simulation: lockout plus break-glass validity for one failure set."""

from dataclasses import dataclass

from lockout.analyzers.breakglass import BreakGlassVerdict, check_break_glass
from lockout.analyzers.lockout_sim import LockoutResult, simulate_lockout
from lockout.schema import Model


@dataclass(frozen=True)
class SimulationResult:
    lockout: LockoutResult
    break_glass: list[BreakGlassVerdict]
    unrecoverable: list[str]

    @property
    def false_break_glass(self) -> list[BreakGlassVerdict]:
        return [v for v in self.break_glass if not v.valid]


def simulate(model: Model, failed: frozenset[str]) -> SimulationResult:
    """Capabilities that are lost and have no valid break-glass path are unrecoverable."""
    lockout = simulate_lockout(model, failed)
    verdicts = check_break_glass(model, failed)
    rescued = {v.capability for v in verdicts if v.valid}
    unrecoverable = sorted(c.capability for c in lockout.lost if c.capability not in rescued)
    return SimulationResult(lockout, verdicts, unrecoverable)
