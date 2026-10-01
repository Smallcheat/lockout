# Architecture

Lockout analyzes a data center's management plane as a typed dependency graph. It answers one question: *if these components fail, can operators still recover?*

This document describes the planned architecture. Components are added in later PRs; see the status column.

## Concepts

See [glossary.md](glossary.md) for definitions. In short: a **node** is a component, an **edge** is a typed dependency, a **capability** is something operators need in order to recover, and a **break-glass path** is a conditional alternative route to a capability. A break-glass path whose transitive dependencies intersect the failed set is a **false break-glass**.

## Data flow

```
 models/*.yaml ──┐                      assumptions/assumptions.yaml
 scenarios/*.yaml┤                                   │
                 ▼                                   ▼
        ┌──────────────────┐   errors     ┌───────────────────┐
        │ Loader+Validator │────────────► │ CLI / CI gate     │
        └────────┬─────────┘              └───────────────────┘
                 ▼
        ┌──────────────────┐
        │ Typed graph      │
        └────────┬─────────┘
   ┌─────────────┼──────────────┬───────────────┐
   ▼             ▼              ▼               ▼
 Bootstrap/   Lockout       Break-glass     Recovery-time
 cycle        simulator     validity        Monte Carlo
 analyzer                   checker
   └─────────────┴──────┬───────┴───────────────┘
                        ▼
              ┌───────────────────┐
              │ Reporter          │  JSON / Markdown
              └─────────┬─────────┘
                        ▼
                CLI · API (read-only) · CI
```

## Components

| Component | Responsibility | I/O | Planned in |
|---|---|---|---|
| `schema` | Data types for node, edge, capability, break-glass path, scenario | none | PR 3 |
| `loader` | Read YAML, validate schema, semantic lint (dangling references, duplicates, unknown types) | files | PR 4 |
| `graph` | Build the typed graph, answer reachability queries | none | PR 5 |
| `analyzers` | Bootstrap cycles, lockout simulation, break-glass validity, recovery-time Monte Carlo | none | PR 5 onward |
| `scenarios` | Load scenarios, resolve the failure set (names and tag selector) | files | PR 7 |
| `report` | Render results as JSON and Markdown | none | PR 8 |
| `cli`, `api` | Edges of the system: parse arguments, call the library, print or serve results | yes | PR 6 onward |

## Design rules

- **Pure core.** Analyzers take already-loaded data and return results. They never read files or use the network. I/O lives only in the loader, CLI and API.
- **No hidden numbers.** Every default value (durations, group sizes) comes from `assumptions/assumptions.yaml`. Nothing is hard-coded in analyzers.
- **Reproducible randomness.** Monte Carlo runs are seeded; the same input and seed give the same output.
- **Readable errors.** A validation error names the model, the node and the field that is wrong.
- **Synthetic data only.** No real systems, no scanning, no secrets.

## Algorithms (description only)

1. **Bootstrap analysis.** Find strongly connected components in the subgraph of `requires_to_start` and `requires_to_authenticate` edges. A component with more than one node is a cycle: no valid start order exists.
2. **Lockout simulation.** Remove the failed set F and compute which capabilities become unreachable.
3. **Break-glass validity.** For each break-glass path, compute its transitive dependency set and intersect it with F. A non-empty intersection means a false break-glass; the report includes the dependency chain.
4. **Recovery time.** Order recovery tasks along the critical path, draw durations from distributions in `assumptions.yaml`, and report a P10–P90 range. Results are labeled as calibratable estimates, not measurements.

## Limits

The model is only as good as its author's description of the environment. A shared component that is not drawn as an edge is invisible to the graph; see [ADR-0001](decisions/0001-failure-propagation-modeling.md) for how common-mode failures are handled and what that approach cannot find.
