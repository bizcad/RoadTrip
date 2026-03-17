# PPA Reward Function v1

## Purpose
Define a portable, implementation-ready reward function for PPA routing and execution that optimizes for:

- completion quality
- elapsed time
- monetary cost
- deterministic preference
- safety/compliance outcomes

This spec is designed to transfer into a separate PPA repository with minimal changes.

## Core Principle
Optimize value under constraints, not output volume.

- Primary objective: maximize value-per-token and value-per-minute.
- Hard constraints: budget caps, policy gates, and reliability thresholds.

## Definitions

- `Q`: quality score in [0, 1].
- `T`: elapsed time in seconds.
- `C`: dollar-denominated compute cost.
- `D`: deterministic coverage ratio in [0, 1].
- `P`: policy compliance indicator (1 if pass, 0 if violation).
- `R`: reliability score in [0, 1] (tests/evals/confidence calibration).
- `E`: escalation penalty in [0, 1] (higher means more expensive fallback behavior).
- `S`: strategic value estimate in [0, 1] (business/user impact estimate).

## Reward Equation

Use a weighted constrained objective:

R_total = P * (
  w_q * Q
  + w_s * S
  + w_d * D
  + w_r * R
  - w_t * T_norm
  - w_c * C_norm
  - w_e * E
)

Where:

- `T_norm = min(T / T_budget, 2.0)`
- `C_norm = min(C / C_budget, 2.0)`
- `P = 0` if any policy hard-fail occurs

Recommended initial weights:

- `w_q = 0.30`
- `w_s = 0.20`
- `w_d = 0.15`
- `w_r = 0.20`
- `w_t = 0.07`
- `w_c = 0.06`
- `w_e = 0.02`

Rationale:

- prioritize correctness and reliability
- reward deterministic execution where feasible
- penalize time and cost in normalized form
- keep escalation penalty small but non-zero to discourage avoidable invention-path churn

## Hard Constraints (Must Pass)

1. Policy gate pass required.
2. Budget limits not exceeded unless explicit override.
3. Safety-critical checks must pass deterministically.
4. If confidence below threshold, return non-answer or deferred work instead of synthetic certainty.

## Path-Level Budget Policy

- fast-path:
  - smallest effective model first
  - strict low latency and low cost caps
- thinking-slow-path:
  - wider retrieval and cross-check
  - medium latency and medium cost caps
- invention-path:
  - triage packet + deferred work
  - explicit approval or queue policy before heavier exploration

## Deterministic Preference Policy

When two plans have similar expected quality, choose the one with higher deterministic coverage and lower expected cost.

Tie-break rule:

1. higher policy confidence
2. higher deterministic coverage
3. lower normalized cost
4. lower normalized time

## Deferred Work Handling

For `assistance-request` and unresolved dependencies:

- mark completion as `completed_deferred_work`
- write queue item to prospective memory
- reward successful queueing and metadata quality
- do not force low-confidence direct answers

## Metrics for Optimization

Track and optimize these weekly:

1. Cost-to-Learn (CTL): dollars per validated insight.
2. Value per 1M tokens.
3. Value per engineering hour.
4. Router efficiency: percent handled by smallest effective tier.
5. Verification spend ratio.
6. Deferred-work resolution rate.
7. Reversal rate: percent of decisions reversed after deployment.

## Free/Low-Cost Compute Strategy

Use free tiers and prepaid token pools as accelerator resources, not assumptions.

- maintain provider-aware budgets
- avoid reward shaping that assumes long-term near-zero token pricing
- re-estimate `C_budget` and `w_c` quarterly or when pricing changes materially

## Suggested Runtime Defaults

- `T_budget_fast = 8s`
- `T_budget_slow = 30s`
- `T_budget_invention = 120s` (for packet generation only)
- `C_budget_fast = $0.02`
- `C_budget_slow = $0.10`
- `C_budget_invention = $0.20` (triage-only stage)

These are starting values; calibrate from observed telemetry.

## Transfer Notes

To move this into a dedicated PPA repo:

1. Keep this file as a policy artifact.
2. Implement equation and constraints in a routing policy module.
3. Bind metrics to telemetry events emitted by execution stages.
4. Version weight changes with decision receipts.

## Initial Validation Plan

1. Shadow mode for one week: compute rewards without changing routing.
2. Compare baseline vs reward-aware routing on quality, time, cost.
3. Enable reward-aware routing for low-risk classes first.
4. Expand to higher-risk classes after stability thresholds are met.
