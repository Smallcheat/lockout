# Model and scenario format (draft)

Status: **draft**. The authoritative definition is the schema introduced in PR 3. This page fixes the intent so the schema has something to be reviewed against.

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
- A capability lists the nodes it needs. A break-glass path is attached to a capability and lists the nodes it needs.

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
- Scenario fields for RTO and RPO are optional and are added in a later PR.

## Validation errors

An error names the model, the node and the field, for example: `model "example-model": node "vault": field "kind" is required`. Semantic lint reports dangling references, duplicate ids and unknown edge types in the same style.

## Not yet decided

Exact field names may change when the schema is written in PR 3.
