# Model and scenario format (draft)

Status: **model format implemented (PR 3); scenario format implemented (PR 4)**. The authoritative definition of the model format is the schema in `src/lockout/schema/model.py`, exported as `src/lockout/schema/lockout-model.schema.json` (regenerate with `python -m lockout.schema.export`).

Models and scenarios are YAML files. All values are synthetic.

## Model

```yaml
name: example-model
nodes:
  - id: idp
    kind: identity-provider
    tags: [role:identity]
  - id: vault
    kind: secrets-vault
    tags: []
edges:
  - from: idp
    to: vault
    type: requires_to_authenticate
capabilities:
  - id: console-login
    description: Log in to the management console
    requires: [idp]
break_glass_paths:
  - id: console-local-account
    capability: console-login
    requires: [vault]
```

### Nodes
- `id` (required, unique within the model), `kind` (required), `tags` (optional list of strings).
- `tags` exist from the first schema version, because adding them later would be a schema change. See [ADR-0001](decisions/0001-failure-propagation-modeling.md).

### Edges
- `from`, `to` (node ids) and `type`, one of `requires_to_start`, `requires_to_authenticate`, `requires_to_reach`, `requires_to_authorize`. There are exactly four edge types.

### Capabilities and break-glass paths
- A capability lists the nodes it needs (`requires`). A break-glass path names its `capability` and lists the nodes it needs (`requires`). Both may carry an optional `description`.

### Redundancy groups
- `redundancy_groups` (optional) are checked by the redundancy analyzer: shared dependencies and group state under a failure set (see architecture.md, Semantics). They list `members` (at least two node ids) that can stand in for each other. `min_available` (default 1) must be smaller than the number of members; otherwise no member could ever fail.

### Identifiers and tags
- Ids match `^[a-z0-9][a-z0-9_.-]*$`. Tags are `key:value` or a plain word in the same character set, for example `os:windows`.
- Unknown fields are rejected, so a typo cannot silently drop information.

### Semantic lint
The loader checks what the schema cannot:
- errors: duplicate ids, references to unknown nodes or capabilities, a redundancy group that allows no failure;
- warnings: a duplicated edge, a capability with an empty `requires`, a node used by nothing.

An error stops loading. Warnings are returned next to the model.

## Scenario

```yaml
name: edr-content-update-failure
failed:
  nodes: [dns-primary]
  select:
    tags_all: [os:windows, agent:edr]
```

- `failed.nodes` lists nodes by id.
- `failed.select.tags_all` selects every node carrying all listed tags. The final failure set is the union of both. 
- `failed.select.tags_all` must list at least one tag. Unknown fields are rejected.
- Resolution fails with a readable error when a named node does not exist, when the selector matches no node, or when the failure set ends up empty.
- Scenario fields for RTO and RPO are optional and are added in a later PR.
- Example scenarios live in `scenarios/`. The scenario schema is in `src/lockout/scenarios/model.py`.

## Validation errors

An error names the model, the node and the field, for example: `model "example-model": node "vault": field "kind" is required`. Semantic lint reports dangling references, duplicate ids and unknown edge types in the same style.

