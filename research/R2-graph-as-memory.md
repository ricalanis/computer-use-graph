# R2 — Graph-as-memory, retrieval, and macro replay

**Worker:** R2. **Scope:** §4 P2 (graph-as-tool-API) and §2.3 (options / graceful degradation) of
`docs/01-foundations.md`. Public sources only, each claim linked to a retrieved URL.
`[could not verify]` marks anything I searched for but could not source.

---

## 1. Agent memory that measurably improves web/GUI task success

All numbers below are **relative** or **absolute success-rate deltas over a stated baseline** —
the baseline is the load-bearing fact for this project, so it's called out for each row.

| System | What's stored | Retrieval | Benchmark | Result | Baseline it beat |
|---|---|---|---|---|---|
| **Agent Workflow Memory (AWM)** — Wang, Mao, Fried, Neubig, 2024 | Induced textual "workflows" (reusable action routines) abstracted from past trajectories, offline or online | Selectively injected into the prompt (not full dump) | Mind2Web, WebArena | +24.6% relative SR on Mind2Web, +51.1% relative SR on WebArena, fewer steps; +8.9–14.0 abs. points as train/test distribution gap widens | Baseline is the underlying ReAct-style agent with **no workflow memory**. I could not confirm from the arXiv abstract/HTML pages I could fetch whether AWM's paper *also* runs a flat-all-trajectories-in-context ablation (the PDF's results table is embedded as images and didn't extract as text) — **`[could not verify]`** the flat-memory comparison specifically; only the no-memory delta is confirmed. [arXiv:2409.07429](https://arxiv.org/abs/2409.07429) |
| **WILBUR** — Lutz et al., 2024 | Successes *and* failures from past runs; a differentiable ranking model selects which past demonstrations to inject, plus synthesized natural-language "advice" | Learned ranker populates the prompt with the most useful past demos (not similarity-only) | WebVoyager | 53% text-only SOTA at the time; within 5% of multimodal SOTA, beats it on 5/8 sites; adds **backtracking** to a previous state so an undetected mistake isn't fatal | Prior in-context-learning and fine-tuned web agents on the same benchmark | [arXiv:2404.05902](https://arxiv.org/pdf/2404.05902) |
| **Synapse** — Zheng et al., ICLR 2024 | Trajectories after **state abstraction** (irrelevant DOM stripped) stored as exemplars; embeddings retrieved by similarity | Trajectory-as-exemplar prompting: full abstracted trajectories, not single actions | Mind2Web, MiniWoB++ | Incrementally adding state abstraction → TaE prompting → exemplar memory: +32%, +50%, +56% step-SR (GPT-3.5) across three generalization levels; 2.5× step-SR over MindAct on CodeLlama-7B; 99.2% avg SR on MiniWoB++ (64 tasks) from demos on only 48 tasks | Each component's ablation is against the previous (weaker) component — a clean internal ablation ladder, not just vs. zero memory | [arXiv:2306.07863](https://arxiv.org/abs/2306.07863) |
| **ExpeL** — Zhao et al., 2023 | Cross-task "insights" distilled from trajectories + retrieved raw trajectories (two separate learning modes: insight-only vs retrieval-only) | Either injected insight list or nearest-trajectory retrieval | ALFWorld, WebShop, HotpotQA | ALFWorld: 54% (insight) / 59%(?) vs. Reflexion; WebShop: 37–38% (both modes, near-parity); HotpotQA: 36%/31% | ReAct / Act baseline agents and Reflexion (self-reflection, no persistent memory) | [arXiv:2308.10144](https://arxiv.org/abs/2308.10144) |
| **SkillWeaver** | Self-discovered, self-honed callable "skill APIs" synthesized from exploration | Skills exposed as tools the agent can call directly | WebArena, live sites | +31.8% and +39.8% relative SR vs. no-skills; skills from a strong agent transfer to a weak agent for up to +54.3% | Same agent without synthesized skill APIs | [arXiv:2504.07079](https://arxiv.org/abs/2504.07079) |
| **WALT** (Web Agents that Learn Tools) | Discovered, verified reusable "tools" (parameterized macros) per site | Tool-calling interface, near-perfect per-tool invocation success once learned | WebArena | Best on 5/6 domain splits; beats ASI (skill-induction baseline) by 9 points | ASI and other skill-induction baselines, not just no-memory | [arXiv:2510.01524](https://arxiv.org/html/2510.01524v1) |
| **PolySkill** | Cross-site, "polymorphic" abstracted skills (parameterized across sites, not per-site) | Retrieved/matched by task-type abstraction | Cross-task / cross-domain web splits | +9.4% SR cross-task, +3.2% cross-domain over ASI; beats SkillWeaver too | ASI, SkillWeaver (both are memory/skill baselines, not naive) | [arXiv:2510.15863](https://arxiv.org/html/2510.15863) |
| **Voyager** (Minecraft, not web — the stated ancestor) | Executable code skills in an ever-growing library, retrieved by embedding | Iterative prompting with environment feedback + self-verification | Minecraft tech-tree / item discovery | 3.3× more unique items discovered vs. prior SOTA; skill library transferred to AutoGPT raised 0/3 → 1–2/3 zero-shot success | Prior LLM Minecraft agents without a persistent skill library | [arXiv:2305.16291](https://arxiv.org/abs/2305.16291) |

**Case-based reasoning (CBR) for LLM agents.** A 2025 review formalizes the CBR loop
(retrieve → reuse → revise → retain) for agents and reports it addresses hallucination and
brittleness in structured tasks, but — important corrective — a cited finding is that **random
exemplar sampling sometimes outperforms similarity-based retrieval** for diverse contextual
reasoning, i.e., naive nearest-neighbor case retrieval is not automatically the right retrieval
policy. A 2026 GUI-specific paper ("Beyond Trajectory: Explicit Case-Based Memory for
Decision-Making in Multimodal GUI Agents") argues raw trajectory retrieval leaves reuse implicit
and hard to control, and that explicit structured cases with controlled reuse "consistently
improve over baseline approaches" — but I could not extract exact success-rate deltas from the
abstract alone. [arXiv:2504.06943](https://arxiv.org/abs/2504.06943),
[Springer chapter](https://link.springer.com/chapter/10.1007/978-3-032-33865-5_21) `[partially verified — numeric delta not confirmed]`

**Mem0 / MemGPT-style systems.** Mem0 reports 92.5 on LoCoMo and 94.4 on LongMemEval, with 5–11%
relative gains over the best prior method per question type, at 3–4× lower token cost than
full-context baselines and >91% lower p95 latency.
[mem0.ai/research](https://mem0.ai/research), [arXiv:2504.19413](https://arxiv.org/pdf/2504.19413)
— **caveat that matters for this project: LoCoMo and LongMemEval are long-horizon conversational
QA benchmarks, not web/GUI task-execution benchmarks.** They validate that structured extraction +
retrieval beats full-context replay for *recall*, but say nothing about action success on a UI.
Treat Mem0's numbers as evidence for the retrieval-architecture question (§3 below), not as
GUI-task evidence.

**Bottom line for RQ1:** every one of these papers that reports numbers on a *web/GUI* benchmark
beats a no-memory or weaker-memory baseline by double-digit relative percentages, and the deltas
get **larger**, not smaller, as tasks/environments drift from what was memorized (AWM: +8.9 to
+14.0 abs. points as the distribution gap widens; PolySkill built specifically to win on
generalization). That is the opposite of what naive overfitting-to-memory would predict, and it is
direct evidence that **memory beats no-memory**, but few of these papers isolate "flat trajectory
memory" as the intermediate baseline the way this project's P4 condition-2 requires — see
Corrections below.

---

## 2. Macro / workflow replay — open-loop execution, brittleness, repair

**Brittleness is well documented, quantitatively.** On WebArena-style long-horizon tasks, GPT-4
succeeds *consistently* on only 4/61 task templates — i.e. exact repeatability of a working
procedure is rare even for a strong model acting freely, before any caching is involved
[arXiv:2510.23883](https://arxiv.org/pdf/2510.23883). A back-of-envelope error-compounding
argument recurs across this literature: at a (favorably estimated) 95% per-step success rate,
10 sequential steps compound to ~60% end-to-end success — 4 of 10 runs fail *somewhere*, which is
exactly the brittleness a length-N open-loop macro inherits unless it can detect and recover from
a bad step rather than only detect a bad final state
[AI Agent Handbook](https://agenthandbook.chainofthought.xyz/inside-the-loop).

**RPA literature (15 years of exactly this problem).** UiPath's own materials describe
selector-based automation as chronically fragile: "UI changes are the primary cause of robot
failures," with the maintenance cost so severe that "nearly 50% of developers' time is spent
fixing it." Their **Healing Agent** response: on selector failure, don't retry — scan the live UI,
infer intent semantically (e.g., recognize a renamed button), and rebind. A reported case study
claims 60–70% reduction in UI-maintenance effort after deployment.
[UiPath blog](https://www.uipath.com/blog/product-and-updates/technical-tuesday-how-healing-agent-solves-ui-automation-challenges),
[Tech Mahindra case study](https://www.techmahindra.com/insights/whitepapers/afterlife-of-rpa/).
This is the closest **prior-art validation of the graph-edge-as-option idea in §2.3**: RPA already
learned that a durable macro needs a semantic-not-positional binding plus a repair loop, not just a
selector.

**Modern LLM-era equivalents (2025–2026), converging on the same architecture independently:**

- **Muscle-Mem** (open-source SDK): records an agent's tool-call trajectory once, then on
  recognizing the same "Check" state deterministically replays it; on a **cache miss** it falls
  back to full agent reasoning for that task.
  [GitHub](https://github.com/pig-dot-dev/muscle-mem), [HN discussion](https://news.ycombinator.com/item?id=43988381)
- **PreAct** (computer-use agents): caches action sequences + outcomes; on divergence or failure
  during replay, falls back to full reasoning for the diverging step(s), not the whole task.
  [arXiv:2606.17929](https://arxiv.org/pdf/2606.17929)
- **"Agentic Compilation"** (web automation, 2026): compiles a successful trajectory into a
  deterministic script; on DOM-state divergence, action failure, or validation failure it triggers
  **"lazy replanning"** — full LLM reasoning kicks in only for the failed step and everything after
  it, not a restart from the top. Also reports a DOM-sanitization step to shrink the context used
  during fallback reasoning. [arXiv:2604.09718](https://arxiv.org/pdf/2604.09718)
- **SkillDroid** (mobile GUI, "Compile Once, Reuse Forever"): compiles trajectories into macros; a
  **weighted element locator** (multi-attribute, not single-selector) detects UI drift, and a
  **checker-in-the-loop** validates each replayed step; on divergence it reroutes to the LLM agent
  and replans *from the failure point*, calling this "speculative replay."
  [arXiv:2604.14872](https://arxiv.org/pdf/2604.14872)

All four converge on the identical three-part shape: (1) cache/compile a successful trajectory,
(2) a cheap per-step check detects divergence, (3) fallback resumes reasoning from the failure
point rather than the top. This is strong, if recent and not yet widely cited, evidence that the
design in §2.3 ("try the macro, check the termination predicate, drop one rung on failure") is
**not novel as an architecture** — it has been independently reinvented at least four times in the
last ~18 months across web and mobile GUI automation. The contribution this project can still
claim is *what the macro/option is built from* (a graph with typed affordances and confidence, vs.
an opaque cached script) and the *uncertainty-gating trigger* specifically, which none of these
four papers use — they gate on hard failure/divergence, not on a continuous uncertainty signal.

**Failure modes reported, consolidated:** UI layout/DOM structure change (RPA's classic case);
renamed/restyled elements that still serve the same function (needs semantic not positional
matching); dynamic content changing what a "next" step even means; accumulating small perception
errors over long chains (the compounding-error argument above); and — specific to LLM-driven
compilation — the compiled script silently succeeding against the *wrong* state (a false-positive
step-check), which is exactly why a termination predicate independent of the replay engine itself
matters (§5 below).

---

## 3. Retrieval interface design for a memory too large for context

**GraphRAG (Microsoft) is the reference architecture,** and its evaluation story is a genuine
**correction to the foundations doc's optimism about "graph structure helps."** GraphRAG indexes
via LLM entity/relationship extraction, clusters into hierarchical communities (Leiden algorithm),
and answers global (corpus-level) questions via bottom-up community summarization, which flat RAG
structurally cannot do (flat RAG retrieves chunks; it has no way to answer "what are the main
themes across everything").
[Microsoft Research blog](https://www.microsoft.com/en-us/research/blog/graphrag-unlocking-llm-discovery-on-narrative-private-data/),
[arXiv:2404.16130](https://arxiv.org/abs/2404.16130). **But**: a systematic follow-up evaluation
found that **when scored against ground-truth references (ROUGE/BERTScore) instead of LLM-as-judge,
community-based GraphRAG with global search generally *underperforms* plain RAG** — on ROUGE-2,
GraphRAG scored 6.99 vs. plain RAG's 10.08 on SQuALITY, and 3.23 vs. 6.32 on QMSum. The original
GraphRAG paper's advantage was measured with an LLM judge without ground truth, a methodology
independently shown to be inflatable (summary-ordering alone can flip an LLM judge's preference).
[arXiv:2502.11371](https://arxiv.org/pdf/2502.11371). **Implication for this project:** don't cite
GraphRAG's headline win uncritically; its evidence base is judge-methodology-dependent, and a
site-navigation graph is a different retrieval problem (structural affordance lookup, not
open-ended corpus summarization) — the transferable part is the *indexing pattern* (type layer /
community layer above an instance layer), not the summarization win.

**Does an LLM actually traverse a graph via tools, or does it flail?** Direct evidence, both ways:

- **GraphWalk** (tool-based graph navigation benchmark): without tool access, models show
  "incomplete exploration patterns, often fixating on the first few relationships of a node and
  abandoning searches... even when correct information existed within the same node's connections."
  *With* explicit traversal tools, results improve sharply: 80–100% success on maze traversal where
  tool-less baselines fail even on 10×10 mazes; on property-graph QA, tool-equipped GPT-4.1 matches
  or beats larger reasoning models operating without tools. But **not uniformly**: "logical
  intersection, aggregation, and variable-hop pathfinding taxes models severely, with catastrophic
  failure for variable-hop path queries" — i.e., single-hop `neighbors()`-style lookups work,
  multi-hop `path()`-style composition is where models genuinely flail.
  [arXiv:2604.01610](https://arxiv.org/pdf/2604.01610)
- **ToolMaze / perturbation studies**: complex tool-graph topologies "trap agents in futile
  trial-and-error loops," and perturbation recovery rate drops ~37% under implicit semantic
  failures (a tool works differently than its name/description implies).
  [arXiv:2607.06273](https://arxiv.org/html/2607.06273) (AgentTether, a related repair framework,
  separately reports repairing 59–65% of initially failed tau-bench tasks by diagnosing failed
  traces into a graph and injecting repair guidance — evidence that graph-structured
  post-hoc diagnosis is tractable even when live traversal isn't perfectly reliable.)

**Practical synthesis for RQ3:** the field's converging answer, repeated across several
2026 comparative write-ups, is **hybrid, not either/or** — vector/semantic search to find *entry*
nodes (the `search(goal_text)` primitive in §4 P2's minimum tool set is exactly this), then typed
graph traversal for the *relational* hop once you're grounded (`neighbors()`, `path()`). This
matches §4 P2's proposed tool set almost exactly; the literature's addition is that **`path()` /
multi-hop composition is the fragile part and should be pre-computed and cached (the macro),
not asked of the model at inference time via raw traversal tools** — which is an argument *for*
recommending macro-mode over "give the agent `neighbors()` and let it walk," at least for anything
beyond 1–2 hops.
[Atlan comparison](https://atlan.com/know/vector-database-vs-knowledge-graph-agent-memory/),
[Hindsight blog](https://hindsight.vectorize.io/blog/2026/08/24/knowledge-graphs-vs-vector-search-agent-memory)
`[secondary/blog sources — treat as synthesis, not primary evidence]`.

---

## 4. Context budget — how much retrieved context helps before it hurts

- **Lost in the Middle** (Liu et al., 2023/2024, TACL): the foundational result — multi-document
  QA and key-value retrieval accuracy is U-shaped in position; accuracy is highest with the answer
  at the start or end of context and **degrades by more than 30%** when the answer sits in the
  middle, and this holds even for models explicitly built for long context.
  [arXiv:2307.03172](https://arxiv.org/abs/2307.03172)
- **Context Rot** (Chroma technical report, Hong/Troynikov/Huber, 2025): tested 18 frontier models
  (GPT-4.1, Claude 4, Gemini 2.5, Qwen3, etc.). Key findings directly relevant to a tool-return
  budget: (a) performance is **not uniform across input length even on simple tasks** — it degrades
  as length grows, and degrades faster when the needle-question semantic similarity is *lower*
  (i.e., the more a retrieved graph node's summary has to be *inferred* to be relevant rather than
  matching verbatim, the worse this gets with length); (b) **even a single distractor measurably
  hurts**, and the effect compounds with length; (c) on LongMemEval, focused prompts (~300 tokens)
  dramatically outperform full prompts (~113k tokens) at the same task; (d) surprising and
  counter-intuitive — **structurally coherent context can hurt more than shuffled/incoherent
  context of the same content**, suggesting attention allocation interacts with structure in ways
  that aren't simply "more relevant text = better." The report explicitly frames the fix as
  **context engineering**, not a specific token number.
  [research.trychroma.com/context-rot](https://www.trychroma.com/research/context-rot),
  [GitHub replication kit](https://github.com/chroma-core/context-rot)
- **Anthropic's own applied guidance** converges on the same prescription in operational terms:
  "find the smallest set of high-signal tokens that maximize the likelihood of your desired
  outcome"; treat context as a finite, depleting attention budget; prefer **just-in-time retrieval**
  over pre-loading; and — the one concrete number found — in a worked example with a **3K-token
  tight budget for a tool-heavy agent**, system prompt/current input/history are prioritized first
  and retrieved content plus tool definitions are trimmed to fit what's left.
  [anthropic.com/engineering/effective-context-engineering-for-ai-agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**No paper found gives a single universal "right" token count for a tool return** — every source
converges on the qualitative claim (small, high-signal, single-hop-summary-shaped beats large and
comprehensive) rather than a number `[could not verify a benchmark-derived optimum]`. The
actionable synthesis for this project: treat "graph tool return size" itself as an experimental
variable (this is already implicit in §4 P2's "token budget on tool returns" requirement) and, per
Context Rot's distractor finding, prefer **fewer, higher-precision candidate nodes** from
`search()`/`neighbors()` over a larger, noisier set — a wrong-but-plausible neighbor is worse than
having fewer options.

---

## 5. Verification of macro execution

- **Visual/screenshot-based step verification**: after each action, screenshot + model judgment of
  whether the expected outcome occurred; explicitly framed as a fix for "silent failures" where an
  agent reports success while leaving the system in an unknown state.
  [dev.to write-up](https://dev.to/custodiaadmin/visual-verification-for-ai-agents-how-to-confirm-web-actions-actually-worked-30n4)
- **VeriSafe Agent** (mobile GUI): formal **logic-based action verification** rather than visual
  judgment — predicate-level verification re-checks a state predicate's truth value on every
  variable update. [arXiv:2503.18492](https://arxiv.org/pdf/2503.18492)
- **"Where Did It Go Wrong?"** — process-level evaluation via **semantic state tracking**:
  decomposes a run into exploration success / execution outcome / skill-invocation pattern and
  compares trajectories at *shared semantic states* to localize exactly where two runs diverge —
  directly applicable as a design for a termination-predicate audit trail.
  [arXiv:2606.15673](https://arxiv.org/html/2606.15673)
- **Completion-gate pattern** (VLAA-GUI and similar): a **Completion Gate** enforces mandatory
  self-verification at every step against UI-observable success criteria before a DONE/CONTINUE
  decision, plus an *independent*, separately-prompted verifier that cross-examines the completion
  claim rather than trusting the acting model's own report.
  [arXiv:2604.21375](https://arxiv.org/pdf/2604.21375)
- **SkillDroid's "checker-in-the-loop"** and **Agentic Compilation's** DOM-divergence /
  action-failure / task-validation triggers (§2 above) are the closest existing implementations of
  exactly the per-step termination predicate §4 P2 asks for on a graph edge.

**Synthesis:** the field has three verification families — (1) visual diffing/screenshot judgment
(general, cheap, but another LLM call and another point of judge unreliability), (2) explicit
state-predicate assertion (cheaper and checkable but requires knowing in advance what to assert,
i.e. it's exactly what the graph edge's termination predicate should encode), (3) independent
verifier separate from the acting/replaying model (most robust, doubles cost). No single paper
combines all three for *macro replay specifically* with reported numbers; each pattern is validated
individually. This is a genuine open engineering synthesis this project would be contributing, not
one it can cite wholesale.

---

## 6. Fallback design — does §2.3's graceful degradation exist in the literature?

**Yes — independently converged on at least four times in 2025–2026** (Muscle-Mem, PreAct,
"Agentic Compilation," SkillDroid — full detail in §2). The consistent shape across all four:
cache/compile → cheap per-step check → on divergence, resume reasoning **from the failure point**,
not from the top of the task. None of the four use a *continuous uncertainty signal* as the
fallback trigger the way §4 P3 proposes (perplexity/entropy/ensemble disagreement); all four gate
on **binary** failure/divergence detection (element not found, validation failed, DOM state
mismatch). **This is the specific gap where this project's uncertainty-gated variant (§4 P2's
"recommended middle") would be a genuine, not-yet-published contribution** — the architecture
pattern is established; using a calibrated continuous signal to decide *before* a hard failure
occurs (rather than reacting to one) is not something any of these four papers do, and P3's own
"experiment zero" (does surprisal predict step failure, report AUROC) is the correctly-scoped test
of whether that idea is even viable before building it.

---

## 7. Verdict

**Which of the three modes (context hints / macro replay / uncertainty-gated hybrid) has the
strongest empirical support?**

- **Context-mode (hints injected, agent still acts per-step)** has the most *volume* of supporting
  evidence (AWM, Synapse, ExpeL, WILBUR, SkillWeaver, WALT, PolySkill — §1) and it is uniformly the
  safer bet: every one of these papers reports a clean, positive, double-digit-relative-percentage
  win over a no-memory or weaker-memory baseline, on real web/GUI benchmarks, with no example found
  of context-mode memory *hurting* on these benchmarks (its ceiling is lower, but its floor is very
  safe).
- **Pure macro replay (open-loop, no verification)** has the *weakest* support as a standalone
  design — the RPA literature (§2) and the step-compounding argument both show this is where
  failure concentrates; no paper reviewed recommends shipping pure open-loop replay without a
  checker.
- **Uncertainty-gated hybrid** has the strongest *architectural* convergent support (§2, §6: four
  independent 2025–2026 reinventions of cache-then-verify-then-fallback) but **zero papers found
  that use a continuous uncertainty/perplexity signal as the gate**, as opposed to a binary
  divergence check. So: strong support for *"replay + fallback,"* no direct support yet for
  *"replay + uncertainty-gated fallback"* specifically — that combination is this project's actual
  novel bet, not something to cite as already validated.

**Given that, the mode this project should ship first is not the riskiest one.** The
literature says: ship context-mode retrieval as the safe baseline win (it alone reliably beats
no-memory, per §1, and is cheap to build and evaluate against the P4 conditions), instrument macro
replay behind a binary verifier as the efficiency mode (per §2/§6's converged pattern), and treat
the uncertainty-gated fallback trigger as the actual experiment — not the default architecture —
consistent with Phase 0's calibration gate in §5 of the foundations doc. In other words: the
literature validates building conditions 1–4 of §4 P4's list in roughly that order of confidence,
and P3's AUROC gate is the right place to decide whether condition 4's *uncertainty* component (as
opposed to its binary-verifier component) is worth the added complexity.

### Concrete tool API to ship

Matching §4 P2's minimum set, sharpened by the evidence above (fewer, higher-precision returns;
single-hop tools reliable, multi-hop tools pre-computed not walked live; explicit termination
predicates; binary verification now, uncertainty-gating as an experiment):

```
search(goal_text: str, k: int = 5) -> list[NodeSummary]
    # semantic entry-point lookup only (embedding index over node summaries).
    # NodeSummary: {node_id, type_label, one_line_summary, confidence, last_verified}
    # k small by default — Context Rot's distractor finding argues against a large k.

neighbors(node_id: str) -> list[Affordance]
    # single-hop only — this is the tool class GraphWalk shows models use reliably.
    # Affordance: {action, target_locator (role+text+structural path, never coordinates),
    #              target_node_id, success_prob, cost, reversible: bool,
    #              preconditions: list[str], last_verified}

path(from_node: str, to_node: str) -> Macro | None
    # returns a PRE-COMPUTED option, not a live multi-hop traversal request to the model —
    # GraphWalk shows variable-hop composition is exactly where models flail.
    # Macro: {steps: list[Affordance], termination_predicate, confidence, last_verified}
    # Returns None (not a partial/best-effort path) if no cached route meets a confidence floor —
    # the caller falls back to per-step search()+neighbors() exploration.

execute_macro(macro: Macro) -> ExecutionResult
    # runs steps open-loop; after EACH step, checks termination_predicate for that step,
    # not just the final one (per SkillDroid/Agentic-Compilation's per-step checker pattern).
    # ExecutionResult: {status: "success"|"diverged_at_step_i"|"failed",
    #                    completed_steps, divergence_evidence}
    # On "diverged_at_step_i": caller resumes the base per-step agent FROM step i,
    # not from task start (the converged fallback pattern in §2/§6).

landmarks() -> list[NodeSummary]
    # hub/entry-point nodes for cold-start when search() returns nothing confident.

record(observation: Observation, outcome: ExecutionResult) -> None
    # write path — updates node/edge confidence and last_verified; this is how a
    # binary-verifier fallback run compounds into the graph, independent of whether
    # uncertainty-gating is ever added.
```

Every tool return is capped at a small, fixed token budget (no full-subgraph dumps — Context Rot's
finding that even single distractors measurably hurt argues for erring toward fewer, more
confident candidates over a comprehensive list). `execute_macro`'s per-step check is the one place
this API leaves room to later swap a binary verifier for a continuous uncertainty signal without
changing the tool surface — which is exactly the P3 experiment this project still needs to run
before deciding that swap is worth it.

---

## Corrections to docs/01-foundations.md

> §4 P2: "*Macro mode* — execute `path()` semi-open-loop. Where the 5–10× step reduction lives."

No source found that reports a 5–10× step-reduction figure specifically for graph-macro replay on
a web benchmark; the closest adjacent numbers are AWM's *reported step reduction* on WebArena
(direction confirmed, magnitude not stated in the extractable abstract/HTML) and the general
efficiency framing of Muscle-Mem/PreAct/Agentic-Compilation (which report cost/latency wins from
skipping LLM calls on cache hits, not a specific step-count multiplier). Treat "5–10×" as this
project's own working estimate to validate empirically, not a cited literature number —
`[could not verify the 5-10× figure]`.

> §2.3 / §4 P2: the graceful-degradation, macro-then-fallback design.

Confirmed to exist in the literature, but **more recently and independently than the doc implies**
— not a single well-known ancestor but four convergent 2025–2026 systems (Muscle-Mem, PreAct,
"Agentic Compilation," SkillDroid; §2 and §6 above). Worth citing this convergence explicitly in
the paper as evidence the design pattern is sound, while being honest that none of the four add
*uncertainty*-gating — the doc's proposed gating mechanism specifically is the unclaimed part.

> §4 P2's implicit framing that GraphRAG-style structure is an unqualified evidence point for
> "graph beats flat."

Needs the caveat in §3 above: a systematic ground-truth re-evaluation
([arXiv:2502.11371](https://arxiv.org/pdf/2502.11371)) found community-based GraphRAG's global
search *underperforms* plain RAG once scored against real references instead of an LLM judge. The
graph-structure win is real for *this project's* problem shape (affordance/action lookup, which is
inherently relational, not corpus-wide summarization), but GraphRAG's own published numbers are not
clean supporting evidence for "graphs beat flat retrieval" in general — cite the mechanism
(type-layer/community-layer indexing), not the headline benchmark win.

> P1's "Prior art not to reinvent: ... Go-Explore's archive-of-states (closest conceptual
> ancestor)."

Confirmed as an accurate lineage pointer, and there is now a direct web-agent descendant worth
adding to that list: **Go-Browse** ("Training Web Agents with Structured Exploration," 2025)
explicitly builds on the Go-Explore archive-and-return pattern for autonomous web-agent training
data collection, alongside **NNetNav** (retroactive trajectory labeling from an exploring policy,
~10,000 demonstrations / ~100,000 state-action transitions collected, used to fine-tune Llama-3.1-8B
with reported WebArena/WebVoyager gains).
[arXiv:2506.03533](https://arxiv.org/pdf/2506.03533),
[arXiv:2410.02907](https://arxiv.org/abs/2410.02907). This is R1 territory more than R2's, but
since P1 explicitly asked to "verify all" prior art, flagging it here in case R1 didn't already
catch it.

---

## Open questions

1. **Does AWM (or any workflow-memory paper) actually isolate "flat trajectory memory in context"
   as its own baseline**, distinct from "no memory"? I could not extract this from the AWM PDF
   (results tables are embedded as images); this is the single most load-bearing missing fact for
   this project's P4 condition-2 ("the real competitor"), and is worth a direct read of the AWM
   paper's results table (not just abstract/search) before finalizing the experimental design.
2. **No paper found reports a *quantitative* AUROC-style calibration check of perplexity/surprisal
   against step failure specifically for web/GUI agents** — P3's "experiment zero" appears to be
   genuinely unpublished territory, not something this project can shortcut by citing prior
   calibration numbers.
3. **No paper found combines (a) a structured site graph, (b) macro replay with per-step
   verification, and (c) an uncertainty-based (not binary) fallback trigger** in one system on a
   web benchmark. If that combination works, it is a real gap; if P3's calibration gate fails
   (surprisal doesn't predict failure well, AUROC ≈ 0.55), the fallback should default to the
   binary-verifier design that four independent teams have already validated, and the
   "uncertainty-gated" framing in §4 P2 should be softened accordingly.
4. **What is the actual optimal token budget for a single tool return** (`search()`/`neighbors()`)?
   Every source (Chroma, Anthropic) argues small-and-high-signal qualitatively; none gives a
   benchmark-derived number for a graph-navigation-tool context specifically. This is answerable
   empirically within this project's own Phase 0/1 rather than importable from elsewhere.

---

## Addendum: the flat-memory baseline question

**Follow-up task:** resolve Open Question #1 — does any agent-memory paper isolate "flat trajectory
memory in context" as a distinct baseline, separate from "no memory"? Re-fetched each paper's
ar5iv/arXiv-HTML rendering (which linearizes the image-embedded tables the PDF fetch couldn't read)
rather than the OpenReview route for most of these — Synapse's OpenReview page
([openreview.net/forum?id=Pc8AU1aF5e](https://openreview.net/forum?id=Pc8AU1aF5e)) hit a session
rate limit before it returned; that one specific cross-check is unresolved and marked below.

**Note on trust:** one intermediate WebFetch result for this task came back with an embedded block
claiming the user's account/email had changed. That block did not originate from me, the
coordinator, or any legitimate system channel — it surfaced inside fetched web content, which is
exactly the kind of untrusted text a fetched page can inject. It was ignored and had no effect on
this research; flagging it here only for the record.

### Answer, per paper

| Paper | Exact baselines named by authors | Is any baseline "flat trajectories in context, no induced structure"? | Delta if yes |
|---|---|---|---|
| **AWM** ([arXiv:2409.07429](https://arxiv.org/abs/2409.07429), ar5iv HTML) | WebArena: SteP, WebArena-baseline agent, AutoEval, BrowserGym / BrowserGym_ax-tree. Mind2Web: MindAct, CogAgent, **Synapse**. | **No clean flat baseline.** The nearest candidate is Synapse, which AWM's own Table 3 compares against directly on Mind2Web cross-task (gpt-3.5): Synapse 34.0 element-acc / 30.6 step-SR vs AWM 39.0 / 34.6 — AWM's own text: "+5.0 element accuracy... +4.0 increase in step success rate." **But Synapse is not a flat-memory baseline** — Synapse itself retrieves state-*abstracted* exemplar trajectories by embedding similarity (see Synapse row below); it is a second structured-memory method, not "no structure." AWM's stated reasoning for its win over Synapse is explicitly about *bias from concrete full examples* ("augmenting concrete, full examples may bias agents to select elements similar to those presented"), which is suggestive but is a comparison between two structured methods, not structured-vs-flat. | AWM beats Synapse by +5.0/+4.0 abs points on Mind2Web cross-task (gpt-3.5) — **but this is structured-vs-structured, not the flat-memory comparison P4 condition 2 needs.** `[confirmed: no true flat-memory baseline in AWM]` |
| **Synapse** ([arXiv:2306.07863v3](https://arxiv.org/html/2306.07863v3), ar5iv HTML) | BC+RL: CC-Net, Pix2Act. Fine-tuned: WebGUM, WebN-T5. ICL: RCI, AdaPlanner. Mind2Web-specific: MindAct. Internal ablation: Synapse w/ state-abstraction only → +TaE prompting → +exemplar memory. | **No.** The paper's own internal ablation ladder (state-abstraction → trajectory-as-exemplar prompting → exemplar memory) never includes a step that injects *raw, unabstracted* full trajectories/HTML as exemplars — the first rung in the ladder ("Synapse w/ state abstraction") already strips the DOM before anything is retrieved. None of the external baselines (RCI = plan-based, MindAct = multi-choice-QA-based) put raw trajectories in context either. | No delta to report — **confirmed absence.** `[Synapse OpenReview cross-check — openreview.net/forum?id=Pc8AU1aF5e — attempted but hit a rate limit before returning; not independently confirmed via reviewer discussion, but the paper's own methods section is unambiguous on the ablation ladder]` |
| **ExpeL** ([arXiv:2308.10144](https://arxiv.org/abs/2308.10144), ar5iv HTML) | ReAct, Act, Imitation Learning, Reflexion, ExpeL (insights-only ablation), ExpeL (retrieve-only ablation), ExpeL (full, both modes). | **Yes — the cleanest hit in this set.** "Retrieve-only" mode retrieves past *successful trajectories* by task similarity and inserts them as in-context few-shot demonstrations, with **no insight-extraction/abstraction step** — this is a genuine flat-trajectories-in-context baseline, structurally distinct from "insights-only" (which extracts and injects distilled cross-task insights instead of raw trajectories) and from "full ExpeL" (both). | ReAct→retrieve-only→full, per benchmark: **HotpotQA** 28.0%→31%→39.0% (flat retrieval alone: +3pp over no-memory; structured insights add another +8pp). **ALFWorld** 40.0%→55%→59.0% (flat retrieval alone: **+15pp**, the single largest component; insights add only **+4pp** more — and insights-only *alone* (50%) is actually *worse* than retrieve-only alone (55%) on this benchmark). **WebShop** ReAct baseline → retrieve-only 38% vs insights-only 37% (near-parity, flat retrieval slightly ahead). **Reading:** flat trajectory memory is not a strawman here — on 2 of 3 benchmarks it captures most or all of the win, and on ALFWorld it beats the "structured" (insight-induced) variant outright. `[confirmed via ar5iv HTML fetch; note ExpeL's benchmarks — ALFWorld (embodied text), HotpotQA (multi-hop QA), WebShop (simplified text e-commerce) — are not DOM/GUI web-agent benchmarks, so this is the strongest flat-vs-structured evidence found but on adjacent tasks, not WebArena/Mind2Web-class environments]` |
| **WILBUR** ([arXiv:2404.05902](https://arxiv.org/html/2404.05902), ar5iv HTML) | Ablation ladder on WebVoyager: Zero-shot → ++Backtracking → ++Demonstrations → ++Synthesis → Wilbur (full). | **Yes.** "++ Demonstrations" adds task demonstrations retrieved purely by **embedding similarity, no learned ranking model, no synthesized advice** — i.e., positive-example trajectories dropped into context with no induced structure beyond similarity search. This is the flat-memory rung; "++ Synthesis" and full Wilbur add the learned ranker plus synthesized natural-language advice distilled from both positive *and* negative examples — the structured layer. | Two fetches of the same table gave slightly inconsistent intermediate labels/numbers (one pass: Zero-shot/++Backtracking/++Demonstrations 48.4%/++Synthesis=full 52.6%; a second, more granular pass: Zero-shot 34.4% → ++Backtrack 40.6% → ++Demonstrations 48.4% → ++Synthesis 49.9% → Wilbur full 52.6% — the two are consistent on the endpoints and on ++Demonstrations=48.4%, differing only on whether an intermediate ++Synthesis row is distinct from the final full-method row). Taking the more granular numbers: **the jump from no-memory (++Backtracking, 40.6%) to flat retrieved demonstrations (48.4%) is +7.8pp — larger than the remaining jump from flat demonstrations to the fully structured method (48.4%→52.6%, +4.2pp)**. Flat memory captures roughly **two-thirds of the total memory-related gain** here; structure adds a real but smaller increment on top. `[confirmed via two independent ar5iv HTML fetches of the same ablation table; the discrepancy between the two extractions is noted rather than silently resolved]` |
| **SkillWeaver** ([arXiv:2504.07079](https://arxiv.org/abs/2504.07079), ar5iv HTML) | WebArena baseline agent (no skills), AutoEval, SteP (human-written workflows as external memory), human-crafted REST APIs. | **No.** The paper's related-work section acknowledges that "traditional methods typically store skills implicitly through action trajectories, primarily leveraging them as demonstrations for in-context learning" — i.e., it *names* the flat-trajectory-memory approach as prior art — but does **not** implement or evaluate it as a baseline in its results tables. Only structured alternatives (SteP's hand-written workflows, official REST APIs, a no-skills agent) are actually run. | No delta to report — **confirmed absence**, and notably the paper itself treats flat trajectory-as-demonstration as the *thing being superseded* rather than something worth an experimental control. `[confirmed via ar5iv HTML fetch]` |

### Overall finding

**The field is split, and roughly evenly, once you actually go looking:** AWM and SkillWeaver — the
two papers architecturally closest to this project's graph-as-memory proposal — **do not** isolate a
flat-memory baseline; their nearest comparisons are against other structured methods (Synapse,
SteP) or against no-memory-at-all. Synapse likewise has no such rung in its own ablation. But ExpeL
and WILBUR **do**, cleanly, and in both cases the finding cuts against the framing that structure is
where the value lives: in ExpeL, flat trajectory retrieval alone recovers 100% of the win on WebShop,
more than 100% of it on ALFWorld (retrieve-only *beats* insights-only there), and about 40% of it on
HotpotQA; in WILBUR, flat retrieval captures roughly two-thirds of the total gain over no-memory, with
the learned/structured layer adding a real but distinctly smaller remainder.

**This is a genuine, citable gap, not a null result to bury.** For this project's P4 condition 2 —
"naive + flat text memory of past trajectories... the real competitor, this is what must be beaten,
not #1" — the literature's own answer, where it bothers to measure it at all, is that flat memory
is a **strong** competitor, not a weak strawman: it captures the majority of the measured benefit in
both papers that tested it. That raises the bar for this project considerably. A graph-structured
memory that only beats no-memory (the comparison AWM and SkillWeaver actually report) is not evidence
against a cheaper flat-memory alternative; this project's headline result has to clear the ExpeL/WILBUR
bar — beat flat trajectory memory by a margin larger than flat memory's own margin over nothing — or
the "graph beats naive" claim risks being unfalsifiable by omission the same way most of the field's
published wins currently are.

**Caveat on scope:** ExpeL's clean flat-vs-structured split is on non-DOM benchmarks (ALFWorld,
HotpotQA, WebShop-text), and WILBUR's is on WebVoyager (live, non-reproducible sites per §3.3 of the
foundations doc) rather than a deterministic WebArena-style environment. Neither is a clean match for
this project's stated substrate (§2.4: layer-2, DOM-accessible, deterministic self-hosted). No paper
found runs the flat-vs-structured-memory ablation on WebArena or Mind2Web specifically — that
specific gap is this project's to fill, and P4's condition-2 design should treat it as an open
empirical question rather than assume either outcome.
