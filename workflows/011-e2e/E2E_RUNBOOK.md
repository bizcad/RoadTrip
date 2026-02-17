# E2E Runbook (Tomorrow)

## Goal

Run one real trusted workflow end to end:

- acquire enough usable skills/MCPs
- compose a graph workflow
- execute safely
- inspect outputs/artifacts/decisions

---

## Track A — DSL terminology

- [ ] Review and approve `DSL_TERMINOLOGY.md`
- [ ] Lock preferred public naming:
  - [ ] Supply Chain Trust Pipeline
  - [ ] Trusted Admission Gate
  - [ ] Trust Manifest
  - [ ] Pre-Execution Verification

Output:
- [ ] Terminology accepted for docs/UI/logging

---

## Track B — connector spec

- [ ] Review and approve `NODE_EDGE_CONNECTOR_SPEC.md`
- [ ] Validate node contract fields are sufficient for:
  - [ ] skill nodes
  - [ ] MCP nodes
  - [ ] future crypto/privacy extension points

Output:
- [ ] Connector spec accepted as implementation baseline

---

## Track C — supply chain trust path

For each candidate capability:

- [ ] Find candidate (`skill` or `mcp`)
- [ ] Test minimum behavior
- [ ] Fingerprint and provenance check
- [ ] Register in trusted registry
- [ ] Generate/refresh trust manifest

Command pattern:

```powershell
py scripts/generate_trust_scorecard.py --manifest-dir workflows/006-Skill-Acquisition/trust-manifests --release-id <id> --manifest-evidence-map workflows/006-Skill-Acquisition/TRUST_MANIFEST_EVIDENCE_MAP_TEMPLATE.json
```

Output:
- [ ] At least 3 trusted capabilities (`allow_auto` or explicit manual-review plan)

---

## Track D — real workflow execution

- [ ] Select scenario (safe, bounded, no irreversible side effects)
- [ ] Build DAG with typed connectors
- [ ] Include checkpoint before any committing action
- [ ] Execute workflow
- [ ] Inspect:
  - [ ] action results
  - [ ] artifacts
  - [ ] trust and policy decisions
  - [ ] errors/warnings/drift indicators

Output:
- [ ] One complete run report with what worked and what failed

---

## Fatal failure policy

On fatal failure before commit barrier:

- [ ] halt execution
- [ ] drop staged steps since checkpoint
- [ ] preserve trace and artifacts for diagnosis

On fatal failure after commit barrier:

- [ ] execute compensation path if defined
- [ ] mark incident for manual review

---

## Definition of done

- [ ] Terminology locked
- [ ] Connector spec accepted
- [ ] Trust path exercised on real candidates
- [ ] One real DAG run completed and reviewed
- [ ] Next actions captured for implementation sprint
