# Worker briefs

Exact dispatch prompts, kept for reproducibility. All six ran as `general-purpose` agents on Claude
Sonnet 5, in parallel, on 2026-09-12. A shared preamble plus standards block applied to every
brief; per-thread research questions follow.

## Shared preamble (paraphrase-free template)

> You are research worker **R<n> — <thread>** on a public, clean-room research project at
> `/Users/ricalanis/dev_public/computer-use-graph`.
> FIRST: read `docs/01-foundations.md`, especially <sections>. That document is the hypothesis under
> test — your job is to verify, correct, and deepen it, NOT to agree with it.
> YOUR DELIVERABLE: write `research/R<n>-<slug>.md`. Do not edit any other file.

## Shared standards block

> - Use WebSearch and WebFetch aggressively. This is a literature/verification task, not a
>   reasoning-from-memory task.
> - **Never fabricate a citation.** Every paper, repo, or doc you cite must have a URL you actually
>   retrieved. If you believe something exists but cannot find it, write `[could not verify]` and say
>   what you searched for. A short dossier of verified facts beats a long one with invented arXiv numbers.
> - Where the foundations doc is wrong, say so under `## Corrections to docs/01-foundations.md`,
>   quoting the line and giving the correction with a source.
> - End with `## Design implications` and `## Open questions`.
> - Clean-room rule: public sources only; no employer-internal or proprietary systems.

## R0 — Substrate / action-space layers (§1.2, §2)

1. For each major agent stack (Anthropic computer use, OpenAI CUA/Operator, BrowserGym/AgentLab,
   browser-use, Playwright/Selenium agents, WebArena, OSWorld, AndroidWorld, set-of-marks agents,
   Playwright-MCP), document the rung of the agent's action space and what the executor does.
   Produce a comparison table.
2. Published reliability and cost difference between coordinate-level and element-level actions:
   success gaps, grounding error rates, tokens/latency. ScreenSpot family is relevant.
3. Trusted events: what breaks with JS-level `el.click()` / `.value` (React controlled components,
   CSRF, bot detection, listeners). Authoritative sources.
4. Code-as-action evidence (CodeAct and related): gains and caveats.
5. Options/semi-MDP framing: confirm Sutton-Precup-Singh; find any GUI/web application. Is §2.3
   standard, novel, or naive?
6. Read-at-layer-6 / write-at-layer-2: does anyone publish it? Is intercepting XHR responses
   documented in agent harnesses? Any ethics/ToS discussion of request forging by agents?
7. Verdict on §2.4 for an experiment about uncertainty over actions. Argue both sides; name what
   would NOT transfer to a pixel agent.

## R1 — State abstraction & site-graph construction (§4 P1)

1. Prior art on explicit graph/map representations of websites/GUIs for agents: NNetNav, AWM,
   Go-Explore, LASER, Explorer, Synatra, AutoWebGLM, Agent-E, WILBUR, Agent Skill Induction,
   ExACT/R-MCTS, WebDreamer, Koh et al. tree search, site maps / world models. For each: node, edge,
   build, benefit, benchmark. **Verify each exists; some names may be misremembered.**
2. State aliasing: URL canonicalization, DOM similarity/hashing, visual embeddings, LLM labels, and
   the web-testing/crawling literature (Crawljax, model-based crawling). Mine it.
3. The two-layer type/instance proposal: supported, contradicted, or unexplored? Schema/ontology
   induction, wrapper induction, page classification.
4. Partial observability: modals, cart, auth, filters, infinite scroll, SPA routing.
5. Exploration safety: classifying irreversible actions before taking them; safe exploration; how
   crawlers historically avoid destructive requests; SOTA for a "do not click Delete" filter.
6. Graph staleness: invalidation, re-verification, drift detection.
7. Verdict, plus a concrete node-identity scheme and edge schema you would implement.

## R2 — Graph-as-memory, retrieval, and macro replay (§4 P2, §2.3)

1. Agent memory that measurably improves web/GUI success (AWM, WILBUR, skill libraries/Voyager, CBR,
   trajectory retrieval, Mem0/MemGPT): what was stored, how retrieved, delta, benchmark, and **which
   baseline it beat** (none vs flat memory matters enormously).
2. Macro/workflow replay: open-loop success, brittleness, failure modes, repair; RPA selector
   brittleness and self-healing selectors.
3. Retrieval interface design for memory larger than context: semantic search vs traversal tools vs
   subgraph dumps; GraphRAG / KGQA transfer; do LLMs traverse or flail?
