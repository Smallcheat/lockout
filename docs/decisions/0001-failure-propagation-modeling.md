# ADR-0001: Model common-mode failure with tags and scenario selectors

- Status: accepted
- Date: 2026-10-01

## Context

Some incidents are common-mode: one shared component, such as a security agent receiving a faulty content update, takes down every host that runs it, including systems needed for recovery. The model must be able to express "this shared component fails, and everything relying on it fails with it".

Recovery requirements for such cases (a per-device fix, a key, a credential) can already be modeled with the existing edge types: for example a "restore endpoint" capability that `requires_to_authenticate` against the node that holds keys and admin credentials.

## Options

| Option | Description | Pros | Cons |
|---|---|---|---|
| A. New edge type `crash_coupled` | A host is coupled to the agent's content channel; when the channel fails, the host fails. | Explicit semantics, visible in the graph. | A fifth edge type: schema, validation, UI legend and all analyzers change. Cycle analysis must learn that this is not a start cycle. |
| B. Extend `requires_to_start` to "start or keep running" | One edge type also means runtime dependency. | No new type. | Mixes concepts: runtime dependencies can appear as false bootstrap cycles, and interpretation gets harder. |
| C. Scenario property plus tags | Nodes carry `tags` (for example `os:windows`, `agent:edr`). A scenario selects its failure set with a tag selector. The lockout simulator already handles a failure set. | No new edge type, small change (a `tags` field and a selector), works with existing analyzers. | The shared component is not an edge in the graph, so hidden common-mode failures are not found automatically; the scenario author has to know to write the scenario. |

## Decision

Option C. It is the simplest option that is sufficient: a replay of a common-mode incident needs a failure set of "all nodes with these tags" and the computation of its consequences, which the lockout simulation already does. The four edge types stay unchanged and no migration is needed.

## Consequences

- `tags` is added to the node schema in the first schema version (PR 3), because adding it later would be a schema change.
- The tag selector is added to the scenario format in PR 7.
- Known weakness: common-mode failures that nobody thought to write a scenario for stay invisible.
- Possible follow-up: a common-mode sweep that tries each tag as a failure set and reports which tags lose recovery capability. This addresses the weakness without a new edge type. It is optional and not committed to.
- Where a model places key storage or similar details is a **model assumption**, not a claim about any vendor.
