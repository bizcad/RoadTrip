# SRCGEEE Execute Layer: Preflight Pattern

**Date:** 2026-03-17
**Context:** Design discussion — closing the SRCGEEE loop with a concrete Execute component
**Skill target:** `git-push-autonomous` (first implementation, generalizes to all skills)

---

## The Problem

The current Execute phase is a dead end. It either succeeds (logged) or fails (logged). Neither path feeds back into the loop in a structured way. The Evaluate layer never sees failures. Novel failures surface as silent exits, missing tokens, or cryptic stderr — hours after the fact.

The specific incident: `gpush` was silently failing due to a GCM intercept of the GITHUB_TOKEN. No error raised. No triage. No notification. The operator noticed something was wrong 20 minutes later and had to reconstruct state from git history.

---

## The Collect-After-Failure Trap

The instinct is to wrap Execute in a try/catch and collect data on failure. This works sometimes but is fragile:

- You get a stack trace, stderr, and an exit code
- Triage has to reverse-engineer the diagnosis from wreckage
- Context is already partially lost by the time collection happens
- Different failure modes look identical at the exception level

---

## The Preflight Pattern

Instead: validate all preconditions **before touching the world**.

A preflight is not a simulation of execution. It is a **read-only checklist**: did we do our prep work? Can the environment receive what we've composed?

### Checks for `git-push-autonomous`

The checks have a natural dependency order — each is pointless if the previous failed:

```
1. commit_message produced?     ← pipeline state: did Compose complete?
2. GITHUB_TOKEN set?            ← environment
3. remote reachable?            ← network (useless to check if 2 fails)
4. branch exists on remote?     ← repo state (useless to check if 3 fails)
5. push is fast-forward?        ← conflict state (useless to check if 4 fails)
```

First failure short-circuits. The error is always the **earliest unsatisfied precondition** — the most actionable one.

### Key Insight: Typed Failure Modes

Preflight failures are **typed** — they have domain meaning. This is what makes them consumable by triage:

| Check name | Triage path |
|---|---|
| `commit_message` | Re-enter Compose phase |
| `token_set` | Auth docs + PAT.txt instructions |
| `remote_reachable` | Network check, GCM intercept check |
| `branch_exists` | Pull/create branch decision |
| `fast_forward` | Pull/rebase decision needed |

Triage doesn't need to be intelligent. It matches the check name to a remediation path. Table lookup, not diagnosis.

---

## The Execute Structure

```
try:
    Execute(composed_action)
    → success → Evaluate(result)          # normal loop

except RecoverableError:
    context = gather(error, skill_docs, current_state)
    → Triage(context)                     # retry with different approach

except:
    → Evaluate(escalated=True, error)     # beyond recovery, needs judgment
```

The preflight runs **before** this try/catch:

```
Preflight → all checks pass → Execute try/catch
          → any check fails → Triage(PreflightResult)   # immediate, no execution attempted
```

---

## The Closed Vocabulary

The set of named preflight checks for a skill is its **closed vocabulary of failure modes**. This does double duty:

- **Known name** → triage routes to remediation
- **Unknown name** → triage escalates immediately to Evaluate, no wasted retries

```python
KNOWN_CHECKS = {"commit_message", "token_set", "remote_reachable",
                "branch_exists", "fast_forward"}

if result.first_failure.name not in KNOWN_CHECKS:
    escalate_to_evaluate(result)   # novel failure — don't guess
```

---

## Novel Failures: The Full Loop

When a 6th failure mode is discovered:

```
Unknown preflight failure detected
  → Evaluate: "novel failure mode, check name not in vocabulary"
  → immediately: GitHub Issue opened (thepopebot)
  → immediately: operator notified via Telegram
  → Invent agent: background task — reads telemetry, SKILL.md,
                  burned_patterns, figures out what happened
  → eventually: PR with new PreflightCheck + version bump
  → human reviews PR: stepwise debug, reproduce locally, merge or revise
  → on merge: fingerprint re-stamped, SKILL.md version bumped,
              AgentCard re-announced, network learns new failure mode
```

### Why This Division of Labor Works

The urgency is in the **notification** (thepopebot, immediate).
The correctness is in the **review** (human, deliberate).
The drafting is Invent's job (no time pressure).

The Issue contains:
- Exact failure reason from preflight
- Telemetry ID linking to full execution trace
- Skill version that was running
- What Invent drafted and why

The operator opens the PR and reads a single new `PreflightCheck` and a version bump. She can reproduce the failure locally against the draft before merging. No context reconstruction. No firefighting.

### Evolve's Concrete Output

Not "the model improved itself" in some opaque way. A specific, reviewable diff:

```
- new PreflightCheck added to skill
- SKILL.md version bumped (e.g. 1.2.0 → 1.3.0)
- fingerprint re-stamped via skill_scanner.py stamp
- changelog entry: "added check: <name>, discovered via novel failure <telemetry_id>"
- GitHub Issue closed by PR
```

The lineage from Part 5 is just git history.

---

## dryrun vs Preflight

`dryrun` is the public method on `SRCGEEEExecutor` that **runs the preflight and returns the result without executing**. It corresponds directly to the `-DryRun` flag on the existing `git_push.ps1` — same concept, proper return value instead of `Write-Host` output, consumable by triage programmatically.

```python
result = executor.dryrun(action)    # read-only, returns PreflightResult as ExecResult
if not result.success:
    triage(result)
else:
    result = executor.run(action)   # now execute with confidence
```

---

## Relationship to SRCGEEE

| Phase | Role |
|---|---|
| Sense | Match utterance to skill |
| Retrieve | Load skill docs, past telemetry |
| Compose | Stage files, generate commit message |
| Gate | Rules engine: are these files allowed? |
| **Execute** | **Preflight → run() or dryrun()** |
| Evaluate | Score result; receive escalated novel failures |
| Evolve | Draft new PreflightCheck; open Issue/PR |

The preflight sits at the **Compose→Execute boundary**: it verifies that Compose completed (commit message exists) and that the environment can receive the composed action (token, remote, branch, fast-forward).

Gate and Preflight are complementary:
- Gate asks: **should we execute?** (rules, policy, permissions)
- Preflight asks: **can we execute?** (environment, state, readiness)
