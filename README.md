# RoadTrip: An Intelligent, Trusted Travel Partner

> **How do you trust an AI agent that needs access to the internet?**
>
> RoadTrip is a proof-of-concept framework for building **verifiable, auditable AI skills** that can safely interact with external services while remaining under your control.

---

## The Vision: A Travel Companion You Can Actually Trust

Imagine you're planning a cross-country road trip. You want an AI partner to help you:

- **Plan the route** using real maps and traffic data
- **Track fuel costs** based on current gas prices  
- **Monitor weather risks** and suggest safer alternatives
- **Update your plans** as conditions change during your journey
- **Remain verifiable** — you can see exactly what it's doing at every step

This sounds simple. But it requires something rare in AI development: **transparency and verifiable integrity at every layer**.

That's what RoadTrip builds.

---

## The Problem: AI Access + Safety

Most AI frameworks choose a uncomfortable binary:

1. **Keep AI sandboxed** — limited capability, limited usefulness
2. **Give AI full access** — powerful, but unverifiable and risky

Neither is acceptable for a system you want to trust with real decisions that affect real safety.

RoadTrip chooses a third path: **build verifiable systems from the ground up**.

This means:
- ✅ Deterministic code for critical decisions (file validation, authorization, logging)
- ✅ Probabilistic reasoning for creative tasks (planning, message generation, adaptation)
- ✅ Transparent verification for every output (test infrastructure, audit logging, end-to-end checks)
- ✅ Controlled access to external services (APIs, maps, weather data — no unlimited internet)

---

## How It Works: Skills as Building Blocks

RoadTrip uses a **skills framework** where each capability is independently verifiable:

```
┌─────────────────────────────────────────────┐
│  Orchestrator (Claude decides what to do)   │
└──────────────┬──────────────────────────────┘
               │
       ┌───────┴────────┬──────────┐
       ▼                ▼          ▼
   ┌────────┐   ┌────────────┐  ┌──────────┐
   │ Auth   │   │ Commit     │  │Telemetry │
   │Validator   │ Message    │  │  Logger  │
   │(verify)│   │Generator   │  │(audit)   │
   │        │   │(generate)  │  │          │
   └────────┘   └────────────┘  └──────────┘
```

Each skill:
- Has a **clear responsibility** (one reason to change)
- Is **independently testable** (run in isolation)
- Is **verifiable** (outputs can be checked)
- Is **documented** (SKILL.md, CLAUDE.md, tests)

---

## Why This Matters: The Rigor Problem

When you build AI systems, you face a fundamental challenge:

> **How do you know your system is doing the right thing?**

This is what engineers call "the rigor problem," and it's worse in AI because failures can be subtle and non-deterministic.

RoadTrip solves this through three architectural patterns:

### 1. **Immutable Prototypes** (Know What You Trust)

Core systems like `git_push.ps1` are never modified. Instead of integration through modification, we integrate through **composition**:

```powershell
# New skills call old prototypes, not the reverse
$message = .\invoke-commit-message.ps1 -StagedFiles @("file1")
.\git_push.ps1 -Message $message    # Old system remains pure
```

This guarantees: **if the original worked, it still works**.

### 2. **Invisible Test Infrastructure** (Tests Don't Contaminate)

Test files are in `.gitignore`—they're metadata, not deliverables. This eliminates circular references where tests become part of what they're testing.

### 3. **Oracle-Based Verification** (Verify Against Reality)

We use simpler, proven systems to validate complex ones:

```
Both tools analyze the same files:
✓ git_push.ps1:       "chore: update 3 files (+0 ~3 -0)"
✓ commit_message.py:  "chore: update multiple modules"
✓ Both valid, both verifiable
→ Different heuristics, but same intent proven
```

**Result**: You can actually trust the output.

---

## Getting Started

### Quick Look at the Concept

Start with the proof-of-concept planning tool:

👉 [**docs/README_RoadTrip.md**](docs/README_RoadTrip.md) — The travel planning POC  
- Google Sheets integration  
- Google My Maps integration  
- Weather risk tracking  
- Cost estimation

### Understanding the Philosophy

For the engineering principles behind trustworthy AI skills:

👉 [**docs/Principles-and-Processes.md**](docs/Principles-and-Processes.md) — Design framework  
- Core principles (fail-safe, SOLID, deterministic + probabilistic)
- Skill development methodology  
- Quality standards and review process  
- Code organization patterns  

### How We Built This: A Case Study

For a hands-on walkthrough of how we apply this philosophy to real code:

👉 [**docs/Blog_Rigor_in_Agentic_Development.md**](docs/Blog_Rigor_in_Agentic_Development.md) — Case study in verification  
- How we built the commit-message skill  
- Why immutable prototypes matter  
- How oracle-based testing works  
- Why verification is non-negotiable  

---

## Architecture: Skills + Orchestration

The current codebase implements **Phase 1b** of the RoadTrip framework:

### Skills (Reusable Building Blocks)

