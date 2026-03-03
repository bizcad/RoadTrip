# NateBJones-There-are-4-skills-in-2026
## Visual table

| Layer | Skill Domain | Purpose | Primary Owner(s) | Readiness Signals / Metrics |
|---|---|---|---|---|
| Meta | Prompt Craft | Produce clear, bounded task requests and expected outputs. | Individual contributor, prompt author | Fewer clarification loops; stable output format adherence; lower rework per task |
| Meta | Context Engineering | Design the full information environment required for solvable tasks. | Context architect, lead engineer | Retrieval precision/recall trends; reduced context clash; improved first-pass task success |
| Meta | Intent Engineering | Encode goals, trade-offs, and escalation boundaries for autonomous behavior. | Product lead, domain owner, governance lead | Fewer “technically right, strategically wrong” outcomes; escalation correctness rate |
| Meta | Specification Engineering | Create long-horizon executable specs for multi-session, multi-agent work. | Spec engineer, tech lead | Acceptance-criteria pass rate; handoff success across sessions/agents |
| Execution | Memory Engineering | Manage short/long-term memory quality, retention, and rehydration. | Platform engineer, AI engineer | Memory conflict rate; stale-memory incidents; summary compression quality |
| Execution | RAG Engineering | Deliver high-signal just-in-time knowledge with minimal noise. | Data/retrieval engineer | Top-k relevance; hallucination-with-source rate; freshness latency |
| Execution | Tool/Action Engineering | Define safe, reliable, permission-scoped tool invocation paths. | Backend engineer, security engineer | Tool failure rate; retry success; authorization-denied correctness |
| Execution | Instruction Architecture | Layer system/developer/task constraints with deterministic precedence. | AI engineer, governance lead | Instruction conflict incidents; policy override violations |
| Execution | Output Contract Engineering | Enforce structured, machine-usable outputs for downstream automation. | API engineer, integration engineer | Schema validation pass rate; parse failure rate; downstream pipeline breakage |
| Governance | Evaluation Engineering | Prove quality and safety with deterministic + rubric-based evals. | QA/evals engineer, reviewer | pass@k, pass^k, regression failure rate, drift alerts |
| Governance | ContextOps | Version, test, rollout, observe, and rollback context bundles like code. | DevOps/MLOps, platform owner | Context release cadence; rollback MTTR; A/B lift from context revisions |

### Usage
- Treat the first four rows as strategic disciplines and the remaining rows as implementation/governance capabilities.
- For each new feature, identify one owner and one metric per row to avoid gaps in execution.
- Use this table as a checklist in specs, PR templates, and release gates.

## Summary
This vlog argues that “prompting” is no longer a single chat skill. In 2026, with long-running autonomous agents, useful prompting is a stack of four disciplines that must work together.

### Core thesis
- 2025-style chat prompting is still useful, but now only table stakes.
- The performance gap comes from designing the full execution context before the agent starts, not from clever phrasing in a live chat.
- As agent autonomy increases, communication quality, specification quality, and evaluation rigor become leadership-level skills.

### The 4 prompting skills
1. **Prompt Craft (table stakes)**
  - Clear instructions, examples/counterexamples, guardrails, explicit output format, and conflict-resolution rules.
  - Best for synchronous, session-based interaction.

2. **Context Engineering**
  - Curating the optimal token environment: system prompt, memory, tools, retrieved docs, and history.
  - Emphasis shifts from “better wording” to “better context infrastructure.”

3. **Intent Engineering**
  - Encoding goals, values, trade-offs, decision boundaries, and escalation rules.
  - Prevents technically correct but strategically wrong outcomes.

4. **Specification Engineering**
  - Writing complete, structured, executable specs that agents can run for long periods without human intervention.
  - Treating the organization’s document corpus as agent-readable specifications.

### Five primitives for specification engineering
- Self-contained problem statements
- Acceptance criteria
- Constraint architecture (must, must not, prefer, escalate)
- Decomposition into independently verifiable units
- Evaluation design with repeatable test cases and regression checks

### How the “Context Engineering Explained” bubbles map to the talk
The Venn diagram model is consistent with the transcript’s message: all of these layers jointly form context, and their overlap is what makes autonomous execution reliable.

- **Outer boundary: Context** = the full information environment, not just user text.
- **State / short-term memory + long-term memory** support continuity and stability across sessions.
- **Instructions / system prompt** sets role and operating constraints.
- **RAG (center overlap)** bridges user intent with relevant knowledge, tools, and memory.
- **Available tools** define what actions are possible.
- **User prompt** sets immediate task intent.
- **Structured output** enforces predictable, machine-usable results.

### Practical takeaway
To scale from chat assistance to autonomous, high-trust agent work, teams should progress through the stack in order: strong prompt craft, robust context engineering, explicit intent infrastructure, and finally executable specification engineering with eval-driven gates.

## Analysis
Nate’s framework is strongest when interpreted as a layered model: the “four skills” are top-level disciplines, while context engineering unfolds into a broader systems practice. Your Venn diagram and Additional Resources make this explicit.

