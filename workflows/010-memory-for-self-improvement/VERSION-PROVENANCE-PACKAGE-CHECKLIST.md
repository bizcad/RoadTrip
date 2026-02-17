# Version Provenance Package (Solo, Minimal)

Purpose: satisfy trust/version requirements with the least overhead possible.

Target time: 5-10 minutes per release decision.

## Required (Blocking)
- [ ] `SKILL.md` front matter includes `version` (for each trusted skill changed)
- [ ] `CLAUDE.md` front matter includes matching `version` (or explicit N/A note)
- [ ] Fingerprint/provenance record references those exact versions
- [ ] Hash/fingerprint input list includes versioned artifact paths
- [ ] Release note records one decision line: `version provenance verified = yes`

## Evidence (just links/paths)
- Skill spec paths:
- CLAUDE spec paths:
- Fingerprint/provenance artifact path:
- Hash input manifest path:
- Release decision record path:

## Quick Fail Rules
- If any changed trusted artifact has no version metadata → No-Go.
- If spec version and fingerprint/provenance version disagree → No-Go.
- If evidence paths are missing → No-Go.

## Practical Reminder
Keep this tiny. If it takes more than 10 minutes, capture only the minimum evidence needed to prove version-to-fingerprint integrity and move on.