**`src/skills/commit_message.py`** — Generates semantic commit messages
- **Tier 1**: Deterministic heuristics (90% of commits, zero cost)
- **Tier 2**: Claude fallback (10% of ambiguous cases, ~$0.001 per call)
- **Tier 3**: User override (explicit control)
- **Result**: Valid [Conventional Commits](https://www.conventionalcommits.org/) format

**`src/skills/rules_engine.py`** — File validation  
- Pattern matching against configurable rules
- Idempotent, deterministic, fully testable

**`src/skills/auth_validator.py`** (ready to implement)
- Multi-layer authorization decisions  
- Audit logging
- Role-based access control

**`src/skills/telemetry_logger.py`** (ready to implement)
- Decision tracking
- Cost tracking
- Audit trail for compliance

### Orchestration (Skill Composition)

**`src/skills/skill_orchestrator.py`** (ready to implement)
- Chains skills in sequence
- Handles errors and fallbacks
- Routes decisions to Claude when needed

### Configuration (Policy-Driven)

**`config/commit-strategy.yaml`** — Policy for commit message generation  
**`config/authorization.yaml`** — Authorization rules  
**`src/skills/models.py`** — Data contracts for all inputs/outputs

---

## Current Status: Phase 1b

✅ **Complete**
- commit-message skill (all Tier 1→2→3 implemented)
- Comprehensive test runner (oracle-based validation)
- Error handling patterns
- Documentation templates (SKILL.md, CLAUDE.md, CLAUDE.instructions.md)

🔄 **In Progress**
- skill-orchestrator (chains multiple skills)
- Integration testing with real commits

📋 **Ready to Implement**
- auth-validator (authorization layer)
- telemetry-logger (decision tracking)
- Phase 2 features (content scanning, learning loops)

---

## Why Verification is Non-Negotiable

Here's the key insight from building this: **verification isn't optional**.

When you build AI systems that access the internet, you must be able to answer these questions with evidence:

1. **What did the system do?** (Audit trail)
2. **Why did it do that?** (Decision logging + reasoning)
3. **Is that the right decision?** (Verification against spec)
4. **Can I prove it to someone else?** (Reproducible on demand)

RoadTrip answers all four. That's why you can actually trust it.

---

## Philosophy: Conservative Defaults

The entire framework is built on one principle:

> **"If in doubt, block."**

- Missing authorization rule → block access
- Low confidence score → ask Claude for rationale
- Unexpected file type → fail safe, don't guess
- Unknown error → escalate, don't recover

This isn't about being paranoid. It's about being honest about what you know and don't know.

---

## Contributing: How to Add Skills

Each new skill follows the same pattern:

1. **Create the SKILL.md** — Define input/output contract, confidence model, cost
2. **Create src/skills/my_skill.py** — Implement with deterministic core
3. **Create tests/** — Write comprehensive tests; keep tests in `.gitignore`
4. **Create docs/how-my-skill-works.md** — Explain the rigor, not just the code
5. **Update the orchestrator** — Register the skill for composition

---

## Security & Trust Model

This framework prioritizes **transparency over black magic**:

- ✅ All configuration in YAML (readable, auditable, versionable)
- ✅ All decisions logged with confidence scores
- ✅ All code in Python/PowerShell (readable, not compiled)
- ✅ All tests use `.gitignore` (infrastructure ≠ deliverables)
- ✅ All outputs verifiable (can reproduce on demand)

**Trade-off**: Slightly more verbose, more explicit, more to review. **Benefit**: You actually know what your system is doing.

---

## Next Steps

### For Understanding
1. Read [docs/Principles-and-Processes.md](docs/Principles-and-Processes.md) (design philosophy)
2. Read [docs/Blog_Rigor_in_Agentic_Development.md](docs/Blog_Rigor_in_Agentic_Development.md) (how we verify)
3. Read the other files in [docs/](docs/) to understand where I got the ideas.
4. Clone the repo and run the tests

### For Building
1. Pick a skill from the "Ready to Implement" list
2. Follow the SKILL.md template
3. Build deterministic core + Claude fallback
4. Write tests (keep them in `.gitignore`)
5. Push and verify on GitHub

### For Collaboration

This is an open effort to define how we build trustworthy AI. If you:
- Build AI skills and want them to be verifiable
- Care about safety and transparency
- Want to contribute patterns or skills
- Have experience with AI orchestration

→ Consider contributing. This framework is designed to be extended.

---

## License

See [LICENSE](LICENSE) for details.

---

## Further Reading

- **Inside RoadTrip**: Start with [docs/README_RoadTrip.md](docs/README_RoadTrip.md)
- **Design Principles**: See [docs/Principles-and-Processes.md](docs/Principles-and-Processes.md)  
- **How We Built It**: Read [docs/Blog_Rigor_in_Agentic_Development.md](docs/Blog_Rigor_in_Agentic_Development.md)
- **OpenClaw Risks**: We're building safer alternatives to vulnerable AI crawlers
- **Signed Agentic Work**: We're defining standards for trustworthy AI skills (see `workflows/003-signed-agentic-work/`)

---

**RoadTrip: Build AI skills you can actually verify. Deploy systems you can actually trust.**
