# PPA v0 Execution Contract

## Purpose

PPA v0 now returns a completion package instead of an unstructured answer blob. The contract is designed to keep three things explicit:

- what PPA thought the request was
- what path it chose to complete the work
- whether the outcome is an answer, a non-answer, or an escalation

This keeps "asking questions is successful completion" as a first-class behavior rather than a fallback apology.

## Paths

- `fast-path`: bounded deterministic work with a high chance of immediate completion
- `thinking-slow-path`: wider retrieval and cross-checking when the fast path is weak
- `invention-path`: create a triage packet when known skills and known evidence are insufficient

`invention-path` is not synthetic completion. It is explicit deferred work with evidence.

## Completion States

- `completed_answer`: grounded answer returned
- `completed_non_answer`: no trustworthy answer yet, but clarification or a bounded non-answer was returned successfully
- `completed_escalation`: PPA produced a triage packet for deeper research or new capability work
- `completed_deferred_work`: reserved for future background jobs and queued work

## Request Classes and Routing Contract

PPA v0 treats request class as a first-class routing input so orchestration can be moved into a dedicated repo without changing runtime semantics.

- `chat-question`: general conversational question
- `memory-query`: asks for prior decisions, rejections, or open questions
- `known-skill-execution`: deterministic execution against vetted code
- `assistance-request`: async help request where response time is unknown
- `invention-request`: capability gap requiring triage/research path

Routing rules:

1. `known-skill-execution` -> `fast-path`
2. `memory-query` -> `fast-path`, then `thinking-slow-path`, then `invention-path`
3. `assistance-request` -> `fast-path` queue action with `completed_deferred_work`
4. `invention-request` -> `invention-path` triage packet
5. `chat-question` -> default to memory-query flow until richer chat skilling exists

Asynchronous assistance is written to Prospective Memory queue:

- `analysis/ppa/prospective_memory_queue.jsonl`

This supports completion-through-deferred-work when external dependencies are unresolved at request time.

## Stage Contract

Every run returns these stages inside `completion_package`:

1. `request`
   Contains the incoming question, question id, timestamp, and selected skill.
2. `sense`
   Normalizes the question, identifies the requested skill, and decides whether clarification is required.
3. `retrieve`
   Records approach hints, retrieval attempts, and selected evidence counts.
4. `compose`
   States which skill or plan was selected and which path was chosen.
5. `gate`
   Explicit pass-through for now. This is a no-op stage by policy, not an omitted stage.
6. `execute`
   Records which deterministic executor ran and any artifacts created.
7. `evaluate`
   Maps the outcome to a completion state.
8. `evolve`
   Logs the run for future weighting and analysis.

## Current Skill Mapping

### `echo`

- Sense: classify as `echo-input`
- Retrieve: skipped
- Compose: deterministic `echo`
- Execute: return input with `Echo:` prefix
- Evaluate: `completed_answer`

### `memory-search`

- Sense: classify as `retrieve-roadtrip-memory` or `clarify-memory-query`
- Retrieve: try `fast`, then `slow`, then `slower`
- Compose:
  - `fast-path` when evidence is already strong
  - `thinking-slow-path` when wider retrieval is needed
  - `invention-path` when evidence stays weak and a triage packet is required
- Execute:
  - grounded answer
  - clarification questions
  - triage packet artifact
- Evaluate:
  - `completed_answer`
  - `completed_non_answer`
  - `completed_escalation`

### `assistance-request`

- Sense: classify as `assistance-request`
- Retrieve: skipped
- Compose: deterministic queue-deferred-work
- Execute: append deferred item to prospective memory queue
- Evaluate: `completed_deferred_work`

## Failure Classes

PPA v0 should keep these classes separate even before RBAC and policy become real:

- deterministic failure: executor bug, missing file, timeout, malformed input
- blocked completion: not enough detail to answer safely, so clarification is required
- capability gap: evidence and current skills are insufficient, so invention-path escalation is required

These are different outcomes and should not be merged into one generic failure.

## JSON Schema

The machine-readable schema lives here:

- `analysis/ppa/ppa_completion_package.schema.json`

That schema is the stable boundary for future aliases, wrappers, and UI work.

## Immediate Next Steps

- add a second-pass extractor for decisions, rejections, and reversals
- treat `completed_deferred_work` as the contract for queued invention jobs
- attach runtime duration and artifact hashes once execution expands beyond memory search
- hand off routing contract, schema, and queue semantics into standalone PPA repo