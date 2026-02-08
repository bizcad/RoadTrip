# How We Built a Trusted AI Skill: A Case Study in Rigorous Development

**Date**: February 8, 2026

---
I, like a lot of you, have been fascinated by OpenClaw (ne Moltbot, ne Clawdbot), and horrified by the number of vulnerabilities that it opens up if you run it on your main machine; not to mention the possible leaking of (shudder) API keys. So I decided to build something safer, something verifiable, something that could be trusted to have access to the wild world of the internet.

I started by building a Road Trip monitor that could help me drive across country more safely. Start with a google map and overlay real-time traffic data, weather conditions, and rest stops. It should be easy using existing APIs and a bit of scripting and an AI. Right? Not so fast. It turns out that even a seemingly simple task like this can quickly become complex when you want it to be reliable, secure, and verifiable. How do I know that I am not giving up my secret keys or exposing my system to vulnerabilities?

I wanted to let Claude build the app as much as possible, but I needed the app to access the internet and I needed to be able to access it while I was on the road. So I decided to build a system that could run anywhere, with minimal trust required. I wanted to use Claude skills and MCPs, but how do I trust them?

## The Moment

This morning, I had a simple goal: implement a skill that generates semantic commit messages for git repositories so that Claude could automatically stage, generate meaningful commit messages, commit, and push changes. I wanted a 1-button push solution. Not particularly complex, not particularly novel. But here's what made it interesting: I wanted to do it with *complete transparency*, *verifiable integrity*, and *zero shortcuts*.

