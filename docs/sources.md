# Sources

Every external fact in this repository (standards, incidents, laws) is recorded here with its source and the date it was verified. A fact that is not listed here must not appear in the docs or code.

Rules:
- Standards (for example IEC 62443 or ISO standards) are used for concepts only, never quoted.
- Replay models separate "the report says" from "the model assumes". See `docs/replays/` once it exists.
- Add the entry in the same PR that first uses the fact.

## Entry format

| ID | Claim (as used in this repo) | Source (title and URL) | Verified on | Used in |
|---|---|---|---|---|

## Entries

| S-001 | On 2024-07-19 Windows hosts running the Falcon sensor crashed (bugcheck / blue screen); the problematic channel file `C-00000291*.sys` had timestamp 0409 UTC and the reverted version 0527 UTC; Mac and Linux hosts were not impacted; the workaround for individual hosts that kept crashing was Safe Mode or the Windows Recovery Environment, deleting the channel file, and a cold boot; BitLocker-encrypted hosts may require a recovery key | CrowdStrike, "Windows crashes related to Falcon Sensor" tech alert, published 2024-07-19. https://www.crowdstrike.com/wp-content/uploads/2024/07/Tech-Alert-Windows-crashes-related-to-Falcon-Sensor-2024-07-19.pdf | 2026-10-03 | `docs/reference-model.md` |
| S-002 | Customers running Falcon sensor for Windows 7.11 and above that were online between 04:09 and 05:27 UTC on 2024-07-19 may be impacted; a sensor configuration update triggered a logic error resulting in a system crash and blue screen; the issue was not the result of a cyberattack | CrowdStrike, "Technical Details: Falcon Content Update for Windows Hosts", 2024-07-20. https://www.crowdstrike.com/en-us/blog/falcon-update-for-windows-hosts-technical-details/ | 2026-10-03 | `docs/reference-model.md` |
| S-003 | The cause was a mismatch between the 21 input fields defined for the template type and the 20 values supplied, which led to an out-of-bounds memory read and a system crash | CrowdStrike, "External Technical Root Cause Analysis: Channel File 291", 2024-08-06. https://www.crowdstrike.com/wp-content/uploads/2024/08/Channel-File-291-Incident-Root-Cause-Analysis-08.06.2024.pdf | 2026-10-03 | `docs/reference-model.md` |

Notes on verification:
- S-001 and S-003 were read from the downloaded PDFs; S-002 from the published page text.
- The public reports describe affected Windows hosts in general. They do not say which customers' management hosts were affected; that part is a model assumption (see `docs/reference-model.md`).
