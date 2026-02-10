# Zero Trust for Agents

## By: John Kindervag, Principal Analyst, Forrester Research
- link: https://www.forrester.com/report/zero-trust-for-agents/RES177427
- link: https://www.youtube.com/watch?v=d8d9EZHU7fw

## Transcript
0:00
We've entered the age of agentic AI, systems that don't just think, but they also act.
0:06
Agents can talk to APIs. They can call tools. They can buy things. They can move data, even create
0:13
sub-agents. But every new capability adds a new attack surface, yet another way the bad guys can
0:20
get into our systems. So how do we protect this new ecosystem? We bring zero trust. Never
0:26
trust. Always verify. I know, I know, you've heard about zero trust before. Isn't that just a
0:33
marketing slogan that all the vendors used and abuse in order to get us to buy whatever they
0:38
had on the truck? Well, yes and no. Definitely the term got hijacked by overzealous sellers trying
0:43
to meet their quotas. But I'm a cybersecurity architect, and I never got confused by all that
0:49
noise because I knew there were some solid, even game-changing security principles worth holding
0:54
on to. And now that we have AI agents popping up everywhere, the time is right to dust off the hype
1:00
and repurpose the good in zero trust in order to face the current security challenge. Okay, let's
1:06
take a quick review of what zero trust principles are. What distinguishes zero trust from doing
1:12
things in a non zero trust way? Well, one of the simple things that I mentioned previously is you
1:17
verify and then you trust. So you only trust something that has in fact been verified. Or trust
1:24
follows verification is another way to think of it. Another thing is we get rid of the Just in
1:29
Case principle, where we put things out in case we need them, and replace it with just in time. So we give
1:36
the access rights that are needed only when they're needed, and not for longer than they're
1:41
needed. That's a preserving of the principle of least privilege, which says you have only the
1:47
access rights that you need for only as long as you need them, and not longer. Another thing is we
1:52
move from perimeter-based controls, where we're trying to basically put the hard crunchy outside
1:59
and leave the soft, chewy center. That's not very good. In fact, what we want to move to is a more
2:05
pervasive set of security controls. So the security controls are throughout the system, not
2:12
just around the outside. then what I think is the most important aspect, and it often gets
2:17
overlooked in zero trust discussions, is the idea of the assumption of breach. You assume the bad
2:23
guy is already in your system, already in your network, already in your database, in your
2:28
application, already has elevated privileges from stolen credentials. That's what we're going to
2:35
operate from. Now design your security. So it's assuming that you've been breached already. And
2:41
it's a very different model, a very different paradigm and way of thinking about security. So
2:46
let's take a look and see what zero trust principles would look like if they were applied
2:50
to an agentic environment. First of all, let's look at a traditional environment. How do we apply zero
2:56
trust in this case? Well, we've got users that have to be secured. They're part of the security
3:01
equation. So I need to do identity and access management. I need to make sure that the user has
3:06
an account that they're logged in, that the person logged in is in fact the user they claim to be. So
3:11
that's strong authentication. Access controls, so that they can only access the things that they're
3:17
permitted to see. The device that the user is using matters as well. It could be compromised. I
3:23
need to make sure that it is in fact pure, that it hasn't been jailbroken, that an attacker hasn't
3:29
taken control of the system, because then it won't matter if I have the authentic user trying to do
3:35
the right thing if the device has already been compromised. I need to look at the data layer of
3:40
all of this. So I need to make sure that the data that's sensitive has been encrypted so it can't
3:45
be easily seen. I need to make sure that it's not leaving my network if it's not supposed to, things
3:51
like that. And then another big part, and a lot of people start their zero trust discussions in this
3:57
particular area. And it's the area of the network. So I'm going to make sure that my network is well
4:03
secured, that if information is traversing a part and that information is sensitive, then I want to
4:09
have it encrypted. I want to make sure that I do things like micro-segmentation, where I group
4:15
individual parts of the network together and give some level of isolation so that if this guy gets
4:21
infected, his infection doesn't easily spread to others. So those are some of the things that we've
4:26
done traditionally in zero trust and spreading this pervasively throughout the system. I've got
4:32
to do all of that as I move into the agentic world. Plus, I have to do some more. So as we start
4:39
looking at agents, who are the actors? The actors are in fact software. So we've got an AI agent
4:46
here that is using a non-human identity. So here we had
4:52
users, and we could associate them with the identity they were using. But an agent may in fact
4:58
use lots of these different NHIs, lots of different non-human identities. So here we have a
5:05
proliferation of these things growing. I need to make sure all of them have the same level of
5:11
control and visibility that we had for the human users, in fact, maybe even more. Because they're
5:16
operating autonomously and we need supervision of that. We need tools that we're going to be using
5:23
to also be secure. We need to make sure that the tools that we're leveraging are tools we can
5:28
trust. Again, we have data. In this case, data may be the thing that was the basis for the
5:35
AI agent. We use data to train the model. We need to also augment the model. We may use preference
5:41
information and other context information that we put into the model I need to make sure all of
5:47
that stuff has been secured, that it hasn't been tampered with. And then ultimately, I need to be
5:53
able to look at the intentions of the agent and make sure those intentions match what the
5:58
original users intentions were for this particular system. Let's take a look at an agentic
6:03
system and see where the threats might be. So here's how the thing basically works. We have a
6:08
sensing portion. That is the thing that takes the input. It might be visual. It might be textual. It
6:14
could be a lot of different things. But that feeds into the AI, which does the thinking. And then in
6:20
that thinking, we will augment that with policies, preferences and other things like that. So we'll
6:25
have that information affecting the thought process, the reasoning process that's happening.
6:30
And then ultimately, it takes those actions. So it could do an API call. It might write some data and
6:37
move some data around. It might use a tool, it might spawn other agents. And then all of this is
6:44
going to be driven by credentials. So we have Individual capabilities that each one of these
6:50
things ought to be able to have. So if I'm an attacker, I look at this thing and start to figure
6:55
how might I break this thing? Well, one thing I could do right here is a direct prompt injection.
7:02
I might send a prompt in that is going to break the context of this system and have it start
7:07
doing things that it's not supposed to do so that's one of the things I could think about.
7:12
Another is I could attack right here, and I could do something to manipulate to to mess up the
7:18
policy, the preference information to poison that information or even poison the model that was
7:24
used to train this thing. So that's another one to look at. Another thing here is looking at all of
7:29
these interfaces - What if I insert myself at any one of these? That would be a place where I
7:36
could do some damage if on this and this might be, say, an MCP call, something along those lines. And
7:43
I would be able to insert and take control of that. I might also attack individuals of these
7:49
services, these APIs, the data source, the tools, the agents. So all of those are an extension of the
7:55
attack surface. And then right here, their credentials. Maybe I want to go in and attack
8:01
those. Maybe I can copy those credentials. Maybe I can log into a system and create new accounts or
8:08
increase my level of privilege. So there's a lot of different moving parts in this system. An
8:13
attacker has a wealth of different places that they could in fact dive into and do a lot of
8:19
damage. So now, let's apply those zero trust principles to this AI agentic environment, and we'll
8:26
see what we can do to eliminate some or all of these threats. So first of all we're going to
8:31
start here with the credentials. I mentioned this before. We want unique credentials for every
8:36
agent, for every user and every agent that those agents create as well. So we need a place to store
8:42
all of these non-human identities and keep all of them access controlled. Keep them so that they
8:48
don't have more privilege than they're supposed to have. We want it to be just in time, not just in
8:55
case. In other words, we give the privilege just when it's needed, and then we take it away. We
8:59
don't give it in advance and say, well, just in case, you might need this later. So we're going to
9:03
do that. We're going to make sure that these systems also never include credentials buried
9:09
into the system itself And that's been a temptation of programmers. They put a password,
9:15
they put an API key, and they bet it and embed it directly into their code. That is an absolute no-no.
9:21
What we want instead is to store all of these in a vault where we have a dynamic system
9:28
where I can go check credentials in and out. I can get new credentials created over time. I can
9:34
enforce just in time. I can enforce role-based access control. I can do strong authentication.
9:41
I can do all of those kinds of things that I'm needing to do in these cases. So we're going to
9:47
cover all of those bases. No static credentials. Everything is dynamic instead. And then we're
9:53
going to move over to the tools themselves. So I need to make sure that these things have
10:00
registered versions. So I'm going to have a tool registry where I have verified these are secure
10:07
APIs that we can afford to use. The others have not been vetted. These are a set of secure
10:13
databases and data sources that we can use. These are a set of tools that we have vetted and we can
10:20
trust. And all of these kinds of things, if we're going to be using those. It's basically, think
10:24
about if you're making a cake or a soup, you want to make sure that the ingredients that go into it
10:29
are pure. So we want to make sure that we're using the pure stuff to begin with. Then, I need
10:34
something that's going to give me some sort of inspection over the whole thing. So something
10:39
that's going to be able to look over it all. Look here and see if there are improper inputs going
10:46
into any of these tools that are coming out of the agent. Also, be able to look and check for
10:52
these prompt injections that may be coming into the system. We could use an AI firewall or an AI
10:58
gateway, whichever term you prefer to do those sort of checks and block. So it will look and see
11:04
is that something that should be allowed to go in? Do we have information leaking out of systems
11:08
that shouldn't be? Are we making improper calls? This sort of thing. So it's an enforcement layer
11:13
here as well. And then ultimately I need to be able to have traceability of all of this. So I
11:20
need a system where I'm logging immutable logs. means that they can't be changed. I don't
11:25
want a bad guy to come in here and change the information that's in my log. I want to be able to
11:30
prevent that. So when actions are occurring in the system, it needs to be able to be traceable. So we
11:36
can go back later and understand why it did what it did. I also want to scan the entire
11:43
environment. Be able to look across all of these different things. And we've got different tools
11:47
for different types of scanning. We've got network scanning tools. We've got endpoint scanning tools.
11:52
We've got tools now that can scan AI models and look for vulnerabilities that may be latent and
11:58
hiding inside of those. Ultimately, at the end of all this, we need still a human in the loop.
12:05
We need an ability to be able to have a kill switch. If someone sees this thing is running out
12:10
of control, what it's doing is not right and we can go see what it's been doing. We want to put
12:16
throttles in place in some cases so that if maybe it's a buying application, it doesn't just
12:22
suddenly decide, hey, I like this, I'm going to buy a thousand of these in a minute. Maybe we don't
12:27
want it to do that. So we throttle back its activity. We have canary deployments where we sort
12:32
of drop the canary in the coal mine to see what happens. So we're going to see if this system
12:37
dropped into an environment is going to operate properly or not. A lot of different things you can
12:44
see here. The agent systems are complex. The number of threats that we face are complex and
12:50
numerous. So our security defenses have to be up to the challenge. Agentic AI
12:57
multiplies power and risk. Zero trust gives us the framework to keep that power contained.
13:04
Every agent must prove who it is, justify what it wants and earn trust continuously. As we move
13:11
forward with autonomous systems, zero trust principles deployed correctly serve as guardrails
13:16
that keep innovation in alignment with our intent instead of the bad guys.

