# Reference model

`models/reference-dc/model.yaml` is a synthetic, vendor-neutral management plane. It describes no real site, product or vendor, and it contains no location-specific data. It is the model the CI gate will require to pass (PR 5).

## Shape

46 nodes, 80 edges, 9 capabilities, 6 break-glass paths and 3 redundancy groups. All four edge types are used.

| Layer | Nodes (examples) |
|---|---|
| Networks | core, management and out-of-band networks, VPN, jump host, cellular OOB gateway |
| Core services | two NTP sources, two DNS servers, DHCP |
| Identity and secrets | directory, two identity providers, MFA, PKI (offline root, issuing CA), HSM, secrets vault, privileged access manager, disk key escrow |
| Operations tooling | configuration management, monitoring, logging, DCIM, BMS, change approval, backup (online and offline), security agent console |
| Compute | hypervisors, virtualization manager, BMCs, Windows and Linux admin hosts |
| Physical access | access control, door controllers, key safe, security desk |
| Humans | on-call engineer, on-site engineer, change approver, incident commander |

## Design choices

- **Bootstrappable.** The start and authenticate subgraph has no cycle. A test guards this until the cycle analyzer (PR 4) replaces it.
- **Out-of-band independence.** The OOB network and the cellular gateway depend on no identity service, so break-glass paths through them are independent of the identity stack.
- **Common-mode tags.** Several hosts carry `os:windows` and `agent:edr`. Per [ADR-0001](decisions/0001-failure-propagation-modeling.md) there is no edge for the shared agent; a scenario selects the failure set by tag.
- **Model assumptions, not vendor claims.** For example, `disk-key-escrow` authenticating against the directory is a choice made for this model.

## Not in the model

Power, cooling and facility systems beyond DCIM and BMS management; real product names; any real topology.
