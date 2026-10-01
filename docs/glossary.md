# Glossary

| Term | Meaning in Lockout |
|---|---|
| Node | A component of the management plane, such as an identity provider, DNS, a certificate authority, an out-of-band network, a jump host, or a human role. |
| Edge | A typed dependency between two nodes. See the four types below. |
| `requires_to_start` | The source cannot start unless the target is available. |
| `requires_to_authenticate` | Logging in to the source requires the target. |
| `requires_to_reach` | Network or out-of-band connectivity to the source requires the target. |
| `requires_to_authorize` | An approval or authorization for the source requires the target. |
| Capability | Something operators need to recover, for example "log in to the management console", "enter the site physically", "approve a change", "restore a backup". |
| Break-glass path | A conditional alternative route to a capability, used when the normal route is unavailable. |
| Valid break-glass path | A break-glass path whose transitive dependencies do not intersect the failed set. |
| False break-glass | A break-glass path that depends on a failed component, so it exists on paper but would not work. |
| Failure set (F) | The set of nodes assumed failed in a scenario. It is chosen by node name, by tag selector, or both. |
| Tag | A free-form label on a node, such as `os:windows` or `agent:edr`. Used to select common-mode failure sets. |
| Bootstrap cycle | A group of nodes that mutually depend on each other to start or authenticate, so none can come up first. |
| Lockout | A state where operators lose a capability they need to recover. |
| RTO | Recovery time objective: how long a service may be down. Used as a scenario field, not as a standard citation. |
| RPO | Recovery point objective: how much data loss is tolerable. Used as a scenario field. |
| Replay model | An illustrative model built from a public incident report. It separates "the report says" from "the model assumes". |