## Summary

### Overview
John Kindervag presents a framework for applying **Zero Trust principles** to agentic AI systems. The core thesis: agentic AI multiplies both power and risk, and traditional security perimeters are insufficient—we need Zero Trust controls embedded throughout the entire system.

### Key Zero Trust Principles Applied
1. **Trust Follows Verification**: Only trust entities that have been verified; implement strong authentication for all actors (users, agents, sub-agents)
2. **Just-in-Time Access (not Just-in-Case)**: Grant privileges only when needed, for only as long as needed; enforce principle of least privilege
3. **Pervasive Controls (not Perimeter-Based)**: Move from hard external boundary to security controls distributed throughout the system
4. **Assumption of Breach**: Design security assuming attackers are already inside with elevated privileges; this fundamentally changes security architecture

### Threat Landscape for Agentic Systems
Agents introduce multiple attack surfaces:
- **Direct prompt injection**: Manipulating input to break system context
- **Model/preference poisoning**: Tampering with training data, policies, or preferences
- **Interface attacks**: Compromising API calls, tool invocations, or MCP (Model Context Protocol) calls
- **External service attacks**: Targeting APIs, data sources, tools, or sub-agents
- **Credential compromise**: Copying, escalating, or misusing agent credentials

### Security Controls Required
1. **Credential Management**
   - Unique credentials for every agent and sub-agent
   - No static/embedded credentials; dynamic credential vaults
   - Just-in-Time credential provisioning
   - Role-based access control enforcement