### 1) Synthesis: Nate’s 4 disciplines + Lütke’s framing
Nate’s argument is that long-running agents break synchronous assumptions and force pre-encoded clarity (prompt, context, intent, specification). Lütke’s framing sharpens this by treating context engineering as communication infrastructure, not prompt wordsmithing: “provide all context needed for plausible solvability in one go.” See the references you included: [philschmid](https://www.philschmid.de/context-engineering), [redis](https://redis.io/blog/context-engineering-best-practices-for-an-emerging-discipline/), [turingcollege](https://www.turingcollege.com/blog/context-engineering-guide).

Interpretation:
- **Nate** defines the strategic stack.
- **Lütke-style context engineering** explains how to operationalize the stack.
- Together, they imply more than four practical competencies.

### 2) Why the Venn implies more than four human skills
The Venn bubbles (state, long-term memory, instructions, RAG, tools, user prompt, structured output) are implementation domains. Each domain requires distinct engineering decisions, ownership, and evaluation loops.

That yields a practical capability tree:

1. **Prompt Craft** (instruction quality)
2. **Context Architecture** (what enters context and why)
3. **Intent Modeling** (goal/priority/escalation logic)
4. **Specification Engineering** (long-horizon executable artifacts)
5. **Memory Engineering** (state, retention, summarization, rehydration)
6. **RAG Engineering** (retrieval quality, ranking, freshness, anti-noise filtering)
7. **Tool/Action Engineering** (tool contracts, routing, permissions, retries, failure handling)
8. **Output Contract Engineering** (schema design, parser safety, downstream reliability)
9. **Evaluation Engineering** (capability+regression suites, drift detection, pass@k/pass^k policy)
10. **ContextOps** (versioning, rollout, A/B testing, rollback, observability)

This aligns directly with your citations around reusable context bundles and system-level design: [growthmethod](https://growthmethod.com/context-engineering/), [blog.langchain](https://blog.langchain.com/the-rise-of-context-engineering/), [addyo.substack](https://addyo.substack.com/p/context-engineering-bringing-engineering), [promptingguide](https://www.promptingguide.ai/guides/context-engineering-guide).

### 2.1) Memory Engineering (embellished): 7 memory levels + Thinking Fast and Slow
Your memory architecture document argues that “memory is a system,” not a single feature. That is exactly the right framing for production agents: each memory lane has a different purpose, retention profile, and reliability requirement. See: [7 levels of memory](7%20levels%20of%20memory.md).

#### Practical separation of the 7 levels
1. **Auto Memory (long-term memory)**
  - Stable truths and durable decisions (`what is true unless changed`).
  - Low write frequency, high validation, explicit provenance.

2. **Session Bootstrap (prospective memory)**
  - What must be resumed next (`what needs to happen now`).
  - High read priority at session start, short TTL, freshness-critical.

3. **Working Memory**
  - Active scratchpad, hypotheses, temporary state.
  - Fast writes/reads, aggressive pruning, periodic checkpoint summaries.

4. **Episodic Memory**
  - Time-stamped event trace (`what happened, when, and why`).
  - Essential for auditability, replay, and incident forensics.

5. **Knowledge Graph (semantic memory)**
  - Entity/relationship model (`how concepts connect`).
  - Best for dependency reasoning and cross-domain joins.

6. **Hybrid Search (associative recall)**
  - Multi-path retrieval across lexical, semantic, and graph signals.
  - Used to reduce blind spots and recover non-obvious but relevant context.

7. **RLM-Graph (chunking at scale)**
  - Partition-and-merge strategy for oversized context queries.
  - Keeps reasoning coherent when direct window loading would fail.

#### Fast vs Slow cognition mapping (agent design)
Applying *Thinking, Fast and Slow* as a design primitive gives a practical control policy: fast paths for fluency, slow paths for correctness under uncertainty. See: [ThinkingFastAndSlow](ThinkingFastAndSlow.md).

- **Fast path (System 1 style)**
  - Uses Bootstrap + Working + lightweight retrieval.
  - Optimized for responsiveness and routine tasks.
  - Guardrails: confidence thresholds, low-risk action limits.

- **Slow path (System 2 style)**
  - Invokes deeper episodic replay, semantic graph traversal, richer RAG, and explicit checks against constraints/spec.
  - Triggered by ambiguity, novelty, high-impact actions, policy-sensitive domains, or low-confidence outputs.
  - Produces structured rationale and verifiable artifacts.

#### Escalation policy (recommended)
- If confidence is high and risk is low: stay in fast path.
- If confidence drops or conflict appears across memory lanes: escalate to slow path.
- If slow path still detects unresolved conflict: escalate to human review with evidence bundle (episodes + retrieved sources + applied constraints).

#### Why this matters for context engineering
This separation prevents two common failure modes:
- **Amnesia** (not enough durable memory)
- **Memory hoarding/conflict** (too much stale or contradictory memory)

Operationally, this turns memory from a passive store into an active decision fabric that supports both speed and reliability—fully aligned with the transcript’s move from chat prompting to long-horizon autonomous execution.

### 3) Deepened interpretation of “communication discipline”
“Communication discipline” here is not just better wording; it is structured transmission of intent across humans and machines:

- **Human → Model clarity**: self-contained tasks, explicit assumptions, defined constraints.
- **Team → Model consistency**: reusable context packages (“context APIs”) with versioning and shared schemas.
- **Model → System reliability**: structured outputs and eval-gated acceptance.

This is consistent with the cross-functional angle in your resources: product, UX, and engineering co-design context as a shared artifact, not an individual prompt habit. See [acquired](https://www.acquired.fm/episodes/how-to-live-in-everyone-elses-future-with-shopify-ceo-tobi-lutke), [fs](https://fs.blog/knowledge-project-podcast/tobi-lutke-2/), [news.aakashg](https://www.news.aakashg.com/p/context-engineering).

### 4) Practical implications for this transcript’s framework
The transcript’s 4-skill model remains valid, but production adoption requires two added lenses:

- **Execution lens** (build and run the context system): memory, RAG, tools, schemas.
- **Governance lens** (keep it correct over time): evals, version control, rollout policy, relevance pruning, feedback loops.

References from your list supporting this operations-first view: [intuitionlabs](https://intuitionlabs.ai/articles/what-is-context-engineering), [matthopkins](https://matthopkins.com/technology/context-engineering-practical-guide/), [praella](https://praella.com/hi/blogs/shopify-news/the-art-of-context-engineering-revolutionizing-ai-interactions-for-optimal-performance), [linkedin](https://www.linkedin.com/posts/sriarun-marimuthu-235416237_ai-llm-contextengineering-activity-7349828794079211520-cjFo).

### 5) Final conclusion
Your instinct is correct: there are more than four “skills” in practice.

- The four are the **strategic disciplines**.
- The Venn bubbles expose the **operational skill domains** needed for real systems.
- The Additional Resources support treating context as **engineered infrastructure** with lifecycle management, not static prompt text.

In short: the future-proof model is **4 top-level disciplines + operational context engineering stack + eval-driven governance**.

## Transcript
f You're Prompting Like It's Last Month, You're Already Late
0:00
If you're prompting like it's last month, you're already too late. And I'm not just doing that for clickbait. If
0:05
you haven't updated how you think about prompting since January 2026, you're already behind. Opus 4.6, Gemini 3.1
0:14
Pro, and GPT 5.3 codecs have all shipped in the past few weeks with autonomous
0:19
agent capabilities that make the chatbased prompting most people are practicing functionally obsolete for
0:26
serious work. These models don't just answer better. They work autonomously for a long time, for hours, for days
0:33
against specs without really checking in. That changes what good at prompting means on a fundamental level. And it's
0:39
time to revisit how we think about prompting as a result. Not because prompting stopped mattering. It actually
0:46
matters more than ever, but because the word prompting is now hiding four completely different skill sets, and
0:53
most people are only practicing one of them. And the gap between the people who see all four of them and the people who
0:58
don't is already 10x and widening. In this piece, I'm going to lay out what those four skills are, why the
1:04
distinction matters now, and exactly how to build the skills you're missing. This builds on my earlier work on intent
1:10
engineering, but it goes way beyond it to lay out a full framework for how to think about prompting post February
1:16
2026. Intent engineering is just one layer in a larger stack. This is the
1:21
full stack for prompting post February, post these new autonomous models. First,
1:26
what changed? The prompting skill that mattered since 2024 has been really conversational. You sit in a chat
1:33
window, you type a request, you read the output, you iterate, you get better at phrasing things, you provide examples,
1:39
you structure instructions. If you're good at that, and if you've been following this video series, you
1:44
probably are. You've been building real skills. They work. you're faster than you were a year ago. But that
1:51
fundamental chatbased skill has a ceiling. And in early 2026, a lot of
1:56
people are hitting it because the models have stopped really being chat partners and started being workers. Workers that
2:03
run for a long time. I'm not kidding when I say days and sometimes weeks. And
2:08
the thing about a worker that runs for a long time is that everything you relied on in a conversation, like your ability
2:15
to catch mistakes in real time, your ability to provide missing context accurately when the model asks, your
2:21
ability to course correct when things drift. All of that must be encoded before the agent starts. Not during the
2:29
course of a conversation, but at the top. This is a fundamentally different skill. It's not a harder version of the
The 10x Gap: Same Model, Same Tuesday, Different Skills
2:35
same skill. It's actually different. I've talked before about the importance of thinking about prompting even in the
2:41
chat window as providing the relevant context for the LLM to provide you an
2:47
accurate response. But this goes way beyond that. If you were giving an agent
2:53
a longunning task, which is where most of AI is going, even if you're not a coder, then you have to think not about
3:01
how do I build for a chat response, but how do I build for economically real work that this agent will do and provide
3:08
the agent the relevant context for that. And this shift is happening really quickly. Between October of 2025 and
3:15
January of 2026, in just 3 months, the longest autonomous cloud code sessions
3:20
nearly doubled, and they've doubled again since then. Agents are running into the hundreds and thousands in
3:25
production systems at major companies. And this is just from publicly available information. We have Telus reporting
3:31
that they have 13,000 custom AI solutions internally. We have Zapia reporting that they have over 800 agents
3:37
internally. Look, whenever they release a press release, you got to assume that company feels behind and is releasing
3:44
something to help them feel better about themselves. The companies that are really serious about AI don't feel the
3:49
need for press releases and have an order of magnitude or more agents. So, this is not about a world that is
3:54
coming. This is about a world that has landed. But this still might not feel concrete enough for you. So, let me talk
4:00
to you about a random Tuesday. Two people sit down with the same model, same subscription, same context window.
4:06
One of them uses 2025 skills. You type a request, you get back something that is
4:12
80% right. You spend 40 minutes cleaning it up and you have a good use of AI
4:17
because you saved it a lot of time. It might have saved 50% on your time, might have saved 60%, maybe higher. Let's make
4:23
the gap concrete. Let's say two people are sitting down with the same model on a Tuesday morning in February of 2026.
4:30
Same subscription, same context window. The only difference is that one of them is using 2025 prompting skills and one
4:36
of them is using 2026 prompting skills. So the 2025 person types a request and
4:42
they're asking for a PowerPoint deck, right? They get back something that's about 80% correct. Maybe there's some formatting issues. Maybe the font has
4:48
some collisions in it. Maybe there's some styling issues. They spend about 40 minutes cleaning it up, but they're
4:54
pretty happy because this deck would have taken two or three hours. That's a 2025 prompting skull application. it would have been good in 2025.
5:01
Person B sits down with 2026 prompting skills. They write a structured specification in 11 minutes. They take
5:07
longer to prompt. Then they hand it off to the same chatbot, but they're thinking of it and using it as an
5:14
autonomous agent. They go to make coffee. They come back to a completed PowerPoint that hits every quality bar
Toby Lutke on Context Engineering as Communication Discipline
5:20
defined up front. And they're able to do this for five other decks before lunch. In other words, they are now doing a
5:26
week's worth of work in a morning easily. Same model, same Tuesday, 10x
5:32
gap. And if you want to replicate this, you can replicate this experiment directly in Claude Opus 4.6 in the
5:39
co-work model, which is available on Windows and Mac. And you can see exactly how this plays out. And this did not
5:45
happen because the person with 2026 prompting skills is smarter or because she's more technical. It's because she's
5:52
practicing a different skill than person one and person one doesn't know that kind of prompting skill exists. I think
5:59
it's worth paying attention to Shopify CEO Toby Lutkkey here. Unlike most CEOs,
6:04
Toby is a technical guy and he does not just dig into AI from a LinkedIn perspective. He has a folder of prompts
6:11
that he runs against every new model release and he really deeply thinks about how new model releases change his
6:18
workflow. He uses the term context engineering because he believes the fundamental skill that we're all facing
6:24
is the ability to state a problem with enough context in a way that without any additional pieces of information, the
6:30
task becomes plausibly solvable. I think that's a really elegant way to describe what person B did in the example I just
6:38
showed you. Person B put all of the information that the model needed to
6:43
build a deck in one task very clearly defined and the model could just go to
6:48
work. This isn't about clever prompt tricks. This isn't about magical words that an AI can use to produce a better
6:54
output. It's about a communication discipline. Can you state a problem so completely with so much relevant
7:01
surrounding information that a capable system can solve it without going out and fetching more context? Can you make
7:08
your request as self-contained as possible? This is a really big deal because it demands a much higher bar for
7:14
communication from us humans than we're used to. And that's something that Toby called out when he reflected on the
7:20
impact of AI on his own leadership style. One of the things he mentioned is that by being forced to provide AI with
7:27
complete context, he is now better at communicating as a CEO. His emails are
7:32
tighter, his memos are better, his decision-making frameworks are stronger, and Toby has gone farther than most
7:37
people thinking about the implications of context engineering. I think one of his most provocative assessments is that
7:43
a lot of what people in big companies call politics is actually bad context
The Four Disciplines Framework
7:50
engineering for humans. What he suggests is that essentially good context engineering would surface disagreements
7:56
about assumptions that are never surfaced explicitly but play out as politics and grudges in large companies.
8:03
And he says that happens because humans tend to be sloppy communicators who rely on shared context that doesn't actually
8:10
exist. I think that's a really interesting thesis. I think one of the implications of getting this February
8:16
2026 prompting lesson deeply ingrained in ourselves is that our communication
8:22
humanto human is likely to improve and our organizations are likely to have cleaner decisioning and cleaner
8:28
communication even between humans as a result. So I bet you're wondering what are these four disciplines? What does it
8:34
mean when prompting becomes multiple skills that we need to learn? Well, I don't want to hide the ball here. Here
8:40
is the framework that I would lay out that describes what prompting should be in February 2026. And I've built it to
8:47
be futurep proof. So we look at the direction that agents are going, how they're developing this year. These four
8:53
disciplines are going to matter even as we expect agents to continue to scale. This represents a significant update on
9:00
how I've taught prompting before 2026 because the way we prompted before 2026
9:06
was helpful as a foundation. You're not losing something by having learned it, but it's not enough as agents get more
9:13
capable. And I think we're due for a reset. So, fundamentally, prompting is the broad skill of providing input to AI
9:20
systems so that they can do useful work. Prompting has diverged into four distinct disciplines, but it's not
9:26
taught that way. And so, I'm laying this out for the first time here. Each of these disciplines is operating at a
Discipline One: Prompt Craft as Table Stakes
9:32
different altitude and time horizon. And you need to understand them all to prompt well. Just because they're not
9:37
often prompted this way, just because they're not often taught this way, doesn't mean that good prompters don't
9:44
intuitively know this. What I'm taking is intuitive knowledge that I see in excellent prompters and boiling it down
9:50
into four key disciplines that you can practice and learn from. And these build on each other. If you skip one, I'm
9:56
presenting them in order. If you skip one, you're creating the kind of failures we tend to see at scale in the
10:01
enterprise, but you're creating it for yourself in your own prompting. And I'll kind of get at what that means and
10:06
you'll get the idea. So discipline one is prompt craft. This is the original
10:12
skill. This is the skill I have taught and many others have taught for the last year or two. It's synchronous. It's
10:18
sessionbased and it's an individual skill. You you sit in front of a chat window. You write an instruction. You
10:24
evaluate the output. Then you iterate. The skill here is knowing how to structure a query. And I've talked a lot
10:30
about this in the past. I'll rehash it briefly here. You must have clear instructions. You must include relevant
10:37
examples and counter examples. You need to include appropriate guard rails. You
10:42
need to include an explicit output format. And you should be very clear about how you resolve ambiguity and
10:48
conflicts. So the model doesn't have to make it up on the fly. This is what anthropics prompt engineering
10:53
documentation covers. Open AI talks about this. Google talks about this. It's on a thousand blog posts and
11:00
LinkedIn courses. Prompt craft has not become irrelevant. Don't hear that. It's
11:05
just become table stakes. It's sort of the way knowing how to type with 10 fingers was once a professional differentiator and now it's just table
11:12
stakes. It's just assumed. If you can't write a clear, well ststructured prompt in 2026, you're the person in 1998 who
11:20
couldn't send an email. Is it important to be able to do it? Yes. Is it going to differentiate you in the workforce? No,
11:26
not really. The key shift is that promptcraft was the whole game when AI interactions were synchronous and
11:33
sessionbased. You wrote something, you got something back, and you refined it in real time. As a human interacting
11:39
with that model, you were acting as the intent layer, as the context layer, and as the quality layer so that longunning
11:46
tasks could get done. You did all the breaking out of those tasks. That model of prompting broke the moment agents
11:53
started running for hours without checking in. Discipline 2 we've been talking about for a few months now. It's
11:58
called context engineering. Enthropic published the foundational piece on this back in September of 2025, but there's a
Discipline Two: Context Engineering
12:05
lot of other good pieces out there as well. I've written a fair bit on it. I define context engineering as the set of
12:11
strategies for curating and maintaining the optimal set of tokens during an LLM
12:17
task. And that's not just me defining that. That's a pretty commonly held definition. Wang Shane's Harrison Chase was even bluntter about what context
12:24
engineering is during a recent Sequoia Capital interview when he said everything is context engineering. It
12:29
actually describes everything we've done at lane chain without knowing the term existed. So that's actually somewhat
12:35
dangerous because context engineering is only one of four levels and people have
12:40
misunderstood it to mean everything. And one of the things I'm trying to get us to move toward is a world where we
12:45
understand context engineering as a specific skill where we're providing relevant tokens to the LLM for
12:52
inference. And yes, it is certainly foundational. It is certainly significant. It is where the industry's
12:57
attention is focused today. It is the shift from crafting a single instruction to curating the entire information
13:03
environment and agent operates within. all of the system prompts, all of the tool definitions, all of the retrieved
13:09
documents, all of the message history, all of the memory systems, the MCP connections. The prompt you write might
13:15
be 200 tokens. The context window it lands in might be a million. Your 200 tokens are 002% of what the model sees.
13:22
The other 99.98% that's context engineering. This is the discipline that produces claw.md files,
13:30
agent specifications, rag pipeline design, memory architectures. It's the discipline that determines whether a
13:36
coding agent understands your project's conventions, whether a research agent has access to the right documents,
13:41
whether a customer service agent can retrieve relevant account history. Anthropics engineering team identified
13:47
the core challenge precisely. LLM degrade as you give them more information. That's correct. They do.
13:54
And the point therefore is to include relevant tokens because the issue is not that they can't hold the tokens. It's
14:01
that retrieval quality does drop as context grows. The practical implication
14:06
is that people who are 10x more effective with AI than their peers are not writing 10x better prompts. They're
14:13
building 10x better context infrastructure. Their agents start each session with the right project files,
14:19
the right conventions, the right constraints already loaded. The prompt itself can be relatively simple because
14:25
the context does the heavy lifting. I have seen this for myself as I've built out my own context engineering
14:31
scaffolding. And if you're wondering how to do it for yourself, I'm putting a guide together with this video over on
14:36
the Substack and I think it'll be helpful. Discipline number three. This one we don't talk a lot about. I think
14:42
is where we're going as these agents start to do much longer autonomous running tasks. I wrote about this one at
14:48
length in a prior piece. I did a video on it. I'm going to be brief here. I'm going to contextualize where it sits in
14:54
the stack. Context engineering tells agents what to know. Intent engineering
14:59
tells agents what to want. It's the practice of encoding organizational purpose, your goals, your values, your
15:06
trade-off hierarchies, your decision boundaries into infrastructure that agents can act against. Claro story is
15:13
the proof case I talked about. Their AI agent resolved 2.3 million customer conversations in the first month, but it
15:19
optimized for the wrong thing. It slashed resolution times, but it didn't optimize for customer satisfaction. And
Discipline Three: Intent Engineering
15:26
as a result, CLA got into big trouble and had to rehire a bunch of human agents and is still dealing with the
15:32
customer trust aftermath. So, intent engineering sits above context engineering the way strategy sits above
15:39
tactics. You can have perfect context and terrible intent alignment. You cannot have good intent alignment
15:45
without good context, though, because the agent needs information to act on the intent. So these disciplines again
15:52
they're cumulative. Another thing I want you to notice is that failure as we progress up this hierarchy is getting
15:59
more and more serious. When you as an individual sit down and you screw up a prompt, it might waste your morning at
16:05
worst. When you as a human being sit down and screw up context engineering or intent engineering, you are screwing up
16:13
for the entire team, your entire org, your entire company. The stakes get higher. And because the stakes get
16:19
higher, our attention to detail matters and the value of the work we do increases commensurately. What I am
16:26
talking about when I talk about context engineering and intent engineering can be a full-time role at a big company.
16:31
And if it's not, it is a highstakes human skill that has a lot of transferable value. Level four is
16:38
specification engineering. We're just starting to talk about this now, even though the best practitioners are
16:44
already doing it. Specification engineering is the practice of writing documents across your organization that
16:50
autonomous agents can execute against over extended time horizons without human intervention. This is a level
16:57
above everything I've described because all of the first three levels focused on how you prepare work directly for an
17:04
agent. Specification engineering is really about thinking about your entireformational
17:10
corpus in your organization as agent fungeible, agent readable. Everything
17:16
you write has to be something the agent can access and do something with. It's
17:21
not really about prompting per se. It's not about an individual agent's context window. It's not even about the intent
17:27
you've given agents. Specifications are complete. They're structured.
17:32
They're internally consistent descriptions of what an output should be for a given task. They look at how
17:37
quality is measured. Specifications are a mindset you bring to your documents
17:43
that allow you to apply agents across
Discipline Four: Specification Engineering
17:49
large swaths of your current company's context with the confidence that what
17:54
the agent reads is going to be relevant. I think an interesting example from Anthropic actually comes from the team's
18:00
struggles with the Opus 4.5 agent which is one generation ago now. They were trying to build a production quality web
18:07
app. But if you give the agent only a highlevel prompt like build a clone of
18:12
claw.ai, the agent tries to do too much at once, runs out of context mid-implementation, and leaves the next
18:18
session guessing at what happened. The fix, it turned out, was not a better model. It was specification engineering.
18:24
It was a pattern that you could specify where an initial laser agent sets up the environment. A progress log documents
18:31
what's been done and a coding agent then makes incremental progress against a structured plan every session. The
18:37
specification became the scaffolding that let multiple agents produce coherent output over days. So the shift
18:43
from prompt to specification mirrors a transition that happened in human engineering decades ago. When you're
18:49
building something small, verbal instructions and conversations work really well. When you're building something large enough to require a team
18:56
or span multiple sessions, you need blueprints. Anthropic needed blueprints in the Opus 4.5 example. And even though
19:03
we've now moved to Opus 4.6, the need for specification engineering has not gone down, it's gone up because Opus 4.6
19:10
can do even more work. That's true for Codeex 5.3. It's true for Gemini 3.1 Pro
19:16
as well. The smarter models get, the better you need to get at specification engineering. Which is why I deliberately
19:22
started this section zooming out and saying the entire org's document corpus
19:27
should be viewed as a form of specification engineering. And yes, this is a fractal insight. You can also think
19:34
about specification engineering for your individual agent task where you think
19:39
about what is the log that the agent has. How do we assign tasks across this agent build? How do we make sure the
19:45
agent has a clearly specified requirements list to work from? But all
19:51
of that gets way way easier to put together if you think of your entire organizational document corpus as
19:58
specifications that are agent readable. Your corporate strategy is a specification. Your product strategy is
20:04
a specification. Your OKRs are a specification. Everything ends up being
20:09
a specification that your agent can use. And that's different from context engineering because the art of context
20:16
engineering is really about shaping the context window in a way that's relevant for the agent. Right? If you look at
20:21
these four levels, the prompt is you and the agent and you're working on crafting clear instructions. The context window
20:27
is how do you shape relevant tokens. Intent engineering is how do you communicate goals and objectives to the
20:32
agent that allow the agent to work autonomously for long periods of time in a direction consistent with company
20:38
strategy. Specification engineering is how do you think about your entire
20:43
corporate document structure, the knowledge, the context that makes the corporation work as a form of
20:50
specification. And yes, for individual agent runs, how do you refine that specification that becomes something
20:57
where you give the agent a good specification? It is going to start to keep the context window cleaner than
21:04
before. And so these start to interplay, right? If you write good spec, if you have a good task log, if the agent
21:10
understands what the spec is from the broader organizational context, they're less likely to go off the rails because
21:16
of intent engineering conflicts. They're less likely to bloat out with bad context. And so all of these start to
21:22
interplay, but the highest level is to think about specification as the way
21:28
your organization does business. You specify the outputs you want. The agent
21:34
does the work. the outputs are produced. That is the highest level description of what business is going to look like in
21:40
the next couple of years and it starts with understanding how to specify. This is where anthropics best practices
21:47
documentation for cloud code becomes really revealing. The recommended workflow for complex features is
21:52
relatively simple. Interview me in detail. Ask about technical implementation, UIUX, edge cases,
21:58
concerns, and trade-offs. Don't ask obvious questions. Dig into the hard parts. The agent then writes the spec
22:04
with the human. I think that that is an artifact of this moment in time. And I
22:10
think we will get to a point where the agent will only be asking us for places
22:17
where the broader specification corpus is in conflict or ambiguous and we have
22:22
to talk about what it means to us for this task to be accomplished. Well, because the entire organizational
22:28
infrastructure is going to be agent. So the practical skill going forward is not writing code. It's not crafting prompts.
Why Long-Running Agents Break Synchronous Assumptions
22:35
It's the ability to describe an outcome with enough precision and completeness
22:40
that an autonomous system can execute against it for days or weeks. I hope you're seeing here how that is a
22:47
fundamentally different skill from writing a good prompt in a chat window. And the people who are excellent at one
22:54
of these layers are not automatically excellent at all of them. Context engineers spend a lot of time thinking
23:00
about how to compress tokens and get good tokens into context windows and how to keep bad tokens out. That is a
23:06
different mindset than thinking about your information environment is agent translatable, agent readable, agent
23:12
fungeible. We have to have all of these skills in order to effectively bring AI
23:18
into the enterprise or even into a small business in 2026. And I will tell you one-person businesses have the greatest
23:25
advantage right now because if you are a oneperson business and you can just convert your notion to be agent
23:31
readable, you're off to the races today. There's no gigantic effort required to make all of your SharePoint agent
23:38
readable. It's simple. It's easy. You just get it into notion and you're done. This comes back to the core idea that in
23:44
2026, speed is going to matter because agents are going to keep getting better
23:49
quickly. What we have now as days and weeks is going to become weeks and months by the end of the year. And the
23:55
corresponding impact of getting specification engineering correct is going to be even higher. The
24:02
corresponding impact of getting all four levels translated into specific roles,
24:07
people who are responsible, DRIs, teams who handle this, that's going to be even more valuable in 2026. And so what I
24:14
mean by that is that if you are at a large company, you should have people who are doing context engineering and that's all they're doing. You should
24:20
have people who are doing specification engineering and thinking about how agents can read the enterprise. You should have people who are thinking
24:26
about intent engineering and how you translate goals into a set of objectives
24:32
that an agent can read and value and a set of verifiable guardrails the agent can follow. Look, the mental model most
24:39
people carry is that prompting is good instructions for the AI and that fails for a very specific reason. And I hope
24:45
you're seeing it here. That entire model assumes synchronous interaction. In the
24:50
synchronous AI human partnership model, you're always there at the computer. You see the output in real time. You correct
24:57
mistakes right away. You provide additional context when the model asks or when you notice it going off track.
The Five Primitives of Specification Engineering
25:03
longunning agents break every single assumption in that model. So if you've relied on the assumptions of synchronous
25:10
prompting, you have a structural vulnerability in the way you think about AI. You need to start thinking about AI
25:19
as if your real time oversight is embedded in the specification before the
25:25
agent begins to work. The planner worker architecture that's dominating production agent deployments really
25:32
reflects this reality. A capable model plans the work, decomposes it into subtasks, defines the acceptance
25:39
criteria, and assigns work out to models and then cheaper, faster models do the work. The planning phase, you could call
25:45
it the specification phase, determines the quality ceiling. The planning phase,
25:51
basically taking your specification and expanding it and enriching it and breaking it out and planning against it.
25:57
That's what determines the quality of the work of the overall system. Execution without that specification
26:02
step produces broken work and it requires extensive human rework to be a
26:08
value at all. So the shift from fixing it in real time, which is what we do with a lot of prompting in the chat
26:13
window to we must get the spec right up front changes your bottleneck skill.
26:19
Right? Real time prompting rewards verbal fluency. It rewards quick iteration. It rewards a good eye for
26:25
output quality. Specification engineering rewards completeness of thinking, anticipation of edge cases,
26:33
clear articulation of acceptance criteria, and the ability to decompose really complicated outcomes into
26:39
independently executable components. Different people are good at these things in different ways. Some people
26:44
are going to be naturally exceptional at synchronous prompting and they're going to struggle with specification work. And
26:50
some people will be mediocre at chatbased interaction, but they might actually be excellent spec engineers. My
26:55
challenge to you is that you don't tolerate whatever your natural propensity is as your ceiling. Think of
27:03
this as a learnable skill and go after it. Now, you might ask, if we're going
27:08
after it, what are the foundational elements to learn? Specification is ironically very vague. Nate, please tell
27:15
me what you mean. I want to suggest to you that in 2026 we can define the primitives that go into good
27:22
specifications in ways that are useful for us to learn. And I'm going to go ahead and define them right here. I
27:27
think these are the foundation that we need to learn if we want to get better at specifying and we want to get better
27:33
at the prompting skills that will matter in 2026 and beyond. Primitive number one, self-contained problem statements.
27:41
This is actually Toby's insight, but it's not only his insight. It's been primitive. Number one is self-contained
27:47
problem statements. Think back to what Toby said when he talked about the idea that we have to give the model
27:54
everything it needs to do the work. Can you state a problem with enough context that the task is plausibly solvable
28:00
without the agent going out and getting more information? The discipline of self-containment forces you to be clear.
28:07
It surfaces hidden assumptions. It makes you articulate constraints you normally leave implicit because you trust the
28:13
human on the other end to fill in the gaps. AI doesn't fill in gaps reliably. It fills them with statistical
28:19
plausibility, and that's a polite way of saying it guesses in ways that are often subtly wrong. So if you're trying to
28:26
train this primitive, I would say take a request you would normally make conversationally, like update the
28:31
dashboard to show the Q3 numbers and rewrite that as if the person receiving
28:36
it has never seen your dashboard, doesn't know what Q3 means in your org context, doesn't know what database to
28:43
query, and has no access to any information other than what you include. That is the level of self-containment
28:49
you should be challenging yourself with if you want to get better at this primitive. Primitive two, learn about
28:55
acceptance criteria. If you can't describe what done looks like, an agent can't know when to stop or more
29:01
precisely, it will stop at whatever point its internal huristics say the task is complete, which may bear no
29:08
relationship to what you needed. This is why the 80% problem is a big issue for agent system design. the specification.
29:15
Let's say the specification said build a login page when it should have said build a login page that handles email
29:21
passwords, social ooth via Google and GitHub, progressive disclosure of 2FA
29:26
session persistence for 30 days and rate limiting after five failed attempts. If you're training on this primitive, you
29:33
want to get to the latter, not the former. For every task you delegate, write three sentences that an
29:39
independent observer could use to verify the output without asking you any questions whatsoever. If you can't write
29:46
those sentences down, you probably do not understand the task well enough to give it to an agent. I have had that
29:52
happen where I've been in a conversation with an AI agent and I realize I don't
29:57
know enough to delegate the task and I have to come back later. That's okay. It's good to realize that before you
30:03
assign the work. Primitive three is constraint architecture. Learn constraint architecture. What the agent
30:09
has to do, what the agent cannot do, what the agent should prefer when multiple valid approaches exist, what
Self-Contained Problem Statements and Acceptance Criteria
30:16
the agent should escalate rather than decide autonomously. These four categories, the musts, the must notss,
30:23
the preferences, and the escalation triggers form the constraint architecture that turns a loose
30:28
specification into a very reliable one. The claw.md pattern that's emerging in the coding community is a practical
30:35
implementation of constraint architecture. The best claw.md files are not long lists of rules. They're
30:42
concise. They're extremely high signal constraint documents. Use these build
30:47
commands. Follow these code conventions. Run these tests before marking a task complete. Never modify these files
30:54
without explicit instructions. The community consensus is very strongly that every line in an file needs to earn
31:00
its place. If you ask would removing this line cause the AI to make mistakes and the answer is no it really wouldn't
31:06
then kill the line. So if you want to train this primitive before delegating a task you should be writing down what a
31:13
smart well-intentioned person might do that would technically satisfy the request but produce the wrong outcome.
31:20
Those failure mos end up being your constraint architecture. Encode them. Primitive four is decomposition. Large
31:28
tasks need to be broken into components that can be executed independently, tested independently, and integrated
31:34
predictably. This is software engineering's oldest lesson, modularity, but is being applied to AI task
31:40
delegation. Anthropic's longunning agent harness splits every complex project into an environment setup phase, a
31:46
progress documentation phase, and an incremental coding session, each independently verifiable. You get
31:52
similar task decomposition automatically inside codecs. A marketing content audit
31:58
requires the same decomposition as a coding task. So I'm not just talking to engineers here. You would have to
32:04
decompose your marketing content into quality scoring, gap analysis, recommendation generation, etc. If you
32:11
want to train on the primitive of task decomposition, take any project that you
32:16
would estimate at a few days of work and decompose it into subtasks that each take less than 2 hours for you to do.
32:23
Have clear input output boundaries and can be verified independently of the other tasks. That is the granularity at
32:30
which agents work best and it's the granularity at which specification engineering tends to operate. Now, in
32:36
2026, you do not have to pre-specify all
32:42
of those 2-hour tasks when you are writing a prompt, but you do have to
32:48
understand what all of those tasks are. And you have to understand how to
32:53
describe for a planner agent what done looks like and what decomposible
Constraint Architecture and Decomposition
33:00
pieces look like in such a way that the planner agent can reliably break the work into those 50 or 60 subtasks. In
33:09
other words, your job increasingly is not to manually write the subtasks for
33:14
the agent. Your job is to provide the break patterns that a planner agent can
33:20
use to break up larger work in a reliable executable fashion. That's a
33:26
level of abstraction even above decomposition and that is a lot of where we're going as agents start to run.
33:31
Primitive 5 is evaluation design. This is critical to do not just in an
33:36
individual level but at an org level. Organizations need to think about every level of AI deployment in terms of eval.
33:45
How do you know the output is good? Not does it look reasonable, which is how most people evaluate AI output. But can
33:52
you prove measurably consistently that this is good. If prompt craft is the art
33:58
of the input, evaluation design is the art of knowing whether that input
34:04
worked. And in a world where agents can run for a really long time, eval design is the only thing standing between AI
34:11
generated output that I can't use and AI generated output we can really use asis.
34:16
If you want to train this primitive for every recurring AI task in your world, build an eval build three to five test
34:24
cases with known good outputs and run them periodically, especially after model updates. This is going to catch a
34:30
regression. It'll build your intuition for where models fail. It will create institutional knowledge about what good
34:36
looks like for your specific use cases, your team, you, your org. You need to be
34:41
doing this systematically. If you're listening to all this and you're wondering where to start, I gave you those four layers for a reason in order.
34:50
Start by closing the prompt craft gap. Most people are worse at basic prompting than they think. You should be rereading
34:57
prompting documentation. I've written a bunch on the Substack. I'm writing more for this piece. You should do
35:03
interactive tutorials. You can head over to AI Cred and see where you are on prompting. You should be building a
35:09
folder of tasks that you do regularly, writing your best prompt against each one and saving the outputs as your
35:15
baseline and then revisiting them over time. Take prompt craft seriously.
35:20
Second, once you feel like you start to have a handle on that, start to build your personal context layer. You should
35:27
be writing a cla.markown equivalent for your work. I don't care if you use claude. You still need to have an idea
35:35
of your goals, your constraints, your communication preferences, your quality standards, the institutional context
35:41
that a new team member would need 6 months to absorb written down. Start AI
35:46
sessions by loading this context. The difference in output quality should be immediate and obvious. Then get into
35:52
specification engineering. Take a real project, not a toy problem, and write a specification for it. Then start to get
36:00
into intent infrastructure. This is an organizational layer. So if you manage people or systems, you can start
36:05
encoding the decision frameworks your team uses implicitly. If you are an individual contributor, you should be
36:11
encoding the decision frameworks you understand and trying to be a champion
36:16
that pushes for this at the organizational level. A lot of teams like to talk about adopting AI. We'll
Where to Start: The Progression That Builds on Itself
36:22
talk about it in terms of building intent infrastructure. Talk about what good enough looks like for each category of work together. Talk about what gets
36:29
escalated by AI versus what AI can decide. Write it down, structure it, make it available to agents. And then
36:37
practice specification engineering. Take a real project, not a toy problem. Write a spec for it before touching AI. Talk
36:44
about acceptance criteria, constraint architectures, decomposition, etc. Hand that spec to an agent and see what comes
36:51
back. And oh yes, from an org perspective, start to think about every doc you touch as a spec that the agent
36:58
will need to read and operate against. Your org is a system of business processes, even if you're a team of one.
37:05
And those business processes should be agent readable and they should be speckable. This has some of the
37:10
downstream implications that Toby talked about where he said a lot of organizational politics is just bad
37:16
context engineering at the org level. If we practice better specification engineering for our documents, we will
37:24
expose a lot of the implicit assumptions that we end up being political about inside orgs and we will start to make
37:31
those agent readable and they will start to become fungeible and we will start to have fewer issues. Practicing
37:36
specification engineering is a way for us to clearly describe intent at organizational scale and clearly
37:42
translate that intent in a way that agents can read it. And yes, it nests down to individual agent runs and it
37:48
ladders up to the full organizational context. And that's why it's the last and most difficult skill to learn. The
37:54
progression here from prompt craft all the way up to spec engineering is not a ladder where you can abandon lower
38:00
rungs. It's a stack where each layer makes the layers above it possible. You cannot write good spec if you can't
38:08
write good prompts. You can't build effective agent systems if you don't
38:13
understand context engineering. You can't align agent behavior with organizational goals without
38:19
understanding how intent works and how that plays into context engineering. They all go together. There's a final
38:24
dimension to this that goes beyond AI, and I want to spend some time on it. I hinted at it when I talked about the
38:30
idea that Toby found that he communicated better when he got better at prompting. The best human managers
38:37
that I've worked with already operate with that degree of clarity. They give complete context when they delegate.
38:43
They specify acceptance criteria to their team members. They articulate constraints. They're effectively
38:49
following the four disciplines of AI input with their people. And that makes for effective leadership. What's
38:55
happening right now, I think, if we step back, is that AI is enforcing a communication discipline that the best
39:02
leaders have always practiced intuitively and now everyone needs it in order to be effective. You cannot just
39:08
rely on shared context with the machine. You cannot just assume that AI will
39:14
know. And that is something that is a gift to us because so many of our colleagues don't know what we mean
39:21
either. How many times have you sat in a meeting where someone is referring to a
39:26
document and you don't know what that document is and you're afraid to ask? That is a wonderful example of the kind
39:32
of poor communication quality that goes into human meetings. This is not a framing you'll see in a lot of how to
39:38
prompt courses. I think it should be. The skill of providing highquality input to intelligent systems turns out to be a
39:45
skill that's translatable for AIs and for humans. It turns out to be a fundamental skill of the agent age that
39:52
benefits us as humans and how we work together. I think the people who develop these skills, this collection of skills
39:59
around prompting for 2026 are going to end up being the leaders who will run organizations where agents and humans
40:07
both perform at their ceilings. And the people who don't, the people who are stuck in 2025 prompting skills are going
40:14
to wonder why their AI investments keep producing partial value. And meanwhile, their human teams keep having alignment
40:21
issues. The prompt by itself is dead. The specification, the context, the
40:27
organizational intent. That is where the value in prompting is moving toward
40:32
because agents are starting to work for longer and longer periods and look in a lot of ways like junior employees. the
40:38
specification done right turns out to be just what clear thinking has always
40:44
looked like really made explicit because machines don't let us be lazy about it and I'm really excited for the way that
40:51
kind of communication clarity can clean up our organizations and our humanto human communication as well. Good luck
40:57
with prompting the humans and agents in your life. Cheers. And yes, there's lots more on this on the Substack. I think
41:02
this is one that needs a really complete guide. So, I wrote up a lot of extra stuff for this so that you can dive into what each layer of learning means.

## Additional Resources
Tobi Lütke’s framing of **context engineering as a communication discipline** is that the core AI‑using skill is no longer just prompt‑writing, but **systematically designing the information environment** so an LLM can solve a task with as little ambiguity as possible.  Below is a concise breakdown of his approach, method, and usable tips/techniques. [philschmid](https://www.philschmid.de/context-engineering)

***

### Core definition and mindset

Lütke prefers “context engineering” over “prompt engineering” because it better captures the **broader, systems‑oriented skill** of giving an LLM everything it needs to plausibly solve a task in one go.  In his view, success with AI is less about clever rewording and more about: [redis](https://redis.io/blog/context-engineering-best-practices-for-an-emerging-discipline/)

- **Precise problem statements** with enough background that the LLM does not have to ask for clarification.  
- **Treating context as infrastructure**—structured, versioned, and reusable across sessions. [growthmethod](https://growthmethod.com/context-engineering/)

He often summarizes it as:  
> “The art of providing all the context for the task to be plausibly solvable by the LLM.” [turingcollege](https://www.turingcollege.com/blog/context-engineering-guide)

***

### Key principles in Lütke’s method

When he talks about context engineering as a **communication discipline**, the emphasis is on:

1. **Clarity and completeness**  
   - Frame the task so that the model can infer intent, constraints, and domain without needing iterative back‑and‑forth. [acquired](https://www.acquired.fm/episodes/how-to-live-in-everyone-elses-future-with-shopify-ceo-tobi-lutke)
   - Include implicit human context explicitly: who the user is, what they’ve done recently, and what the business constraints are. [news.aakashg](https://www.news.aakashg.com/p/context-engineering)

2. **Structured, reusable context bundles**  
   - Think in terms of reusable “context packages” (e.g., role definitions, business rules, product specs, customer‑segment notes) that can be attached to the model alongside the prompt. [turingcollege](https://www.turingcollege.com/blog/context-engineering-guide)
   - Treat these like configuration or schemata rather than one‑off prompts. [blog.langchain](https://blog.langchain.com/the-rise-of-context-engineering/)

3. **System‑level design, not just prompts**  
   - Context engineering includes retrieval‑augmented generation (RAG), memory architectures, and tool routing pipelines, not just the text of the prompt. [addyo.substack](https://addyo.substack.com/p/context-engineering-bringing-engineering)
   - It is closer to **backend‑style engineering** (routing, caching, summarization) than to copywriting. [philschmid](https://www.philschmid.de/context-engineering)

***

### Practical techniques and patterns

From how Lütke and others describe his approach, the following techniques are central to context engineering as a communication discipline:

#### 1. Retrieval‑augmented context

- **Pull in just‑in‑time knowledge** via RAG or vector search, injecting only the most relevant documents, code, or docs into the context. [intuitionlabs](https://intuitionlabs.ai/articles/what-is-context-engineering)
- Avoid “chunk dumping”: instead, filter and rank so that the LLM sees **high‑signal, clean context** without irrelevant noise. [linkedin](https://www.linkedin.com/posts/sriarun-marimuthu-235416237_ai-llm-contextengineering-activity-7349828794079211520-cjFo)

#### 2. Memory and state management

- Use **summary compression** or **checkpoint summaries** so that multi‑turn conversations stay coherent without bloating the context window. [matthopkins](https://matthopkins.com/technology/context-engineering-practical-guide/)
- Store only the most important facts (e.g., user preferences, business rules) in persistent memory and “rehydrate” the model at the start of a session. [intuitionlabs](https://intuitionlabs.ai/articles/what-is-context-engineering)

#### 3. Context‑shaping heuristics

- **Explicitly define roles, constraints, and success criteria** in the system context (e.g., “You are a tier‑2 support agent; you must not give financial advice”). [growthmethod](https://growthmethod.com/context-engineering/)
- Use **format templates** (JSON, XML‑like, or structured bullets) so the model can reliably parse and follow the context. [promptingguide](https://www.promptingguide.ai/guides/context-engineering-guide)

#### 4. Iterative, eval‑driven tuning

- Treat context like code: version it, A/B test it, and use **evaluation pipelines** to see which context shapes produce more reliable outputs. [praella](https://praella.com/hi/blogs/shopify-news/the-art-of-context-engineering-revolutionizing-ai-interactions-for-optimal-performance)
- Incorporate **user feedback loops**: track where the model misunderstands and enrich the context to close those gaps. [praella](https://praella.com/hi/blogs/shopify-news/the-art-of-context-engineering-revolutionizing-ai-interactions-for-optimal-performance)

#### 5. Avoiding context overload and clash

- **Prune irrelevant or conflicting information** so that the model doesn’t get contradictory signals (context clash) or diluted attention. [redis](https://redis.io/blog/context-engineering-best-practices-for-an-emerging-discipline/)
- Use **relevance scoring**, prioritization, or RAG‑based filters so only the most relevant tools, docs, and constraints are active at any given time. [intuitionlabs](https://intuitionlabs.ai/articles/what-is-context-engineering)

***

### Tips for treating context engineering as a communication skill

Lütke’s framing suggests that good context engineering is a **communication discipline** in three ways:

- **Writing for the model as a stakeholder**  
  - Assume the LLM is a skilled but slightly pedantic colleague who needs explicit assumptions, constraints, and background. [acquired](https://www.acquired.fm/episodes/how-to-live-in-everyone-elses-future-with-shopify-ceo-tobi-lutke)
  - Anticipate ambiguity and bake mitigations into the context (e.g., disambiguate homonyms, define domain‑specific terms). [turingcollege](https://www.turingcollege.com/blog/context-engineering-guide)

- **Designing reusable “context APIs”**  
  - Build **standardized context blocks** (personas, product FAQs, compliance rules, pricing logic) that can be composed into different workflows. [growthmethod](https://growthmethod.com/context-engineering/)
  - Version these so teams can iterate on them without reshaping every prompt individually. [blog.langchain](https://blog.langchain.com/the-rise-of-context-engineering/)

- **Co‑designing with engineers and product folks**  
  - In Shopify‑style practice, context engineering is a cross‑functional concern: UX, product, and engineering together define what context the system must provide. [fs](https://fs.blog/knowledge-project-podcast/tobi-lutke-2/)
  - The “communication” is not just user→LLM, but also **human teams→LLM context**, using shared schemas and documentation. [news.aakashg](https://www.news.aakashg.com/p/context-engineering)

***

### How to practice Lütke‑style context engineering

For a developer like you, a practical, Lütke‑inspired approach could be:

- Start with a **problem spec** that fully answers: who, what, constraints, desired output format, and edge cases—then package that as a reusable context block. [philschmid](https://www.philschmid.de/context-engineering)
- Layer on **RAG** (e.g., embeddings over docs, code, and tickets) to dynamically inject the right snippets into that block. [addyo.substack](https://addyo.substack.com/p/context-engineering-bringing-engineering)
- Add **state‑summarization hooks** (e.g., periodic summaries of the conversation or user session) so the model can “remember” without carrying all history. [matthopkins](https://matthopkins.com/technology/context-engineering-practical-guide/)
- Measure results with **evals** and refactor the context like refactoring code: extract common parts, parameterize, and version‑control the context bundles. [promptingguide](https://www.promptingguide.ai/guides/context-engineering-guide)

If you’d like, the next step can be concrete examples of Lütke‑style “context‑engineered” prompts for coding, docs‑QA, or GTM workflows, tailored to TypeScript/infra patterns you actually use.