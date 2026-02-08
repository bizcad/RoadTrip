# Prompt
As always I will start with a Goal.
# Goal
- to become “The person who defined how we trust AI tools.”
## Slogan
- Let's make AI a safer place
- We can come up with more shibboleths as we test them. 
## Examples
- unsafe Skills that contain malware
- OpenCraw has many vulnerabilities
- Long running agentic workflows can run off the rails because of insecure skills and MCPs.
- Robots and cars can kill because of insecure software
## Write First Advocacy paper
1. Tone: Visionary, persuasive, slightly scary but not hysterical.
2. Problem: The risks of revolutionary times
3. Exposition: 
- AI is still software and should be engineered for safety.
- AI will be everywhere it needs to be trusted
4. Solution
- Secure the quality of the building blocks and the end result will be more secure and trustable
- Make them verifiable
## Strategy
1. Use public forums to search for target audiences.
2. Seek comments > respond to comments > build community
3. Contact celebrities after we gain some notoriety.
4. Give conference talks
5. Publish often

## The business plan should be analogous to an AI consultancy.
- We are selling an idea.
- We can use all the techniques that historical idea sellers have used. 
- Ideas have the cheapest cost of goods of any product.
- The only cost is marketing and we want that to be as close to free as possible.

## Suggestions welcome.
  
# Response
Nick—nailed. I drafted your **first advocacy paper** exactly in the tone you asked: *visionary, persuasive, slightly scary (but not hysterical).* It captures your goal, slogan, examples, problem framing, solution, strategy, and business model.