2. **Tool & Dependency Registry**
   - Vetted, registered versions of APIs and tools
   - Verified secure databases and data sources
   - Pre-approval model: only approved tools are available

3. **Inspection & Enforcement Layer**
   - AI Firewall / AI Gateway: monitors all inputs and outputs
   - Detects prompt injections before they reach the agent
   - Blocks improper outputs (data leaks, unauthorized tool calls)
   - Prevents off-policy behavior

4. **Observability & Traceability**
   - Immutable logging (logs cannot be altered)
   - Traceability of all actions for post-incident investigation
   - Environment scanning (network, endpoint, AI model vulnerability scanning)

5. **Human Oversight & Guardrails**
   - Kill switch capability for runaway agents
   - Throttling: rate limits on agent actions (e.g., purchase amounts)
   - Canary deployments: test agents before full rollout
   - Continuous human monitoring

### Bottom-Line
Agentic AI requires a fundamental shift from perimeter-based to Zero Trust security. Every agent must:
- **Prove who it is** (strong authentication, unique identity)
- **Justify what it wants** (request justification, policy evaluation)
- **Earn trust continuously** (monitored, logged, capable of being revoked)

---

## Analysis: Zero Trust Implications for SKILLS Security Model

### Current SKILLS Architecture (from Principles-and-Processes.md)

