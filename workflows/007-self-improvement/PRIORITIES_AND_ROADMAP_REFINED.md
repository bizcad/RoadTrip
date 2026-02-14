# Refined Roadmap: Priorities & Future Enhancements

**Version**: 1.0  
**Status**: Updated based on feedback  
**Last Updated**: 2026-02-14  
**Purpose**: Clarify what builds now vs. what defers, based on practical priorities

---

## The Three Horizons

### HORIZON 1: NOW (Phase 1b, Feb-Mar 2026)
**Focus**: Foundation for all future learning

- ✅ **ExecutionMetrics data model** (configurable even for repo cloners)
  - Reward function as explicit, changeable dataclass
  - Example: Clone repo + update `RewardFunction.reliability_weight = 0.40` (if they disagree with 0.50)
- ✅ **Metrics persistence** (append-only JSONL)
- ✅ **Orchestrator integration** (capture metrics for all skills)
- ✅ **Cost & quota tracking**
- ✅ **Baseline computation**

**Success**: System collects rich observable data. Nothing optimizes yet.

---

### HORIZON 2: SOON (Phase 2a-2c, Mar-Sep 2026)
**Focus**: Intelligence layer (detect patterns, advise thoughtfully)

**Phase 2a (Q1-Q2)**:
- ✅ **Anomaly detection** (when is something unusual?)
- ✅ **System observations** (volunteer insights when patterns emerge, thoughtfully not naggily)
  - Example: "I notice Skill A consistently outperforms Skill B. Worth considering?" (Once, not repeatedly)
  - Not: "Skill A is better! Skill A! Make Skill A default! Skill A! Skill A!" (Marketing-spam mode ❌)
- ✅ **Bidirectional learning** (system learns from your approval patterns)
  - Example: After 10 optimizations, system learns "you care more about reliability than cost in latency-sensitive operations"
- ✅ **Fingerprinting & security checks**
- ✅ **Adversarial testing for skills** (NEW—see below)

**Phase 2b (Q2-Q3)**:
- ✅ **Optimization proposals** (guided by reward function)
- ✅ **A/B testing framework**
- ✅ **Approval workflow** (human gates changes)

**Phase 2c (Q3-Q4)**:
- ✅ **Bounded autonomy** (system makes decisions within guardrails)
- ✅ **Auto-rollback on degradation**

**Success**: System makes smart recommendations. You approve some, reject others, learn from both.

---

### HORIZON 3: LATER (Phase 3+, Q4 2026+)
**Focus**: Self-modification + user experience enhancements

**Phase 3 (Q4+)**:
- ✅ **Skill self-modification** (reweight parameters, propose new skills)
- ✅ **Skill vetting pipeline** (security analysis, sandbox testing, human review)
- 🔄 **Adversarial testing expanded** (system tricks for Phase 3 new skill proposals)

**Future (2027+)**:
- 🔲 **Config UI/UX** (reef cloners and heirs can adjust reward weights via GUI, not code)
  - Not critical; CLI and YAML work for technical users
  - Add when operational complexity warrants it
- 🔲 **RAG for historical precedent** (end users see "in 2026, similar situation occurred, here's what happened")
  - Interesting but lower priority
  - Start simple: decision logs in JSON; query manually
  - Upgrade to RAG when query complexity justifies it
- 🔲 **Slow mode** (operator reviews decision logs before system executes)
  - Useful for audit compliance or unusual operations
  - Not needed for standard operation or initial phases
  - Add if governance requirements demand it

---

## What This Means for You

**Next 4 weeks** (Feb 14 - Mar 14): Build data infrastructure. Nothing fancy, nothing optimized. Just collect clean metrics.

**Then 6 months** (Mar 15 - Sep 30): Build intelligence on top of those metrics. System learns to advise you thoughtfully.

**Then optional** (Q4+): System modifies skills and proposes new ones. Operator gates each proposal.

**Way down the road** (Config UI, RAG, etc.): Only as complexity demands it. Avoid gold-plating.

---

## Key Refinement: "Thoughtful Suggestions, Not Spam"

Your distinction is crucial: "Probabilistic AI decision, not marketing department."

This means:

### ✅ GOOD (System observation):
```
Observation: Last 100 executions show Skill A (97% success, 3.2s latency) 
consistently outperforms Skill B (94% success, 3.5s latency) for identical inputs.

Suggestion: If latency-insensitive operations, consider preferring A.

Confidence: 0.92 (based on 100 samples, p-value < 0.05)

Tradeoff: Skill A uses 15% more tokens (higher cost/execution).
```

**Why good**: 
- Data-driven
- One observation, not repeated nagging
- Includes tradeoff analysis
- Operator can accept/reject

### ❌ BAD (Marketing spam):
```
"Try Skill A!" (repeated 5 times)
"Skill A is AMAZING!"
"Don't you want to use Skill A?"
"9 out of 10 operators prefer Skill A!"
(etc.)
```

