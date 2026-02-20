# Elevator Pitch + Strategy (Fast Thinking)

## Core pitch
Bring safety to AI by making failure recovery bounded, observable, and policy-driven.

## One-liners
- Retry is a scalpel, not a loop.
- Recover once, maybe twice, then stop and learn.
- Fast retries for reliability; hard stops for safety.

## Product framing
- Reliability promise: recover transient issues quickly.
- Safety promise: never recurse into silent damage.
- Learning promise: convert repeated failure patterns into vetted workflow improvements.

## Your intuition captured
- Keep retry depth intentionally small now (1-2).
- Use real-world data to tune depth later.
- If a domain underperforms (e.g., 95% marketing, 60% accounting), trigger a controlled improvement cycle:
  1. detect performance gap,
  2. open candidate workflow/agent proposal,
  3. vet with tests and policy,
  4. promote only with evidence.

## Complexity guardrail
Default to the simplest mechanism that preserves safety; only add control surface after repeated evidence justifies it.