The RoadTrip SKILLS framework already implements **conservative defaults** and **deterministic code**:
- **Phase 1a**: Rules Engine validates files against a blocklist; defaults to "BLOCK_ALL" unless explicitly approved
- **Phase 1b**: Auth Validator, Telemetry Logger, Commit Message Generator (deterministic specialists)
- **Architecture**: Independent skills + central orchestrator coordinator

**Current security posture:**
- Deterministic evaluation (rules-engine) = no probabilistic decision on file safety
- Blocks by design: `.env`, `.secrets`, SSH keys never logged
- Config-driven: safety rules in `config/safety-rules.yaml`
- Audit trail: JSONL telemetry logging
- No embedded credentials
- CLI wrapper security patterns

### How Zero Trust Principles Map to SKILLS

#### 1. **Trust Follows Verification** ✅ Partially Implemented
**Current**: SKILLS validators check files against rules before approval
**Gap**: Agent identity verification not explicitly modeled
- Each skill is deterministic (verifiable output), but agent "identity" is implicit (the orchestrator process)
- No explicit credential verification for the orchestrator itself
- **Recommendation**: Model each skill as a non-human identity (NHI) with provenance tracking

#### 2. **Just-in-Time Access (Least Privilege)** ✅ Strong Alignment
**Current**: SKILLS is perfect for this—each skill has a narrow responsibility:
- Rules-engine: evaluates file safety only
- Auth-validator: checks git permissions only
- Telemetry-logger: records decisions only
- **This is textbook least privilege**—each skill has exactly one job, one permission set

**Recommendation**: Formalize this in `config/role-based-access.yaml`:
```yaml
skills:
  rules_engine:
    permissions: [read_file_paths]
  auth_validator:
    permissions: [check_git_credentials, verify_user_identity]
  telemetry_logger:
    permissions: [append_log_file]
  git_push_autonomous:
    permissions: [exec_git_push]  # Only if all prior approvals pass
```

#### 3. **Pervasive Controls (Not Perimeter-Based)** ✅ Strong Alignment
**Current**: Rules placed at multiple points:
- **Sensing layer**: Command-line args parsed, file paths normalized
- **Thinking layer**: Rules-engine evaluates safety, auth-validator checks permissions
- **Action layer**: Telemetry logs before/after push, orchestrator permits or blocks
- **Logging layer**: Immutable JSONL audit trail

