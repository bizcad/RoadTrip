# Suspected Secret Exposure — Immediate Checklist

1. Contain
- pause relevant automation/workflows
- revoke or disable the suspected token immediately

2. Rotate
- issue replacement credential
- update secret authority store
- propagate to runtime consumers

3. Eradicate
- remove exposed values from tracked files
- scrub logs and memory artifacts where feasible

4. Verify
- rerun authentication checks with non-interactive path
- confirm old secret no longer grants access

5. Document
- capture root cause, blast radius, and timeline
- add prevention control to this packet before closing

## Current scan note
A pattern scan in tracked files found placeholder/token-reference text, but no obvious live PAT signatures in the scanned set.
