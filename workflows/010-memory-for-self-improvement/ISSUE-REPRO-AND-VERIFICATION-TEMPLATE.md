# Issue Repro + Fix Verification (Ultra-Lean)

Use this only for issues that affect reliability, safety, or repeated workflow failures.

## 1) Problem Statement (1-2 lines)
- What is failing?
- Why it matters (impact to user/workflow)?

## 2) Reproduction (minimum viable)
- Trigger steps (short, deterministic)
- Expected result
- Actual result

## 3) Root Cause (current best explanation)
- Proven cause or strongest hypothesis
- Evidence that supports it (only relevant evidence)

## 4) Fix Verification
- What changed (high level)
- Proof the issue is resolved (single strongest check)
- Regression check (what prevents recurrence)

## 5) Decision + Follow-up
- Status: Resolved | Mitigated | Deferred
- If deferred: explicit condition/date for revisit

---

## Required Test Mapping (Non-Negotiable)
For each issue, select applicable categories and attach only the minimum evidence needed:
- [ ] Integration
- [ ] Adversarial
- [ ] Performance
- [ ] Security

If a category is not applicable, state why in one sentence.

---

## Example (Windows shell mismatch)

### 1) Problem Statement
Agent outputs Unix-first commands (`head`, `tail`, `python`) in PowerShell workflow, causing failures and wasted retries.

### 2) Reproduction
- Ask agent to inspect last 20 lines of a log and run a script on Windows PowerShell.
- Expected: PowerShell-native commands (`Get-Content -Tail 20`, `py script.py`).
- Actual: Unix-style commands (`tail -20`, `python script.py`).

### 3) Root Cause
Prompt/system context did not sufficiently prioritize OS-aware command generation in this workflow.

### 4) Fix Verification
- Change: Added explicit PowerShell/Windows command policy in workflow specs.
- Proof: Re-ran same prompt; output used PowerShell-native commands only.
- Regression: Added adversarial prompt variant to ensure no fallback to Unix syntax on Windows.

### 5) Decision + Follow-up
Status: Resolved.
