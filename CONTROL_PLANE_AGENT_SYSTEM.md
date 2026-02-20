## Objective (Next 30 Days)
Build a working self-improving software-generating program (hardened OpenClaw/OpenCraw-style assistant) that can reliably turn probabilistic research into deterministic, testable code artifacts.

## Context
I am managing a rapidly evolving AI engineering project and need a clearer operational system for:
- Idea intake and memory progression
- Research-to-plan conversion
- Adversarial risk review
- Code generation and testing
- Governance and promotion gates

I want this workflow to support memory reliability, execution clarity, and repeatable quality.

## Locked Decisions
1. **Control-plane separation**
   - Assume project-management/control-plane should be a separate repo/program that can manage this and future workspaces.

2. **Testing structure**
   - Keep unit/integration tests near product code.
   - Maintain a separate cross-project evaluation harness for benchmarks, adversarial suites, and regression trends.

## North-Star Metric (30 days)
A working self-improving software-generating assistant.

## Process Requirements
- Fail-fast is mandatory: failures are features.
- Testing/feedback must occur continuously, not only at the end.
- Every cycle must include explicit hypotheses and success metrics.
- Adversarial review must recur throughout the lifecycle.

## Workflow (Required)
1. Add idea to Prospective Memory.
2. AI performs fast research scan.
3. Human filters relevance.
4. AI performs deeper research.
5. Human + AI produce 10,000-ft opportunity plan.
6. Human + AI run adversarial evaluation (recurring, not one-time).
7. AI drafts PRD, constitution, governance, expectations.
8. AI executes plan with self-improvement loop.
9. Human defines verification strategy.
10. Human provides real-world data.
11. AI writes tests (unit → integration → e2e).
12. Human validates with real data and decides continue/pivot/stop.

## Promotion Rules
### Prospective → WIP
Promote only when:
- item is well-defined, and
- first-pass research indicates a plausible path to second-depth research.

### WIP → Published
Promote only after codified multi-pass research and adversarial closure:
1. Initial model outputs gathered.
2. Details summarized; questions answered.
3. Results documented for adversarial review.
4. Adversarial round where models critique/rebut each other.
5. GPT-5.3 arbitrates to consensus.
6. Consensus threshold: **95%** (initial target).
7. Output artifact is promotion-ready PRD/research package.

## Stop-and-Rethink Thresholds (Hard Gates)
Trigger stop/rethink if any threshold is hit:
- **2 failed loops**
- **<95% consensus**
- **>4 minutes** per critical loop
- **>2500 tokens** per critical loop budget

## Required Outputs From You
Please produce:
1. A critique of this operating model (strengths, risks, blind spots).
2. A concrete set of **failure modes** with examples for this project.
3. A revised gating model with measurable pass/fail criteria.
4. A concise implementation roadmap (MVP control-plane first).
5. Any clarifying questions needed to finalize execution.

## Failure Mode Examples to Expand
Include practical examples such as:
- Research drift (no hypothesis/metric)
- False consensus across models
- Spec-code mismatch
- Test illusion (high pass rate, low real-world reliability)
- Memory promotion errors (premature publish)
- Adversarial blind spots (edge cases untested)
- Cost/latency runaway loops
- Safety/policy regression during self-improvement