**This is excellent pervasive control architecture.**

#### 4. **Assumption of Breach** ⚠️ Partially Addressed
**Current**: Conservative defaults handle compromised rules, but gaps remain:

**Scenario 1**: What if `config/safety-rules.yaml` is tampered with?
- Current: Rules are read from disk; no integrity verification
- **Gap**: Config could be modified by lateral attacker after skill starts
- **Solution**: Cryptographic signing of config files; validate signature on load

**Scenario 2**: What if the orchestrator process is compromised after a successful push?
- Current: Telemetry logs are append-only, but could a compromised orchestrator suppress logs?
- **Gap**: Logging is local; no external audit sink
- **Solution** (Phase 2): Send immutable logs to external system (e.g., Azure Confidential Ledger, append-only blob storage)

**Scenario 3**: What if a sub-agent (spawned orchestrator instance) goes rogue?
- Current: SKILLS doesn't yet support sub-agents (multi-level orchestration)
- **Gap**: Future capability requires explicit credential isolation per sub-agent
- **Solution**: Each spawned agent gets a unique, short-lived token; revocable at any time

### Threat Vectors Applied to SKILLS

Using Kindervag's threat model, here are **agent attack surfaces in SKILLS**:

1. **Prompt Injection** (Not applicable—SKILLS is deterministic, not LLM-driven)
   - Mitigation: ✅ SKILLS skills are Python code, not language models; no injection risk

2. **Policy/Preference Poisoning** (⚠️ Applicable)
   - **Attack**: Modify `config/safety-rules.yaml` to whitelist dangerous files
   - **Current mitigation**: File is read-only in production (enforced by CI/CD)
   - **Enhancement**: Sign config files; fail-safe if signature invalid

3. **Interface Attacks** (⚠️ Partially applicable—git API calls)
   - **Attack**: MCP call interception (if using MCP to invoke skills)
   - **Current**: SKILLS are direct Python—no RPC/MCP yet
   - **Phase 2 Risk**: If MCP-based, Kindervag's AI firewall monitoring becomes critical

4. **Credential Compromise** (✅ Addressed)
   - **Attack**: Steal git credentials, SSH keys, API keys
   - **Current mitigations**:
     - No hardcoded credentials in code
     - Git auth delegated to system keychain/ssh-agent
     - API keys referenced but not embedded
   - **Enhancement**: Rotate credentials after each push; use temporary tokens

5. **Telemetry Tampering** (⚠️ Risk if attacker gets code execution)
   - **Attack**: Modify JSONL logs post-facto to hide a malicious push
   - **Current**: Logs are local files; no tamper protection
   - **Enhancement**: Append-only write; send copies to immutable external storage

### Recommendation: SKILLS Zero Trust Hardening Roadmap

#### Phase 1b-Security (Immediate)
1. **Config Signing**: Add HMAC/RSA signature verification to `config_loader.py`
   ```python
   def load_config_with_verification(config_path: Path, signing_key: Path) -> Dict:
       # Load config
       # Verify signature
       # Fail-safe if invalid
   ```

2. **Credential Rotation**: After successful pushes, request fresh credentials:
   ```python
   def rotate_credentials_post_push(agent_id: str) -> None:
       # Revoke old git token
       # Request new short-lived token
       # Update .git/config atomically
   ```

3. **External Audit Log**: Stream telemetry to immutable sink (e.g., Azure Table Storage with append-only SAS token):
   ```python
   async def write_immutable_log(event: StepResult) -> None:
       # POST to append-only endpoint
       # Fail non-blocking if network down
   ```

#### Phase 2-Security (Next Quarter)
1. **Sub-Agent Isolation**: When orchestrator spawns child agents:
   - Each child gets unique, ephemeral identity (JWT with 30-min TTL)
   - Credentials scoped to child's specific tasks
   - Parent can revoke child permissions immediately

