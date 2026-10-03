"""Command line interface. Reads files, calls the pure analyzers, prints text."""

from pathlib import Path
from typing import Annotated

import typer

from lockout.analyzers import (
    BootstrapResult,
    GroupFinding,
    SimulationResult,
    analyze_bootstrap,
    check_redundancy,
    simulate,
)
from lockout.graph import ChainLink
from lockout.loader import ModelError, load_model
from lockout.scenarios import load_scenario, resolve_failure_set
from lockout.schema import Model

app = typer.Typer(add_completion=False, no_args_is_help=True, help="Recovery-lockout analyzer.")

ModelArg = Annotated[Path, typer.Argument(help="Model YAML file.", dir_okay=False)]
ScenarioArg = Annotated[Path, typer.Argument(help="Scenario YAML file.", dir_okay=False)]


def format_chain(chain: list[ChainLink]) -> str:
    parts = [chain[0].node]
    for link in chain[1:]:
        parts.append(f"-[{link.via.value if link.via else '?'}]-> {link.node}")
    return " ".join(parts)


def render_analysis(model: Model, result: BootstrapResult, groups: list[GroupFinding]) -> str:
    lines = [f"Model: {model.name} ({len(model.nodes)} nodes, {len(model.edges)} edges)", ""]
    if result.cycles:
        lines.append(f"Bootstrap cycles: {len(result.cycles)}")
        lines += [f"  - {' <-> '.join(c)}" for c in result.cycles]
        lines.append("No valid start order exists while these cycles remain.")
    else:
        lines.append("Bootstrap cycles: none")
        lines.append("Start order (each tier needs only earlier tiers):")
        lines += [f"  {i}: {', '.join(tier)}" for i, tier in enumerate(result.order)]
    if groups:
        lines += ["", "Redundancy groups:"]
        for g in groups:
            head = f"  - {g.group} (needs {g.min_available} of {len(g.members)})"
            if g.is_false_redundancy:
                points = ", ".join(p.node for p in g.single_points)
                lines.append(f"{head}: FALSE REDUNDANCY, single points of failure: {points}")
            else:
                lines.append(f"{head}: no single point of failure")
    return "\n".join(lines) + "\n"


def render_simulation(name: str, result: SimulationResult) -> str:
    lockout = result.lockout
    lines = [
        f"Scenario: {name}",
        f"Failed: {', '.join(lockout.failed)}",
        f"Impacted nodes (failed or dependent on failed): {len(lockout.impacted)}",
        "",
    ]
    if lockout.lost:
        lines.append(f"Lost capabilities: {len(lockout.lost)}")
        lines += [f"  - {c.capability}: {format_chain(c.chain)}" for c in lockout.lost]
    else:
        lines.append("Lost capabilities: none")
    lines += ["", "Break-glass paths:"]
    for v in result.break_glass:
        if v.valid:
            lines.append(f"  - {v.path} ({v.capability}): valid")
        else:
            lines.append(
                f"  - {v.path} ({v.capability}): FALSE BREAK-GLASS, {format_chain(v.chain)}"
            )
    if result.redundancy:
        lines += ["", "Redundancy groups:"]
        for g in result.redundancy:
            state = "ok" if g.satisfied else "NOT SATISFIED"
            lines.append(
                f"  - {g.group}: {len(g.available)} of {len(g.members)} available, "
                f"needs {g.required}: {state}"
            )
    lines.append("")
    if result.unrecoverable:
        lines.append(
            f"Unrecoverable (lost, no valid break-glass): {', '.join(result.unrecoverable)}"
        )
    else:
        lines.append("Unrecoverable: none")
    return "\n".join(lines) + "\n"


def _fail(exc: ModelError) -> typer.Exit:
    typer.echo(str(exc), err=True)
    return typer.Exit(code=2)


@app.command()
def analyze(model_path: ModelArg) -> None:
    """Report bootstrap cycles and the start order of a model."""
    try:
        model = load_model(model_path).model
    except ModelError as exc:
        raise _fail(exc) from exc
    typer.echo(render_analysis(model, analyze_bootstrap(model), check_redundancy(model)), nl=False)


@app.command(name="simulate")
def simulate_command(model_path: ModelArg, scenario_path: ScenarioArg) -> None:
    """Simulate a failure scenario: lost capabilities and break-glass validity."""
    try:
        model = load_model(model_path).model
        scenario = load_scenario(scenario_path)
        failed = resolve_failure_set(model, scenario)
    except ModelError as exc:
        raise _fail(exc) from exc
    typer.echo(render_simulation(scenario.name, simulate(model, failed)), nl=False)
