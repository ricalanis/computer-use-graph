# Design v0.2: graph memory for web agents, revised after the verification pass

**Status:** v0.2 draft. Supersedes `01-foundations.md` for design decisions. §1–§2 of v0.1 (the
taxonomy and the action-space ladder) remain the conceptual reference and are not repeated here.
All six dossiers are incorporated. The benchmark choice in §3 departs from R4's recommendation; the reasons are given there.
**Sources:** `research/R0`–`R5` dossiers; claims root re-fetched are in
`research/00-verification-log.md` and marked ✓ below. Unmarked citations rest on a worker's
retrieval only.

---

## 1. What changed, in one screen

1. **The core experiment has partly been run already.** *Environment Maps* ✓ ([arXiv:2603.23610](https://arxiv.org/html/2603.23610))
   compared no memory, raw trajectory access, and a structured map on all 812 WebArena tasks:
   **14.2% → 23.3% → 28.2%**. "Graph beats naive" is no longer a contribution by itself.
2. **Flat memory is the real competitor.** It captures roughly **two-thirds** of the memory win in
   two root-verified results: Environment Maps (9.1 of 14.0pp) and WILBUR ✓ (7.8 of 12.0pp). The
   primary contrast is **graph vs flat**, not graph vs none.
3. **Structure's value is site-dependent.** Over flat trajectories the map adds ~0 on Map
   (34.9 → 34.9) and Reddit (58.5 → 60.4), but **+11.1pp on GitLab and +7.1pp on CMS** ✓. These are
   the configuration and admin-heavy sites. That evidence points Phase 1–2 at a
   configuration-heavy site.
4. **Step-level uncertainty gating is contradicted at long horizons.** *Last Step Matters* ✓
   ([arXiv:2608.29685](https://arxiv.org/abs/2608.29685)): no uncertainty signal beats AUROC 0.60
   at 50% trajectory progress, versus 0.85 for verbal confidence at completion, because agents
   *path-switch*. The paper recommends restart gating over mid-course intervention. v0.1's Phase 0
   gate measured the wrong label.
5. **Naive surprisal-driven crawling fails on real sites.** Ads, timestamps, carousels, and CSRF
   tokens are a *noisy TV*: permanently surprising and useless for navigation. The stopping rule
   has to measure **learning progress** ✓ ([arXiv:2509.25438](https://arxiv.org/abs/2509.25438)),
   not surprisal level, and it has to be computed over type-abstracted states.
6. **The macro-plus-fallback architecture is established.** Four 2025–26 systems converged on
   cache → per-step check → resume from the failure point. All four gate on *binary* divergence.
   A continuous gate is unclaimed, but item 4 means it may be the wrong granularity.

### Where novelty still plausibly lives

Environment Maps leaves these open, and together they form this project's contribution surface:

| Gap in the closest prior work | This project |
|---|---|
| Map built from **179 human recordings** | Map built by **autonomous, safety-gated exploration** |
| Eval tasks **not stated to be held out** from map sources (~22% of tasks have trajectories) ✓ | Pre-registered **crawl/eval firewall** |
| Map construction cost reported but **not amortized into the comparison** | **Amortization curve**: success vs cumulative USD including exploration |
| Binary divergence checks (replay literature); no gating in Environment Maps | Uncertainty gating tested at **step and episode granularity**, with restart as a first-class option |
| Per-site maps; multi-site **0/48** ✓ | **Type-layer transfer** across sites, with a pre-registered success criterion |

**Consequence: the hypothesis sharpens.** *An autonomously explored, type-abstracted site graph beats
token-matched flat trajectory memory at equal amortized cost on configuration-heavy sites. An
uncertainty signal calibrated against episode outcome decides when to trust it.*

---

## 2. Substrate (revisions to v0.1 §2)

The decision stands: **layer-2 element-targeted actions over an a11y-tree candidate set, executed by
Playwright.** R0's verdict is that this is right *because* categorical entropy needs an enumerable
candidate set, not because layer 2 is the correct substrate for computer use in general. Revisions:

- **Real systems span rungs; they don't sit on one.** BrowserGym ✓ switches rung via
  `ACTION_SUBSETS` (`bid` = layer 2, `coord` = layer 1) in one codebase, and browser-use and
  AndroidWorld keep coordinate fallbacks. The ladder is a menu the harness selects from per call.
  Useful side effect: a layer-1 vs layer-2 ablation is a config change, not a rewrite.
- **The a11y tree is noisy, not ground truth.** Snapshots can include off-screen or unreachable
  elements (Playwright issue #39955, not root-verified). **Filter candidates for actionability**
  (visible, enabled, receives events) *before* computing entropy. Otherwise entropy partly measures
  phantom elements.
- **"Monotone" holds in expectation on standards-compliant apps, not as a guarantee.** Layer 4 can be
  *less* reliable than layer 2 on poorly instrumented UIs.
- **Unsourced numbers become measurements.** v0.1's "100k+ token trees" and "~50× cost across rungs"
  have no source. Phase 0 measures pruned-tree token counts and per-step cost for the chosen models.
- **Options are an import.** No GUI/web paper uses Sutton–Precup–Singh vocabulary. Present it as a
  formal import and cite AWM, NNetNav, and workflow-guided exploration as the unframed prior art.
- **CodeAct is not GUI evidence.** Its gains (≈20% success, 30% fewer turns) come from API/tool-use
  benchmarks. Code-as-action over layer-2 primitives is recorded as a road not taken.
- **Layer 3 does not bypass CSRF.** It breaks controlled-input value tracking and `isTrusted`-gated
  listeners.

---

## 3. Benchmark, harness, and validators

### 3.1 Decision: WebArena GitLab + CMS primary, WorkArena L1 as replication

| Role | Environment | Tasks | Why |
|---|---|---|---|
| **Primary** | WebArena **GitLab** + **CMS**, using corrected task labels | 180 + 182 = **362** ✓ | Structure beat flat memory on exactly these sites (+11.1 and +7.1pp) ✓. Docker self-hosted, so fully reproducible. Lets us reproduce Environment Maps' arms before any novel arm runs. |
| **Replication** | WorkArena **L1** (ServiceNow) | 19,912 instances of **33 templates** ✓ | The routine-repeat regime, the amortization curve's natural home. |
| Stretch | WorkArena++ | 682 tasks ✓ | Compositional, long-horizon. |
| Tool-API pilot only | WebShop | one synthetic site | Cheap iteration on `search`/`path` ergonomics. Single task type, so it doesn't count as evidence. |

**Where this departs from R4.** R4 recommends WorkArena as primary because it is literally one
site. Three reasons against making it primary:
1. **Its effective n is 33, not 19,912.** Instances of one template share their navigation path, so
   they aren't independent McNemar observations, and a graph that has seen one instance has
   effectively seen the template. It would need template-level random effects and a firewall split by
   template, and 33 clusters is thin.
2. **It isn't self-hosted.** Instances come from a hosted pool behind Hugging Face authentication ✓,
   on a proprietary platform, which adds a reproducibility dependency WebArena's Docker images avoid.
3. **No evidence yet that structure beats flat memory there.** The site-level evidence we have
   (Environment Maps) is on WebArena.

WorkArena stays valuable as replication: if the effect exists, the routine-repeat regime is where
amortization should look best.

**Autonomous exploration makes the firewall cheap.** The Phase 1 crawler is task-agnostic and never
sees task text, so no eval tasks are spent on crawl seeds, and all 362 stay available for evaluation.
The only leakage path left is a human choosing crawl heuristics while looking at tasks. Fix the
crawler config before opening the task files.

### 3.2 Harness
**BrowserGym + AgentLab** ✓. It is maintained and ships per-benchmark action subsets including
`webarena` and `workarena` ✓. Two pieces have to be built:
- **Graph tools** exposed through the environment's custom `action_mapping` extension point.
- **Per-step logprob and candidate-set logging.** It is not provided. Thread the scorer's output
  through the agent-info trace fields.

For budgeting, the BrowserGym ecosystem paper reports $100 for 330 WorkArena-L1 episodes
(9.0 steps average) with Claude 3.5 Sonnet (not root-verified).

### 3.3 Validators
- **Programmatic validators under-credit** ✓ (AgentRewardBench: rule-based evaluation "tends to
  underreport the success rate"). **LLM judges over-credit.** These are opposite biases, so they
  can't be lumped together as "brittleness."
- Prefer tasks scored by **state checks** over tasks scored by fuzzy/LLM matching, and report the
  split.
- **Human-label ~50 trajectories per site** across arms. Report the validator's precision and recall
  against those labels next to the headline number. If validator error differs by arm (for example,
  macro runs finishing in states the validator misreads), the comparison is biased, so check recall
  **per arm**.
- Use corrected WebArena labels. A manual audit corrected 71 of 812 tasks (Surfer 2,
  arXiv:2510.19949; not root-verified).

---

## 4. P1 — State abstraction and graph construction (revised)

**Recharacterized prior art.** NNetNav, AWM, and skill induction **do not build persisted graphs**.
NNetNav is prior art for the *exploration policy* and trajectory relabeling. AWM is flat
natural-language workflows. Skill induction is a flat program library, closer to P2's options. The
state-abstraction problem is under-cited: web-app testing has 15+ years on it (Crawljax's
configurable state-abstraction function, near-duplicate detection, template detection and wrapper
induction). **Reuse that; don't reinvent it.**

**Go-Explore needs a resettable simulator.** Its "return to archived state" step assumes one. WebArena
provides resets; the live web does not. This is one more reason causal claims stay on self-hosted
environments.

**Node identity is layered:**
1. **Primary key** = (URL *template*, stripped DOM-skeleton hash). Template-ize path and query
   variables that vary across instances sharing a skeleton. Before hashing, strip volatile content
   (timestamps, prices, ad slots, tokens) Crawljax-style and keep tag, role, and structural path.
2. **Embedding is a merge signal only.** It clusters nodes the primary key over-splits (A/B layouts,
   markup churn). It is never the identity key, and merges are reviewed, not silent.
3. **Type layer** = clustering over instances. An LLM names each type for display, never for
   identity. A type carries the union of affordances seen across its instances. *No published
   system does this for agent affordance graphs, so this part is ours to build and validate.*
4. **Hidden state is not in node identity.** Auth, cart, active filters, and open modal form a small
   factored **episode context vector** that edges check as **preconditions**. This avoids the node
   explosion that fine-grained abstraction causes.

**Edge schema:**
```
edge = {
  source_type, source_instance, target_type, target_instance,
  affordance: { role, accessible_name, structural_path },   # never coordinates
  action: { type, params },
  preconditions: { auth, cart_nonempty, filters, modal_open },  # each nullable
  risk_tier: SAFE | LOW | HIGH,
  reversible: bool,
  success_prob, observed_cost,
  termination_predicate,      # verifies option completion; doubles as staleness probe
  last_verified, decay_policy
}
```

**Safety gate.** The best available classifier, WebGuard ✓, reaches **76% recall on HIGH-risk
actions** after fine-tuning, and frontier LLMs score under 60%. That is a gate, not a safeguard.
**HIGH-risk edges are excluded from exploration.** They run only when a task deliberately targets
them, after a first-traversal confirmation.

**Staleness.** A failed termination predicate during normal use is the free staleness signal.
Scheduled re-verification covers only low-traffic types, at a rate set by observed drift.

---

## 5. P2 — Graph as memory and tools (revised)

**Ordering by evidence strength:**
1. **Context mode** (hints, per-step acting) is the safe baseline, backed by several positive
   results and no found harms.
2. **Macro mode with a binary per-step verifier** is the efficiency mode, and the design four
   independent systems converged on.
3. **Uncertainty gating** is *the experiment*, not the default. It is conditional on §6's revised
   gate.

**Tool API:**
```
search(goal_text, k=5) -> [NodeSummary]         # entry points only; small k (distractors hurt)
neighbors(node_id) -> [Affordance]               # single-hop: the tool shape models use reliably
path(from, to) -> Macro | None                   # PRE-COMPUTED option; None below confidence floor.
                                                 # Never ask the model to compose multi-hop walks.
execute_macro(macro) -> {status: success | diverged_at_step_i | failed,
                         completed_steps, divergence_evidence}
                                                 # checks termination predicate after EACH step;
                                                 # on divergence, base agent resumes FROM step i
landmarks() -> [NodeSummary]                     # cold start
record(observation, outcome) -> None             # write path; updates confidence, last_verified
```
Every return has a fixed, small token cap. `execute_macro`'s per-step check is the only seam where
a continuous signal could later replace the binary one without changing the tool surface.

**Don't cite GraphRAG as "graphs beat flat."** Against references, its global search
underperforms plain RAG ✓ (QMSum ROUGE-2 3.23 vs 6.32). Its earlier wins came from position-biased
LLM judges. Cite the indexing mechanism, not the headline number.

---

## 6. P3 — Uncertainty (revised)

### 6.1 Instrumentation
- **One fixed open-weights scorer, separate from the actor.** This is now mandatory, not a
  preference: Anthropic's API exposes no logprobs, and OpenAI's Responses API reportedly doesn't
  either.
- **vLLM `prompt_logprobs` with prefix caching disabled.** Combining the two crashed in 2024
  (#3251, #8268 ✓), and #8268 was closed as stale with no fix. Pin the version and run a golden
  regression before trusting numbers: score a fixed prompt with caching off vs on.
- Score each candidate as the summed token logprob of its continuation over a shared prefix.

### 6.2 Signals, in build order
1. **Normalized action entropy** H(p)/log N over the actionability-filtered candidate set. This is
   the primary signal.
2. **Verbalized confidence** from the actor. It costs nothing, is the strongest reported
   end-of-trajectory signal (0.85 ✓), and serves as the baseline the scorer signals must beat.
3. **Sampling disagreement** at k≈5, clustered by action equivalence. It needs no logprobs.
4. **World-model surprisal** over the next observation's *type label*, not raw content, with the
   graph in context vs a control. Build it last, and only after the type layer exists. Scoring type
   labels is what de-noises it.
5. Literal Bayesian surprise with a persistent belief state: **not built.** No LLM-agent precedent
   exists. The two-forward-pass KL is a proxy and is described as one.

### 6.3 The calibration gate, redesigned
Report AUROC of each signal against **two labels**:
- (i) **step failure**, and
- (ii) **eventual episode failure**, bucketed by trajectory progress: 0–25, 25–50, 50–75, 75–100%.

**Decision rule, pre-registered (thresholds are proposals to confirm):**
- If (ii) ≥ 0.70 by the 50% bucket, **step-level gating** is licensed, meaning early fallback to
  exploration.
- If (ii) is informative only in the last bucket, as *Last Step Matters* predicts, switch to
  **episode-level restart gating**. That design is less novel but honest.
- If neither holds, drop uncertainty gating and ship the binary verifier. The paper becomes graph
  vs flat under amortized cost.

Web tasks are shorter and more state-revisitable than the deep-research agents in *Last Step
Matters*, so path-switching may bite less. **That transfer question is itself a result.**

### 6.4 Controls
- The **length confound** needs a distractor graph **matched on token count and its own
  unconditioned perplexity**, averaged over ≥5 draws to form a null band. A plain shuffle is not
  enough, because shuffled text carries different intrinsic perplexity than fluent-but-wrong text.

### 6.5 Crawl stopping rule
`stop when mean_surprisal(window t−1) − mean_surprisal(window t) < ε`. Windows are batches of newly
crawled states **of the same inferred type**, and surprisal is type-label surprisal. This is learning
progress, not surprisal level.

---

## 7. P4 — Experimental design (revised)

### 7.1 Conditions: eight arms, not six
| # | Condition | Isolates |
|---|---|---|
| 1 | Naive, no memory | floor |
| 2 | **Flat top-k trajectory retrieval, token-budget-matched to the graph** | **primary competitor** |
| 2a | Flat raw-trajectory dump, token-matched | retrieval vs no retrieval |
| 3 | Graph, context mode | structure as hints |
| 4 | **Graph, macro mode + gate** (granularity per §6.3) | **primary treatment** |
| 5 | Distractor graph (token- and PPL-matched) | information vs tokens |
| 6 | Random-walk graph (real site, uninformed exploration) | curiosity vs coverage |
| 7 | Oracle graph (hand-built) | ceiling |

- **Primary contrast: 4 vs 2.** Pre-registered, uncorrected.
- **Hard, identical budgets** on tool calls and tool-return tokens across all arms, with actual
  consumption logged as a first-class column. R5 reports large tool-call disparities between arms in
  Environment Maps (not root-verified).
- **Same source data for arms 2 and 4.** Flat memory (arm 2) retrieves over the **same crawl logs**
  the graph (arm 4) is built from, plus the same trajectories accumulated from earlier eval tasks in
  the amortization sequence. That makes 4-vs-2 a contrast of *structure alone*, holding information
  fixed, which is the Environment Maps design applied to autonomous exploration.
- **Firewall.** The crawler is task-agnostic (§3.1), so every task is held out by construction.
  Freeze the crawler config before anyone opens the task files. With WorkArena, split by template.

### 7.2 Analysis plan
- **Primary:** exact McNemar on 4 vs 2, cross-checked by mixed-effects logistic regression with a
  task random intercept.
- **Secondary:** Cochran's Q across arms, then pairwise McNemar with Benjamini–Hochberg FDR.
- Paired bootstrap CIs (10,000 resamples, task-level pairing) on every point estimate.
- **Amortization curve per site:** x = cumulative USD *including exploration*, y = cumulative success
  with CI band. Report both the **cost-crossover N** and the **significance-crossover N**, and state
  plainly if the site's task volume never reaches them. Tokens, steps, wall-clock, and tool calls go
  in an appendix table and are not collapsed into the primary axis.
- Report per-archetype results unconditionally, nulls included.
- **Sample size.** Detecting a **10pp** paired difference at α=.05 (two-sided) and 80% power needs
  ✓ (root-recomputed):

  | Discordant-pair rate ψ | Paired tasks needed |
  |---|---|
  | 0.15 | 116 |
  | 0.20 | 155 |
  | 0.25 | 194 |
  | 0.30 | 234 |
  | 0.40 | 312 |

  The pooled **362** GitLab + CMS tasks (site as a stratum) cover ψ up to ≈0.45. One site alone
  (180) covers ψ only up to ≈0.23. **The v0.1 "≥50 tasks/condition" is underpowered by 2–6× for
  significance testing.** 50 tasks remains adequate for the Phase 0 AUROC calibration. The pilot
  estimates ψ, and the ψ it measures goes into the pre-registration.
- **Seeds.** Use ≥3 seeds per task, modeled as repeated measures (task random intercept), not as
  extra tasks.
- **CIs.** Wilson intervals. At n=50, p=0.5 the half-width is ±13.4pp; that is the band's worst
  case, narrowing to ≈±11pp at p=0.2 ✓.

### 7.3 Reproducibility record, per run
Model + version + date · harness commit + verbatim prompt + tool inventory + stopping rule ·
container **digest** · inference engine + sampling params + seed (or its explicit absence) · full
cost table · structured failure taxonomy per task.

---

## 8. Revised experiment sequence

**Phase 0a — kill tests (≈ half a day, no graph, no crawl infrastructure).**
1. **Noisy-TV check:** crawl a few dozen pages on the chosen site. Does raw next-observation
   surprisal saturate with budget, or stay high? Does type-label surprisal saturate?
2. **Path-switching check:** on any small set of logged trajectories, compare signal AUROC against
   step failure vs episode outcome by progress bucket.

**Phase 0b — pilot (~50 WebArena GitLab tasks).**
Arms 1 and 2 (flat retrieval), with full uncertainty instrumentation (§6.2 signals 1–3) and cost
measurement. Also human-label the pilot trajectories to measure validator precision/recall (§3.3). *Deliverables:* the §6.3 AUROC table, the flat-memory gain, the discordant-pair rate
for power analysis, and measured token/cost per step.
**Proceed/redesign gate, pre-registered and hash-committed before any graph is built.**

**Phase 1 — autonomous map building** on the crawl-seed partition, with the risk-tier gate and the
§6.5 stopping rule. *Deliverables:* two-layer graph, learning-progress curve, and exploration cost
in USD.

**Phase 2 — the eight-arm comparison** on all 362 GitLab + CMS tasks (held out by construction, §3.1). *Deliverables:* primary 4-vs-2 contrast,
amortization curve, and per-archetype table.

**Phase 2r — replication** on WorkArena L1, analyzed with template-level random effects.

**Phase 3 — type-layer transfer** to a second site, with a success criterion **pre-registered
now**. Environment Maps' 0/48 multi-site result says a null is likely, so it must be reportable.

---

## 9. Open decisions (updated)

1. **Primary benchmark.** Recommended: **WebArena GitLab + CMS**, with WorkArena L1 as
   replication (§3.1). R4 recommended WorkArena as primary. The trade is statistical independence and
   reproducibility against routine-repeat realism. Operator's call.
2. **Gating granularity.** Step vs episode is now decided *by* Phase 0b data under the §6.3 rule,
   not up front.
3. **Deliverable shape.** Paper or working system. It decides whether the §6.3 gate is binding.
4. **Scorer model.** The fixed open-weights model, and its size relative to the actor.
5. **Reproduce Environment Maps first?** Recommended. Run arms 1/2a/3 on GitLab and check we land
   near their per-site numbers (8.3 / 11.7 / 22.8) ✓ before any novel arm runs. If we don't, the
   harness is off, not the hypothesis. Their setup used a different agent SDK, so expect some gap and
   set the tolerance in advance.