**Download it here:**  
[Advocacy\_Paper\_Trusting\_AI\_Tools\_Signed\_Skills.docx](blob:https://www.microsoft365.com/bc7c8b3c-6840-442d-87f9-2a2ff359fdc3)

***

## What’s inside (at a glance)

*   **Title:** *Trusting AI Tools — A Visionary Advocacy Paper for Signed Skills & Verifiable Agents*
*   **Goal:** *Become “the person who defined how we trust AI tools.”*
*   **Slogan:** *Let’s make AI a safer place.*
*   **Problem:** Risks of revolutionary times (malicious skills, vulnerable crawlers, agentic drift, physical harm)
*   **Exposition:** AI is still software and must be engineered for safety
*   **Solution:** Verify the building blocks—**tests → attestations → signatures**—and enforce at load time
*   **Strategy:** Forums → comments → community → talks → publish often
*   **Business Model:** An AI trust consultancy with near‑zero COGS; sell playbooks, audits, enablement kits
*   **Call to Action:** Adopt **verified‑only** loading modes and **ship signed skills**
*   **References & Standards:** MCP, Sigstore, SLSA/in‑toto, OCI 1.1 (for provenance and distribution) [\[us-prod.as...rosoft.com\]](https://us-prod.asyncgw.teams.microsoft.com/v1/objects/0-cus-d3-25357510ecf7696ba5bc3d7ad7032b74/views/original/Advocacy_Paper_Trusting_AI_Tools_Signed_Skills.docx), [\[docs.aws.amazon.com\]](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-permissions-id.html), [\[spdx.github.io\]](https://spdx.github.io/spdx-ntia-sbom-howto/)

> This maps directly to the “Signed Skills” architecture we discussed and to the wider ecosystem’s trajectory around MCP and software supply-chain assurance (Sigstore, SLSA/in‑toto, OCI 1.1). [\[us-prod.as...rosoft.com\]](https://us-prod.asyncgw.teams.microsoft.com/v1/objects/0-cus-d3-25357510ecf7696ba5bc3d7ad7032b74/views/original/Advocacy_Paper_Trusting_AI_Tools_Signed_Skills.docx), [\[docs.aws.amazon.com\]](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-permissions-id.html), [\[spdx.github.io\]](https://spdx.github.io/spdx-ntia-sbom-howto/)

***

## Your next step (fast loop)

1.  **Download** the .docx → **edit** in Word (add examples, personal anecdotes, logos).
2.  **Upload** your edited version here.
3.  I’ll **tighten the rhetoric**, add figures/diagrams, and produce a **print‑ready PDF** + **blog‑ready Markdown**.

***

## Suggestions to amplify the impact

### A. Launch Package (1–2 weeks)

*   **1‑page manifesto** (“Trust by Default for AI Tools”) for quick shares.
*   **Blog/LinkedIn post** that condenses the paper to 600–800 words (strong headline + pull‑quotes).
*   **GitHub sample repo** (`signed-skills-starter`) with:
    *   `assertions.yaml` + lock + no‑widening check
    *   CI workflow for **test → attest → sign** (Sigstore keyless)
    *   “Verified‑only” loader stub for MCP hosts
*   **Slide deck** (10 slides) for meetups and calls.

> I can generate each item as **downloadable files** (DOCX/PPTX/MD/ZIP) when you want them.

### B. Audience & Channels (zero‑cost first)

*   **MCP / Agentic communities** (OpenAI Agents SDK, MCP forums, Claude Code channels) to socialize a **“Verified Tools for MCP”** proposal. [\[activestate.com\]](https://www.activestate.com/resources/quick-reads/supply-chain-levels-for-software-artifacts-slsa/)
*   **OSS security & supply‑chain circles** (SLSA, in‑toto, Sigstore, OCI Artifacts WG) to frame it as a **predicate + policy profile**. [\[docs.aws.amazon.com\]](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-permissions-id.html), [\[linkedin.com\]](https://www.linkedin.com/pulse/claude-opus-46-vs-team-agents-mode-jean-philippe-leblanc-b7aje/), [\[spdx.github.io\]](https://spdx.github.io/spdx-ntia-sbom-howto/)
*   **IDE and platform blogs** (Xcode 26.3 added MCP integration; perfect venue for a guest post or demo). [\[legitsecurity.com\]](https://www.legitsecurity.com/blog/slsa-provenance-blog-series-part-2-deeper-dive-into-slsa-provenance)

### C. “Slightly scary” use‑cases to include in talks

*   **Malicious skill** silently exfiltrates data → blocked by **verified‑only** policy and failing attestation.
*   **Agent team** tries to load an unsigned crawler → host refuses; log shows *“signature missing / SLSA<2.”*
*   **Physical system** (robot) only accepts tools with a **passing invariants report** and **valid Sigstore identity**.

(We can mock these in a demo repo so you can run them live.)

***

## Content flywheel (automate with AI)

*   **Research** a topic → **write** a tailored piece → **publish** → **respond** to comments → **measure** → **iterate**.  
    I’ll handle drafting and responses while you steer tone and vision. We’ll adapt for LinkedIn/Medium/Dev.to/Reddit/HN/Substack and conference CFPs.

***

## Optional: add a short **“References”** paragraph to the paper (I can insert on next pass)

*   **Model Context Protocol (MCP)** – open standard for interoperable agent tooling (“USB‑C for AI tools”).
*   **Sigstore** – **keyless** software signing with identity proofs and transparency logs (Fulcio/Rekor). [\[us-prod.as...rosoft.com\]](https://us-prod.asyncgw.teams.microsoft.com/v1/objects/0-cus-d3-25357510ecf7696ba5bc3d7ad7032b74/views/original/Advocacy_Paper_Trusting_AI_Tools_Signed_Skills.docx)
*   **SLSA & in‑toto** – provenance and attestations for trustworthy builds. [\[docs.aws.amazon.com\]](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-permissions-id.html)
*   **OCI 1.1** – standardized artifact **referrers** for signatures/attestations in registries. [\[spdx.github.io\]](https://spdx.github.io/spdx-ntia-sbom-howto/)

***

## Want me to produce the next artifacts now?

*   A **600–800 word LinkedIn** launch post
*   A **blog/Medium** long‑form article (1,500–2,000 words)
*   A **10‑slide PPTX** for your first talk
*   A **GitHub starter repo** (ZIP) with ready‑to‑use CI and example skill

Tell me which one, and I’ll generate **downloadables** you can edit, re‑upload, and iterate—then we’ll publish and start the influence flywheel.