2. **AI Firewall Integration**: If adding LLM reasoning to any skill:
   - Pre-filter all LLM inputs (prompt injection detection)
   - Post-filter all LLM outputs (policy compliance check)
   - Log all filter decisions

3. **Environment Scanning**: Automated checks:
   - Does `config/` contain plaintext secrets? (falco, gitleaks)
   - Are credentials cached in unexpected locations? (git credential verify)
   - Are logs being written to unexpected locations? (audit systemd journal)

---

## Strategic Opinion: Zero Trust Adoption for SKILLS

### Is Kindervag's Zero Trust Framework Beneficial for SKILLS?

**Short answer: YES, highly beneficial. SKILLS is already 70% aligned; this framework guides the remaining 30% hardening.**

### Why Strong Alignment

1. **SKILLS' deterministic architecture is a natural fit for Zero Trust**
   - Deterministic code = verifiable, auditable, repeatable
   - Conservative defaults = assumption of breach ✅
   - No embedded credentials = trust follows verification ✅
   - Narrow skill permissions = least privilege ✅

2. **The orchestrator coordinator pattern matches agent hierarchy**
   - One responsible actor (orchestrator) calling specialists
   - Each specialist has one job, one permission set
   - Failure in one specialist doesn't cascade (error handling + resilience)

3. **Immutable logging + audit trail is foundational**
   - SKILLS' JSONL telemetry is the "traceability" pillar Kindervag emphasizes
   - Append-only design prevents tampering

### Why the 30% Gap Matters

The three missing pieces are **assumption-of-breach scenarios**:
1. **Config tampering** (adversary modifies rules on disk)
2. **Execution compromise** (adversary gains code execution after a push succeeds)
3. **Credential escalation** (adversary exfiltrates a git token for use elsewhere)

These are *not* "nice-to-have" hardening; they're **critical if SKILLS runs in untrusted environments** (CI/CD, cloud, shared infrastructure).

### Recommendation for Principles-and-Processes.md

I recommend **adding a new section: "Security-First Architecture: Zero Trust Model"** that states:

```markdown
### 8. Security-First Architecture: Zero Trust Model

SKILLS implements the **Zero Trust security framework** (Kindervag, Forrester Research):

- **Trust Follows Verification**: Each skill output is verified; credentials verified before use
- **Just-in-Time Access**: Each skill has minimal, ephemeral permissions for its single job
- **Pervasive Controls**: Security decisions at sense → think → act boundaries, not just perimeter
- **Assumption of Breach**: Config signed; logs externalized; credentials rotated; no trusted network assumed

**Phase 1b Roadmap Additions**:
- [ ] `config/role-based-access.yaml` formalizes permission model
- [ ] Config file signing (HMAC verification in config_loader.py)
- [ ] Credentials never cached longer than required
- [ ] Telemetry logs sent to append-only external sink (recommended)
- [ ] Sub-agent credential isolation spec drafted

**Phase 2 Roadmap Additions**:
- [ ] Sub-agent spawning with ephemeral identity (JWT, 30-min TTL)
- [ ] AI firewall integration if LLM reasoning added to any skill
- [ ] Automated environment scanning (gitleaks, git credential verify, audit journal)
- [ ] Credential rotation post-push
```

### Strategic Benefit

Adopting Kindervag's framework **elevates SKILLS from "well-designed deterministic system" to "production-grade agentic AI security model."** This matters because:

1. **Attracts enterprise users**: Enterprises follow Forrester guidance; Zero Trust = board-level credibility
2. **De-risks scaling**: As SKILLS gains capabilities (LLM reasoning, sub-agents, external tools), each new feature has a clear security pattern
3. **Aligns with industry evolution**: AI governance is moving toward Zero Trust; SKILLS will be ahead of the curve
4. **Justifies architecture choices**: Zero Trust framework explains *why* SKILLS is built the way it is (deterministic, conservative defaults, audit trails)

### Final Recommendation

**Highly beneficial. Integrate into Principles-and-Processes.md as foundational security principle (Section 8), not an afterthought. Make explicit the Phase 1b and Phase 2 security roadmap items. This signals that SKILLS is built for production, not just POC.**