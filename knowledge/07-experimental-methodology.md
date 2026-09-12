# Experimental methodology

Sources: R5, R4 §5–7, and root recomputation (✓). How to make "graph beats flat" mean what it says.

## Confound audit (ranked by likelihood of biting)

| # | Confound | Evidence it's real | Control |
|---|---|---|---|
| 1 | **Unequal tool-call / compute budget** | Environment Maps: map arm 12.06 tool calls/task vs 1.15 (traces) vs 0.71 (baseline); no compute-matched rerun | Hard shared caps on tool calls, tool-return tokens, and wall-clock; log consumption as a first-class column |
| 2 | **Free, unamortized exploration** | Common; Environment Maps reports $1–4/site ✓ but never folds it in | Amortization curve (below) |
| 3 | **Token-length mismatch across arms 2–5** | Raw Playwright traces are a noisier substrate than a curated map | One token budget on tool returns, enforced for every memory arm |
| 4 | **Task selection** | Archetypes aren't graph-neutral | Freeze and hash-commit the task list and strata before Phase 2; report every subgroup, nulls included |
| 5 | **Differential tuning effort** | Invisible after the fact | Log prompt iterations and engineering time per arm; freeze arms before eval; ideally a different person owns arm 2 |
| 6 | **Crawl-to-eval leakage** | Environment Maps doesn't state held-out tasks ✓ (22% trace coverage); trace-covered 33.0% vs non-trace 26.9% | Task-agnostic crawler; freeze its config before opening task files; split WorkArena by template |
| 7 | **Evaluator leakage** | A correlated judge favors verbose arms | Programmatic validators for the primary metric; actor and judge never share a checkpoint; human-labeled subset |
| 8 | **Residual prompt asymmetry** | Graph arms need tool instructions | Byte-identical non-tool system prompt; publish diffs |

## Arms

| # | Arm | Isolates |
|---|---|---|
| 1 | No memory | Floor |
| **2** | **Flat top-k retrieval over clean step logs, token-budget-matched** | **Primary competitor** |
| 2a | Token-matched raw dump (recency / relevance / random subsets) | Retrieval vs none; fills the real-information-no-structure cell |
| 3 | Graph, context mode | Structure as hints |
| **4** | **Graph, macro + gate** | **Primary treatment** |
| 5 | Distractor graph, matched on tokens and PPL | Information vs tokens |
| 6 | Random-walk graph at equal crawl cost | Exploration shape vs coverage |
| 7 | Oracle graph | Ceiling |

- **Same source data:** arms 2 and 4 draw on the same crawl logs plus the same accumulated eval
  trajectories, so 4-vs-2 contrasts structure only.
- **Also sweep crawl budget** for the graph arms. One crawl budget gives one x-value; the curve is the
  result.
- **Strawman warning:** Environment Maps' flat arm grepped raw trace files, "a format not designed for
  LLM consumption." A weak arm 2 makes any null or positive uninterpretable.

## Amortized cost accounting — not standard practice; specify it

Environment Maps and RAGSearch each report half the accounting (construction cost, per-query cost).
**Neither plots the crossover.** Rules:

1. **Unit:** USD at a stated rate card, with tokens/steps/wall-clock reported alongside, never
   substituted. Include:
   - every Phase 1 LLM call, including aborted branches, the risk classifier, and the scorer
   - offline graph construction, plus human curation time at a stated rate
   - per-episode execution, tool calls included
   - storage, excluded explicitly
2. **Plot per site per stratum:** x = cumulative USD on that site. The naive curve starts at 0 with flat
   marginal cost; the graph curve starts with a vertical jump (crawl) then its own marginal cost.
   y = cumulative success with a CI band.
3. **Two crossovers, both reported:**
   - **Cost-crossover N:** smallest N with `construction + N·marginal_graph < N·marginal_naive`.
   - **Significance-crossover N:** smallest N where the CIs separate.

   Reporting only the first overclaims. If neither is reached within the site's task volume, that is
   a first-class result.

**Iso-cost view** (Snell et al., 2408.03314): sweep budget B and report `success(arm | cost ≤ B)`.
This credits adaptive spend, which is what gated macros do.

## Statistics

- **Primary:** pre-registered exact McNemar on arm 4 vs arm 2, uncorrected. Cross-check with
  mixed-effects logistic regression using a **task random intercept**, and check whether it collapses
  to the simple model.
- **Secondary:** Cochran's Q across arms, then pairwise McNemar with **Benjamini–Hochberg FDR**
  (2605.00428). Never pick the headline pair after looking.
- **Effect sizes:** paired bootstrap CIs, 10,000 resamples, task-level pairing preserved.
- **Seeds:** nested within task as repeated measures, never extra tasks.
- **Why task effects dominate:** generalizability analysis of agent leaderboards (TheAgentCompany,
  τ²-bench, AppWorld) finds the agent main effect <3% of variance and agent×task interaction 7–23%.
  Not yet confirmed on WebArena.

### Sample size ✓ (10pp, α=.05 two-sided, 80% power)

| ψ (discordant rate) | 0.15 | 0.20 | 0.25 | 0.30 | 0.40 |
|---|---|---|---|---|---|
| Paired tasks | 116 | 155 | 194 | 234 | 312 |

- GitLab + CMS (362 tasks) covers ψ up to ≈0.45. One site (180) covers ψ only up to ≈0.23.
- Estimate ψ from the pilot and put it in the pre-registration.
- **Realistic expectation** (R5): a well-controlled 4-vs-2 contrast lands anywhere in **0–15pp**, not a
  multiple of baseline.

## Reproducibility

An audit of agent-benchmark papers (2605.21404) scored them against a five-field disclosure schema:
**mean score 0.38**, **none disclosed cost**, and **none pinned a container digest**. Pin per run:

- **Model:** provider, exact string, **run date**.
- **Inference:** engine + version, sampling params, seed (or its explicit absence), per-task token
  cap, any aggregation rule.
- **Harness:** commit, verbatim system prompt (or its hash), tool inventory, stopping rule.
- **Environment:** container **digest** (`sha256:…`), snapshot/version, reset procedure.
- **Cost:** full table.
- **Failure taxonomy** per task: grounding / wrong page / tool error / verifier disagreement / timeout.

Use **WebArena Verified** / corrected labels rather than raw WebArena.

## Negative-result plan

- A null is informative **only if** arm 2 is strong, the amortization budget was large enough for a
  true effect to cross over, and the calibration gate passed first.
- **Publishable null:** "graph memory amortizes for configuration/routine tasks within N, not for
  transactional tasks within any tested budget, and type-layer transfer does not survive the
  distractor control."
- **Pre-register the Phase 3 transfer criterion now.** Environment Maps' 0/48 ✓ says a null is likely.

## Minimal falsification (run first)

Phase 0 pilot (~50 tasks): arm 1 vs **arm 2**, plus uncertainty calibration. Environment Maps gives
the prior: flat took 65% of the gain ✓. If flat retrieval already captures most of the gap on the
pilot, building the full graph needs a pre-stated reason to continue, e.g. that the pilot's tasks
aren't multi-hop or configuration-shaped.