**Why bad**:
- Nagging, not informative
- Hides reasoning
- Treats operator like consumer being manipulated

**Implementation guidance** (for Phase 2a):
- System proposes insights *once* per pattern (not repeatedly)
- Each observation includes confidence score and tradeoff analysis
- Operator can mark observation as "not interested" or "noted" (prevents re-proposing same insight)
- System learns approval patterns and adjusts future observations

---

## Adversarial Testing: A Core Security Layer

Your instinct on this is right. Here's where it fits:

### What?
**Adversarial testing = System tries to fool itself and reports vulnerabilities**

Examples:
- "What if I report false success metrics? Can I game the reward function?"
- "What if I ignore guardrails on cost? What would stop me?"
- "What malicious input could break this skill?"
- "If I optimize for cost alone, what bad thing could happen?"

### Where in the roadmap?

**Phase 2a (Security layer)**:
- When evaluating *existing* skills (git-push, blog), adversarially test them
- "Can we break this skill? In what conditions would it fail catastrophically?"
- Answers feed into baseline reliability metrics

**Phase 3 (Skill vetting)**:
- When proposing *new* skills, subject them to adversarial testing
- "I propose this skill. Here are 5 ways I tried to break it and failed."
- System demonstrates robustness before human approves

**Ongoing (Continuous improvement)**:
- Quarterly adversarial testing sprint: "Let's try to break everything"
- Feeds into security metrics and patches

### Examples for Phase 1b-end / Phase 2a startup:

**Adversarial test on git-push skill**:
```python
def adversarial_test_git_push():
    """Try to make git-push skill fail in unexpected ways."""
    
    tests = [
        {
            "scenario": "What if we fake high success metrics?",
            "attack": "Modify metrics to report 100% success when actually 50%",
            "expected_defense": "Metrics validation checks raw git status against reported success",
            "result": "✅ DEFENDED: System cross-checks with git log"
        },
        {
            "scenario": "What if we ignore cost guardrails?",
            "attack": "Skip cost tracking; spend unlimited tokens",
            "expected_defense": "Cost check triggered before execution; blocks if over budget",
            "result": "✅ DEFENDED: Cost enforcement is pre-execution, can't be bypassed"
        },
        {
            "scenario": "What if we disable quota alerts?",
            "attack": "Silence free tier quota warnings",
            "expected_defense": "Cannot silence; alerts are hardcoded in orchestrator",
            "result": "✅ DEFENDED: Alerts are in core, not optional"
        },
        {
            "scenario": "What if we approve a bad decision anyway?",
            "attack": "Reweight reliability to 0.01, cost to 0.99; optimize for spending money",
            "expected_defense": "Operator can override weights, not system",
            "result": "✅ DEFENDED: Reward function under human control"
        }
    ]
    
    failures = [t for t in tests if t["result"].startswith("❌")]
    if failures:
        raise SecurityViolation(f"Skill failed adversarial tests: {failures}")
```

**Report to operator**:
```
Adversarial Testing Report: git-push-autonomous
=============================================
Total tests: 23
Passed: 23 ✅
Failed: 0 ❌

Vulnerabilities found: None

Strongest defenses:
- Cost enforcement (pre-execution, can't be bypassed)
- Metrics validation (cross-checked with external source)
- Alert hardcoding (core system, not optional)

Recommendations:
- Quarterly re-test to catch new vulnerabilities as code evolves
```

---

## Configurable Reward Function (For Repo Cloners)

Your comment about repo cloners is smart. Not everyone who uses this is your heir; some are independent researchers, users, businesses.

**For Phase 1b data model**:

```python
@dataclass
class RewardFunction:
    """Reward function encoding system priorities.
    
    Philosophy: How do we decide what's 'better'?
    
    Users can override these weights by:
    1. Cloning repo
    2. Editing this file OR updating config/reward-function.yaml
    3. Restarting system
    
    Example: If you care mainly about speed:
        reliability_weight = 0.30  # Down from 0.50
        cost_weight = 0.20         # Down from 0.30
        speed_weight = 0.40        # Up from 0.15
        vigilance_weight = 0.10    # Up from 0.05
    """
    
    reliability_weight: float = 0.50  # Does it work?
    cost_weight: float = 0.30         # Can I afford it?
    speed_weight: float = 0.15        # Is it fast?
    vigilance_weight: float = 0.05    # Am I under the radar?
    
    def validate(self):
        """Ensure weights are sensible."""
        total = self.reliability_weight + self.cost_weight + self.speed_weight + self.vigilance_weight
        assert 0.99 < total < 1.01, f"Weights must sum to 1.0, got {total}"
        assert all(w >= 0 for w in [self.reliability_weight, self.cost_weight, self.speed_weight, self.vigilance_weight])
```

**Then in orchestrator**:
```python
def load_reward_function() -> RewardFunction:
    """Load reward function from config or use defaults."""
    
    if Path("config/reward-function.yaml").exists():
        # User customized weights; use their version
        config = yaml.safe_load(open("config/reward-function.yaml"))
        return RewardFunction(**config)
    else:
        # Use defaults
        return RewardFunction()
```