By noon, Claude and I had built, tested, and verified a complete skill system with and orchestrator and a few skills:
- 1,500+ lines of original code (well I didn't write it, Claude wrote most of it)
- Three-tier cost optimization (99% free, 1% LLM fallback)
- Comprehensive test infrastructure  
- End-to-end GitHub verification
- Expandable as new skills are added.

And more importantly: **I know exactly what was built, why it was built that way, and that it worked.**

But how do I prove it? How do you know that the system is trustworthy? The answer is simple: **you verify it.** Verification isn't optional—it's the foundation of trust. 

---

## The Challenge: Staying Honest at Scale

When you're building AI agents and skills, you face a fundamental problem:

> **How do you stay honest when the system is complex?**

The moment your skill does something non-trivial, verification gets hard. You run the code, it produces output, but did it produce the *right* output? Did it make the right decisions? Or did it just look like it did because you didn't inspect deeply enough?

There's a name for this in engineering: **the rigor problem**. It's why surgical teams have checklists. It's why flight crews have redundant instruments. It's why NASA counts down from T-minus 10, not 10, 9, 8...

In AI development, the rigor problem is *worse* because a system can fail in non-obvious ways. 

---

## The Architecture: Three Decisions

I made three architectural decisions that turned out to be surprisingly powerful:

### 1. **The Immutable Prototype**

The existing system (`git_push.ps1`) was my reference implementation—the thing I trust because I understand every line. So I did something unusual: I made it completely immutable.

No integration through modification. No "just add this one line." No shortcuts.

Instead, I built a separate wrapper that calls my new skill independently, and documented the manual integration step:

```powershell
# User manually copies the message from the skill
$message = .\invoke-commit-message.ps1 -StagedFiles @("file1", "file2")

# User passes it to the trusted prototype
.\git_push.ps1 -Message $message
```

This seems backwards—why separate them? Because **mutual independence is verification**. I can run them both on the same input and see if they agree. If they disagree, I don't have circular dependency—I have a diagnostic signal.

---

### 2. **The Invisible Test Infrastructure**

The second decision came from a subtle problem: test files contaminate test results.

Think about it. I have a tool that generates commit messages based on which files were staged. I want to test that tool. So I create a test script. But now that test script is staged. Which means the tool generates a message about the test script. Which changes the test results...

This is a **circular reference**. It's subtle but deadly.

The solution was simple: add test files to `.gitignore`.

Test infrastructure is metadata, not deliverables. It should be invisible to the system being tested. This is why you don't check `node_modules/` or `__pycache__/` into version control—not because they're useless, but because they would corrupt the test results.

By invisible testing, I eliminated an entire class of bugs.

---

### 3. **Oracle-Based Verification**

The deepest insight came last: **use a simpler system to verify a complex one**.

I had two tools:
- `git_push.ps1` (my reference, simple heuristics, 200 lines)
- `commit_message.py` (my new skill, complex heuristics, 700 lines)

Instead of testing them in isolation, I tested them against **each other**, on **the same input**.

```
Test Results:
✓ Tool 1 generates message: "chore: update 3 files (+0 ~3 -0)"
✓ Tool 2 generates message: "chore: update multiple modules"
✓ Messages differ (expected—different heuristics)
✓ Both follow Conventional Commits format
✓ Both identified correct semantic category
Status: PASSED
```

The messages are *slightly different* (one lists counts, one describes semantics). But both are valid. Both are correct. And I know this because I have an oracle validating both against the same spec.

This is more powerful than testing either tool in isolation.

---

## The Verification: The Ultimate Test

After all the code was written and tested, I did something that seems obvious but is surprisingly rare in AI development:

**I checked what was actually published.**

I went to the GitHub web UI. I looked at the commit. I read the files. I verified that:
- The commit message was exactly what we expected
- The files were exactly what we expected
- The timestamps were recorded correctly
- The integrity chain was unbroken

Commit: `33da9da03291942e00b6baf016917cc897eff241`
Message: `chore: update 4 files (+0 ~3 -0)`
Files: `.gitignore`, `invoke-commit-message.ps1`, `commit_message_models.py`, `Phase_1b_Execution_Log.md`

Everything matched.

This is what you do when you actually care about the output being correct. You don't just run the tool. You verify the artifact in the system where it matters.

---
# I am calling it "Verified Agentic Work" or "Signed Agentic Work"

## Why "Signed Agentic Work" Matters for AI Development

Here's what I realized building this:

**"Signed" doesn't just mean cryptographic signatures.**

Cryptographic signatures tell you the code came from a specific person and wasn't tampered with. That's valuable. But it's not enough.

True "signed agentic work" means:
1. **Immutability** — Core services are protected, not modified
2. **Transparency** — Test infrastructure is visible and honest
3. **Verification** — Results are checked independently, not assumed
4. **Traceability** — Every output is recorded in the system where it matters

When you combine these, you get something cryptocurrency folks and Federal Express call a "chain of custody"—an unbroken chain of evidence that each step was done correctly.

---

## The Cost

One more thing worth mentioning: **the cost of rigor is not what you think.**

Building the tool: ~4 hours
Building the test infrastructure: ~2 hours  
Building the verification: ~1 hour (mostly manual inspection)

*Total: ~7 hours*

Creating perfect code with shortcuts and crossing your fingers? Also about 2 hours of coding, but then 3-4 weeks of debugging based on corner cases you missed.

Rigor is not expensive. Ignorance is expensive.

---

## What's Next

The skill is working. The tests are passing. The verification is complete. The code is public.

Next week we're building:
1. An orchestrator that chains multiple skills together
2. An authorization validator that controls what skills can do
3. Full end-to-end integration with multiple tools

And we're applying the same rigor to all of it.

Because if you're going to build trusted AI agents, you can't cut corners on the infrastructure they run on.

---

## For the Skeptics

"Nice story, but did you actually verify this? Or are you just telling yourself you did?"

Fair question. Here's what we did:
- ✅ Wrote 1,500+ lines of production code
- ✅ Built a comprehensive test suite
- ✅ Ran the tests (PASSED, with diagnostics)
- ✅ Pushed the code to GitHub
- ✅ Opened the GitHub web UI and read the commit details directly
- ✅ Verified that what I expected to see is what I actually saw
- ✅ Documented the process for future review

If you want to verify this independently, clone the repo, review the code, run the tests, and check the commit yourself.

That's the whole point.

---

## The Real Insight

The most important skill in building trusted AI systems isn't coding. It's not even algorithm design.

It's **knowing how to verify that you're right, and being willing to do it.**

This morning proved that's not just possible at the tooling layer. It's foundational to everything we're building.

---

**Nick Stein (aka. Bizcad)**  
*Building the framework for trustworthy agentic AI*  
*RoadTrip Project, Phase 1b Option A MVP*