4. Context budget: help-before-hurt evidence for agents; token budget per tool return.
5. Verifying macro execution: state assertions, visual diffing, termination predicates.
6. Replay-then-fallback architectures: does §2.3's graceful degradation exist?
7. Verdict: which mode has the strongest support, and what tool API would you ship (signatures)?

**Follow-up (after completion):** resolve Open Question #1 — does any agent-memory paper isolate
"flat trajectory memory in context" as a distinct baseline? Cover AWM, Synapse, ExpeL, WILBUR,
SkillWeaver: exact named baselines, whether any is flat, and the delta. Use ar5iv/arXiv HTML,
ACL Anthology, GitHub repos, and OpenReview rebuttals to get past image-embedded tables. A clean
"no paper does this" is a valid answer. Append as `## Addendum: the flat-memory baseline question`.

## R3 — Uncertainty, perplexity, curiosity (§4 P3)

Framed as the most delicate thread: "be rigorous and be willing to conclude the idea needs reformulating."
1. UQ for LLMs: NLL/PPL, entropy, length normalization, semantic entropy, self-consistency, verbalized
   confidence, P(true), hidden-state probes, conformal. Measured calibration (AUROC); which are poorly
   calibrated and why.
2. UQ for LLM agents: when to ask, backtrack, replan, or stop; AUROC for step or task failure.
3. Length/context confound: does more context mechanically lower PPL; the correct control; is a
   token-matched shuffle sufficient?
4. Bayesian surprise (Itti & Baldi) and LLM-agent applications; computability; better behaved than NLL?
5. Curiosity (ICM, RND, count-based, empowerment): citations and **failure modes, especially the
   noisy TV**; mitigations; implications for a surprisal-driven crawler.
6. Instrumentation: which providers expose logprobs; constrained-candidate scoring; vLLM / llama.cpp /
   HF setup; tokenizer, BOS, and prompt-caching gotchas.
7. Stopping rules: is "stop when marginal surprisal reduction < threshold" known? Learning progress,
   value of information, coverage-based crawl stopping.
8. Verdict: (a) is the Phase 0 gate right; (b) which primary signal; (c) the single most likely
   failure mode and a cheap test for it.

## R4 — Benchmarks, harnesses, metrics (§3)

Framed as: "§3 was written from memory and is expected to contain errors… produce a verified,
corrected version." Reporting that a name doesn't exist counts as success.
1. Verify every benchmark in §3: name, authors, year, URL, what it measures, size, observation and
   action space, scoring, determinism, current SOTA. Add important omissions.
2. The right benchmark: deterministic, self-hostable, DOM/a11y, **many tasks per site**, programmatic
   validator, permissive license. Rank and recommend with per-site counts.
3. Harness: BrowserGym/AgentLab maintenance; extension story for custom tools and per-step
   logprob/candidate logging; alternatives.
4. Published critiques: unsolvable tasks, validator brittleness, contamination, judge over-crediting,
   reproducibility gaps, audited subsets.
5. Metrics: efficiency reporting, partial credit, variance; compute Wilson/binomial intervals and
   correct §3.7's ±13pp.
6. Judge reliability: AgentRewardBench or equivalent; human agreement.
7. Statistical practice: paired test choice; tasks and seeds for 80% power on 10pp.

**Resume note (after the rate-limit cutoff):** finish and write the deliverable from research already
done; don't spawn sub-agents; prefer a complete file with `[could not verify]` markers over another
cutoff.

## R5 — Experimental design, baselines, causal attribution (§4 P4, §5)

Framed as "the methodological adversary: find the ways this experiment would produce a result that
does not mean what the authors think it means."
1. Confound audit: every way graph-vs-naive could be positive for the wrong reason, with a control
   for each, ranked by likelihood.
2. Is the §4 P4 condition list complete? Is condition 2 the right competitor? Retrieval-only,
   random-walk-graph, and token-matched raw-trajectory conditions?
3. Amortization methodology: published amortized accounting for agent memory; specify the rules and
   a rigorous crossover definition.
4. Cost-matched comparison: iso-FLOP/iso-cost methodology; combining tokens, steps, wall-clock, dollars.
5. Statistics: paired binary test, 6-arm multiple comparisons, seeds; an analysis plan and sample size
   for 80% power at 10pp.
6. Reproducibility: what to log and pin; exemplary papers.
7. Negative-result plan and the fastest cheap falsification experiment.
8. Published claims for and against structured memory beating flat retrieval, with numbers.
