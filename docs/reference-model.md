# Reference model

`models/reference-dc/model.yaml` is a synthetic, vendor-neutral management plane. It describes no real site, product or vendor, and it contains no location-specific data. It is the model the CI gate will require to pass (PR 5).

## Shape

46 nodes, 80 edges, 10 capabilities, 6 break-glass paths and 3 redundancy groups. All four edge types are used.

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
- **Human roles depend on infrastructure.** The on-site engineer needs access control to authorize entry (`requires_to_authorize`), and the on-call engineer reaches the OOB path through the VPN. Break-glass paths that list a human role inherit these dependencies, so they are false break-glass when access control (or the directory behind it) fails. The tool reports this as it is. A finer model would split "engineer already inside" from "engineer arriving"; that is a possible refinement, not done here to keep the model unchanged by the output it produces.
- **Break-glass paths are independent of identity, except one.** The on-call engineer reaches the OOB path through the VPN, which needs the identity provider. `bg-cellular-oob` is therefore a false break-glass when `idp-primary` fails (see `scenarios/idp-primary-down.yaml`). This is a deliberate demonstration in a synthetic model, not a claim about real sites.
- **Model assumptions, not vendor claims.** For example, `disk-key-escrow` authenticating against the directory is a choice made for this model.

## What the tool reports for the redundancy groups

`lockout analyze` flags all three groups as false redundancy, for example because both NTP sources, both DNS servers and both identity providers depend on the single `core-network` node, and both identity providers share the directory, PKI and secrets chain. This is the tool reporting the model as written. The model has one core network node and one directory because of how it is drawn, which is an unjustified design choice (see "Not yet justified"); the findings are not claims about real sites.

## Not in the model

Power, cooling and facility systems beyond DCIM and BMS management; real product names; any real topology.

## Dependency justifications

Rule: every dependency in the reference model has a justification that rests on real practice or a real case. A justification separates **the report says** (a fact with a source in [sources.md](sources.md)) from **the model assumes** (a choice made for this synthetic model). Dependencies without a justification are listed under "Not yet justified" and are not claims about real data centers.

### Common-mode agent failure and fleet administration

Case: the CrowdStrike content update of 2024-07-19.

**The report says**
- Windows hosts running Falcon sensor 7.11 and above that were online between 04:09 and 05:27 UTC crashed with a blue screen; a configuration update triggered the crash, not an attack (S-001, S-002).
- Mac and Linux hosts were not impacted (S-001).
- The cause was an input-count mismatch that led to an out-of-bounds read (S-003).
- Hosts that kept crashing had to be fixed one by one: boot into Safe Mode or the Windows Recovery Environment, delete the channel file, cold boot. BitLocker-encrypted hosts may require a recovery key (S-001).

**The model assumes**
- `windows-admin-hosts` and `windows-server-fleet` run the agent (tags `os:windows`, `agent:edr`). The reports describe affected Windows hosts in general; whether an operator's management hosts ran the agent is the model's assumption.
- Administration happens from those hosts, so the capability `administer-fleet` requires `windows-admin-hosts` and `linux-mgmt-hosts`, and the model has no break-glass path for it. In the scenario `edr-content-update-failure` the capability is therefore lost. The Linux management hosts also carry `agent:edr`, but the scenario selects `os:windows` and `agent:edr`, so they stay up, which matches S-001.
- There is no edge for the shared agent (ADR-0001, option C): the scenario author selects the failure set by tag.

### Disk key escrow and endpoint recovery

**The report says**: individual hosts needed manual remediation and BitLocker-encrypted hosts may require a recovery key (S-001).

**The model assumes**: the capability `restore-endpoint` requires `disk-key-escrow` and an on-site engineer; the key store authenticates against the directory and needs DNS. Where keys are kept and what they depend on is a choice made for this model, not a claim about Microsoft, CrowdStrike or any customer.

### Not yet justified

All other dependencies (network base, core services, identity chain, operations tooling, compute, physical access, human roles) are design choices of this synthetic model. They have no recorded justification yet and must not be read as statements about real sites. Each one needs a justification from real practice or a case, or removal, before v0.1.