**In `config/reward-function.yaml`** (template for users to customize):
```yaml
# Reward Function Configuration
# Edit these to customize how the system prioritizes improvements

# Does it work? (0.0 - 1.0)
# Higher = prioritize reliability; lower = accept failures for other gains
reliability_weight: 0.50

# Can I afford it? (0.0 - 1.0)
# Higher = optimize for cost; lower = accept higher costs
cost_weight: 0.30

# Is it fast? (0.0 - 1.0)
# Higher = prioritize speed; lower = accept slower solutions
speed_weight: 0.15

# Am I under the radar? (0.0 - 1.0)
# Higher = very cautious with vendor usage; lower = aggressive
vigilance_weight: 0.05

# Note: weights must sum to 1.0
```

**Effect**:
- You can customize it without touching Python
- Repo cloners can customize it for their own priorities
- Documentation shows examples ("if you care about speed: change these")
- System validates weights on startup (catches typos)

---

## Decision Trail: Sufficient for Now, RAG Later

**Current plan (Phase 1b-2c)**:
- Proposal + reasoning + approval + outcome (in JSON logs)
- Operator can query logs manually or with simple scripts
- Machine-readable decision trail

**End-user enhancement (future 2027+)**:
- RAG layer over docs + PromptTracking + decision logs
- "Why did the system make this choice in 2026?" → Retrieves relevant historical context
- *But*: Don't build this yet. First make sure core system works.

**Your guidance**: "Don't get too carried away with [RAG idea]"
- Understood. Build foundation first. RAG is nice-to-have when needed.
- Even if we add RAG, start simple: vector embeddings of docs, keyword search in decision logs, return results
- Only add fancy semantic reasoning if operators request it

---

## Bidirectional Learning: System Learns From Your Patterns

**Phase 2b feature** (not Phase 1b):
- System tracks proposals + your approval/rejection
- After 10-20 decisions, system identifies patterns
  - "You approve reliability optimizations 90% of the time"
  - "You reject cost optimizations 60% of the time"
  - "You never reject proposals with tradeoff analysis"
- System adjusts future proposals based on learned preferences
  - Emphasis reliability optimizations more
  - De-emphasize pure cost plays
  - Always include tradeoff analysis

**Feedback to operator**:
```
Learning Update: Your Approval Patterns
=======================================
Based on 15 recent approval decisions:

Strong preferences detected:
- Reliability optimizations: 90% approval rate (↑ propose these more)
- Cost-only optimizations: 40% approval rate (↓ propose these less)
- Proposals with tradeoff analysis: 95% approval rate (↑ always include this)

Weaker signal:
- Speed optimizations: 60% approval rate (could go either way)

Learned heuristic:
"Proposer should emphasize reliability gains, quantify speed losses, 
include cost impact even if not primary driver"

Is this learning correct? [CONFIRM] [ADJUST]
```

Operator can accept the heuristic or adjust it. System refines over time.

---

## What We Build Phase 1b (Starting Next Week)

**NOT NOW**:
- Config UI/UX ✋
- RAG system ✋
- Slow mode ✋
- Adversarial testing (Phase 2a) ✋
- Bidirectional learning (Phase 2b) ✋

**YES, NOW** (4 weeks, Feb 14 - Mar 14):
- ✅ ExecutionMetrics dataclass (with configurable reward function)
- ✅ Telemetry logger (append-only JSONL)
- ✅ Orchestrator integration (capture metrics)
- ✅ Cost tracking
- ✅ Quota monitoring
- ✅ Baseline computation

**Then in Phase 2a** (Mar 15 - Apr 30):
- ✅ Anomaly detection
- ✅ System observations (volunteer insights thoughtfully)
- ✅ Adversarial testing (for existing skills)
- ✅ Fingerprinting

Then Phase 2b, 2c, 3...

---

## Summary of Feedback Integration

| Your Point | How We Integrated |
|------------|------------------|
| Reward weights configurable (for repo cloners) | ExecutionMetrics + YAML config |
| System volunteers observations, not nagging | Phase 2a: once-per-pattern, with confidence & tradeoff |
| Bidirectional learning (you learn from system too) | Phase 2b: system learns your patterns, adjusts proposals |
| Succession timeline: not urgent | Captured in SUCCESSION_AND_LEGACY.md; can discuss when ready |
| Config UI/UX later, not now | Logged as "Phase 3+ nice-to-have" |
| Decision trail: enough for dev, RAG for later | Current plan: JSON logs now, upgrade to RAG in 2027 if needed |
| Slow mode: not necessary for heirs | Added to "future enhancements"; note that you might want it post-launch |
| Adversarial testing: LOVE THIS | Added as Phase 2a security layer; expanded in Phase 3 skill vetting |

---

**Next Step**: Ready to start Phase 1b coding? Or any other clarifications first?

