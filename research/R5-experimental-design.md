# R5 — Experimental design, baselines, and causal attribution

**Role:** methodological adversary to `docs/01-foundations.md` §4 P4 and §5.
**Scope:** does not touch other files. Every methodology claim below is either sourced to a
retrieved URL or marked `[could not verify]` with what was searched. Web search budget for this
session was exhausted partway through (shared across parallel research workers); remaining gaps
are marked explicitly rather than filled with recollection.

---

## 0. Headline finding before the detail

While researching Q8 I found a paper that has, in effect, **already run something very close to
the experiment §5 proposes** — same benchmark (WebArena), same idea (a structured graph built
from trajectories vs. a flat/raw-trajectory baseline vs. a no-memory baseline), same actor model
family. This is not a tangential citation; it is the closest thing to a dry run of P4 available,
and it reproduces several of the confounds named below in the wild. It is discussed throughout,
not just in Q8.

**Environment Maps: Structured Environmental Representations for Long-Horizon Agents**
(arXiv:2603.23610, fetched via `arxiv.org/html/2603.23610`). WebArena, 812 tasks, three
conditions, same base agent (`claude-sonnet-4-5`) and step/timeout limits across conditions:

| Condition | Success | 95% CI |
|---|---|---|
| No-map baseline (session-bound context) | 14.2% | [11.9, 16.7] |
| Raw trajectory access (Playwright trace files, agent greps them) | 23.3% | [20.5, 26.3] |
| Environment Map (structured graph built from those same trajectories) | 28.2% | [25.2, 31.4] |

This is condition 1 vs. a version of condition 2 vs. a version of condition 3/4 from §4 P4,
already run. Read section 3 (Q3) and section 1 (Q1) below for what it gets right and wrong.

---

## 1. Confound audit (Q1)

Ranked by estimated probability of actually biting in this specific experiment (not just
theoretical possibility), with the neutralizing control for each.

### 1.1 Unequal tool-call / compute budget across conditions — **highest risk**

This is not hypothetical: it is exactly what happened in the Environment Maps paper. Fetched
detail: the map condition averaged **12.06 tool calls per task** (median 9) against **1.15** for
raw-trajectory access and **0.71** for baseline, and "92% of tasks involve file access" under the
map condition vs. 3.2% under trajectory access. The authors' own justification — "maps are
structured text with simple indices" so naturally more queryable — is true but does not neutralize
the confound; it *is* the confound. A condition that is allowed to spend 10x more tool calls and
inspect more evidence per task is being compared at unequal inference-time compute, and the paper
reports no compute-matched re-run. `docs/01-foundations.md` §4 P4 lists "more compute" as a named
confound but does not specify how the design prevents it.

**Control:** fix a hard budget shared across all six conditions — max tool calls, max output
tokens read from tools, max wall-clock — not just max agent steps. Report tool-call count and
token count actually consumed per condition as a first-class result column, not a footnote, so a
reviewer can see whether the budget bound bound or the conditions differ anyway.

### 1.2 Extra context tokens (the length confound) — **high risk, already partly addressed**

§4 P4 condition 5 (shuffled-graph control) is the right control and P3 already states the general
principle ("the mandatory control is a shuffled/scrambled graph of identical token count"). Two
gaps: (a) the same token-matching discipline is not stated for conditions 2 vs. 3/4 — a flat-text
trajectory dump and a graph over the same trajectories are not guaranteed to be token-matched
unless explicitly built to be; (b) the Environment Maps paper's own trajectory-access condition
used raw Playwright trace JSONL (verbose, includes screencast frame references, network events) —
a much noisier text substrate than a curated graph, so its 23.3% vs. 28.2% gap is confounded with
substrate cleanliness, not just structure. **Control:** define "token budget for tool returns" once
(§4 P2 already gestures at this — "a token budget on tool returns") and enforce it identically for
conditions 2, 3, 4, 5.

### 1.3 Free/unamortized exploration cost — **high risk, this is P4's own named problem**

Covered in depth in §3 (Q3) below. Rank it high because it is the single most common way this
class of paper misleads: report success rate with the map already built, and never divide by
(construction cost + eval cost). The Environment Maps paper is a partial counter-example — it does
report construction cost ($1–4, 13–31 minutes per site) — but even there the cost is stated as an
aside, not folded into a crossover-point plot against the 812-task eval set. §5's Phase 2 plan says
the right thing ("success vs. cumulative cost... crossover point") but nothing in the document
specifies the accounting rules, which is exactly what a skeptical reviewer will ask for first.

### 1.4 Task selection favoring the graph condition — **medium-high risk**

§1.5 already flags that archetypes are not graph-neutral ("information-seeking... graph-friendly";
"transactional... graph may not amortize"). The risk is in *which* tasks get sampled for the 50+
tasks/condition minimum in §4 P4. If task sampling is not stratified by archetype and pre-registered
before running any condition, a researcher (even unconsciously) can retain "good" seeds/tasks for
the report. **Control:** freeze the task list and archetype stratification (§1.5's five archetypes,
or at minimum info-seeking vs. transactional) *before* Phase 2 begins, hash-commit it, and report
per-archetype breakdowns unconditionally — this is exactly what the Environment Maps paper did well
(Figure 2b breaks down by environment/domain and shows the map's advantage is concentrated in
GitLab/CMS, near-zero incremental value on Reddit, and literally zero improvement — 0/48 for every
condition — on multi-site tasks). Report the null subgroups; do not average them away.

### 1.5 Differential tuning effort ("we debugged condition 4 for three weeks, condition 2 for a
day") — **medium risk, hard to audit externally**

The naive+flat-memory competitor (condition 2) is explicitly named "the real competitor" in P4, but
nothing in the document commits to giving it equal engineering effort (prompt iteration, retrieval
tuning, context-window packing). This is the most reviewer-legible version of "sandbagging the
baseline," and it is invisible after the fact unless logged. **Control:** log prompt/iteration
count and wall-clock engineering time spent per condition during development; freeze all condition
implementations before Phase 2 begins (no prompt edits to any condition once evaluation starts);
ideally have a different, disinterested lab member own condition 2's prompt.

### 1.6 Prior exposure / data leakage into the graph — **medium risk**

If the held-out evaluation tasks in Phase 2 were used (even partially) to seed Phase 1's crawl —
e.g., the curiosity-driven crawl visits pages that happen to be exactly what the eval tasks probe —
the graph condition gets test-set contamination that looks like "the map generalizes" but is
memorization of eval-adjacent structure. §5 Phase 1→2 split does not state a firewall. **Control:**
partition the site's task universe into crawl-seed tasks and held-out eval tasks *before* Phase 1,
and never let the crawl agent or its curiosity objective see eval task text. The Environment Maps
paper's "trace-covered tasks" vs. "non-trace tasks" split (33.0% vs. 26.9% for the map condition) is
the right instinct — report both, with the honest read that most of the win could sit in the
trace-covered bucket.

### 1.7 Evaluator/verifier leakage — **medium risk**

If the same LLM (or a close relative) both acts as agent and validates task success (a common
WebArena-adjacent shortcut when programmatic validators are unavailable or supplemented by an
LLM judge), then any condition that produces more verbose or more "confident-sounding" trajectories
could be scored more favorably by a correlated judge, independent of real task success. §3.7 of the
foundations doc already names this generally ("Judge agreement... not a metric") but P4's own
condition list does not repeat the requirement. **Control:** programmatic validators only for the
primary metric (§4 P4 already requires "deterministic self-hosted... causal claims," which is the
right instinct); if an LLM judge is used anywhere, report human-judge agreement on an audited
subset per §3.7, and never let the acting model and the judging model share a checkpoint.

### 1.8 Prompt/harness differences beyond the tool API — **lower risk given §2's decisions**

§2.4 already fixes actor model, harness (Playwright/CDP), and action rung across the whole project,
which pre-empts a huge fraction of the classic "different agent, different framework" confound. The
residual risk is the *system prompt* — conditions 3/4/5/6 need extra instructions explaining how to
call graph tools, which is itself extra information the naive conditions don't get. **Control:**
keep the non-tool-related portion of the system prompt byte-identical across all six conditions;
diff and publish the prompts in an appendix.

### Ranking summary

1. Unequal tool-call/compute budget (1.1)
2. Free/unamortized exploration cost (1.3)
3. Token-length confound between conditions 2–5 (1.2)
4. Task-selection bias / non-stratified sampling (1.4)
5. Differential tuning effort on condition 2 (1.5)
6. Crawl-to-eval data leakage (1.6)
7. Evaluator/judge leakage (1.7)
8. Residual prompt asymmetry (1.8)

---

## 2. Is the condition list in §4 P4 complete and correct? (Q2)

**Condition 2 (naive + flat text memory of past trajectories) is the right instinct but
underspecified**, and the Environment Maps paper shows exactly why the underspecification matters:
its "raw trajectory access" condition let the agent `grep`/`Read` Playwright trace *files*
(hundreds of files per task, screencast frames, network events — "a format not designed for LLM
consumption," their own words) rather than a clean flat-text log of prior actions. That is a weak
strawman version of condition 2. A skeptical reviewer will ask: *is condition 2 the best plausible
non-graph competitor, or the easiest one to beat?* Concretely, condition 2 needs a specification
that says: same trajectories the graph is built from, same token budget, formatted as clean
step-by-step text (not raw traces), with retrieval (top-k similar past trajectories by embedding
or BM25) rather than the whole history dumped in-context if the token budget doesn't allow it.

**What a skeptical reviewer would additionally demand, roughly in order of how obvious the gap is:**

1. **A retrieval-only-no-structure condition**, distinct from "flat memory of past trajectories."
   Condition 2 as written conflates "no graph" with "no retrieval at all" (dump everything) or
   "naive retrieval" (top-k nearest trajectory). These are different competitors with different
   expected performance, and the graph's claimed advantage over "flat text memory" could shrink or
   vanish against a properly-tuned dense/BM25 retrieval baseline over the same trajectory corpus —
   this is precisely the RAGSearch finding (§8 below): dense retrieval "remains a practical and
   competitive alternative" once paired with a well-designed agentic search loop, and the
   graph-vs-flat gap narrows substantially outside multi-hop-style tasks. **Recommend adding this
   as condition 2a**, separate from condition 2's "dump the trajectories" reading.

2. **A random-walk-graph condition** (structure without the accretion signal — a graph built from
   an equal-cost *undirected/random* crawl rather than the curiosity-gated or task-accreted one).
   This isolates "does the *shape* of exploration matter" from "does having any graph at all
   matter." Without it, a positive result for condition 4 over condition 2 could be entirely a
   crawl-budget effect (more site coverage, any structure) rather than evidence the *graph
   representation itself* (as opposed to more trajectories) is doing the work. This directly
   answers a question the Environment Maps paper leaves open in its own limitations: "future work
   should investigate the threshold at which structured maps become strictly superior to raw
   traces" — that threshold is exactly what a random-walk-graph control would locate.

3. **A same-token-budget-of-raw-trajectories condition**, i.e., condition 2 capped to precisely the
   token count the graph occupies (not "all trajectories," a token-matched subset chosen by
   recency, by relevance-to-task, or randomly — report all three subset-selection policies since
   they will disagree). This is the true apples-to-apples test of "is structuring the same
   information worth anything," separate from condition 5 (shuffled-graph, which token-matches but
   destroys semantics). Condition 2 + condition 5 together bracket the space; the token-matched raw
   condition fills the missing middle cell (real information, no structure, matched tokens).

4. **A condition that is only in the doc implicitly and should be explicit: "graph, but time-boxed
   to the same construction budget as no graph"** — i.e., what does the graph condition look like
   if exploration is capped at, say, one hour of crawl time instead of "however long it takes to
   converge"? Without this, the crossover-point plot in the amortization section (§3 below) has
   only one x-value per graph condition (the one they happened to build), when the actually
   informative result is the curve *across* exploration budgets.

**Verdict:** the six-condition list is the right skeleton (baseline / real competitor / two graph
variants / token-matched-null / oracle-ceiling), but condition 2 as literally written ("flat text
memory of past trajectories") is ambiguous between three different real competitors (dump-all,
naive top-k retrieval, and the raw-trace grep-based access actually tested in the closest prior
work), and the list is missing the random-walk-graph and token-matched-raw-subset cells that
together are needed to attribute a win specifically to *graph structure* rather than to *more
site coverage* or *more tokens*.

---

## 3. Amortization methodology (Q3)

**Does anyone actually do this?** Partially, and inconsistently.

- **Environment Maps** (arXiv:2603.23610) is the best example found of even *reporting* the
  number: "constructing maps for the five WebArena environments used between 19 (Reddit) and 45
  (E-Commerce) trajectories at a cost of approximately $1 to $4 and around 13 to 31 minutes per
  environment. Applying these maps to 812 evaluation tasks yielded 114 additional successes." That
  last sentence is one hop away from an amortized cost-per-marginal-success figure ($1–4 / ~23
  additional successes per site ≈ pennies per success once amortized over 812 tasks) but the paper
  does not compute or plot it — no crossover-point graph, no cost curve vs. number of tasks
  executed on the site. It is closer to free-exploration-with-a-caveat than to a rigorous
  amortization result.
- **RAGSearch** (arXiv:2604.09666, "Do We Still Need GraphRAG?") is the most self-aware source
  found on this exact question. It explicitly reports offline construction cost as a separate table
  (construction time per 1M tokens, dollar cost per 1M tokens, retrieval time, context length) and
  states outright: *"Given the substantial offline construction and latency overhead associated
  with GraphRAG..., dense RAG — especially when paired with well-designed agentic workflows —
  remains a practical and competitive alternative for general QA scenarios,"* while conceding
  *"GraphRAG remains advantageous... when its offline cost is amortized"* over enough queries. This
  is the clearest published statement that amortization is query-volume-dependent and that whether
  it "pays off" is a threshold question, not a single verdict — which is exactly the crossover-point
  framing §4 P4 already proposes. It still does not produce the curve itself; it produces the two
  ends (per-query cost, per-corpus construction cost) and leaves the reader to do the division.
- **AWM (Agent Workflow Memory)** (arXiv:2409.07429): checked specifically for cost/amortization
  discussion. Its abstract and readily-fetched material report relative success-rate gains
  (+24.6% Mind2Web, +51.1% WebArena) with no visible accounting of the cost of workflow induction
  or a cost-matched comparison to baselines — i.e., this looks like a "quietly free exploration"
  case, though a full read of the PDF body (not obtained here — text extraction failed, see below)
  might contain a cost appendix. **`[could not verify beyond abstract/metadata — PDF body did not
  extract as text via WebFetch; worth a follow-up direct read]`.**
- General pattern across the memory-for-agents literature surveyed for Q8 (Infini Memory,
  MemGraphRAG, SAGE, GroupMemBench, EvoMemBench): all report accuracy-only headline numbers; only
  RAGSearch among those fetched reports a cost table at all, and none plot success vs. cumulative
  cost with an explicit crossover point.

**Conclusion for the deliverable:** *the amortization crossover-point plot §4 P4 and §5 Phase 2
already call for is, as far as this search found, not standard practice in this literature.* The
closest analogues (Environment Maps, RAGSearch) report the two cost components without combining
them into the curve. This is worth stating as a real, if modest, methodological contribution in the
paper this project produces — but it also means there is no existing template to copy; the
accounting rules have to be specified from scratch. Proposed rules:

1. **What counts as cost, denominated in one common unit (recommend: USD at a stated inference
   rate card, with token/step/wall-clock reported alongside, never substituted for it — see Q4).**
   - Crawl/exploration compute: every LLM call made during Phase 1 (including failed/aborted
     branches, and calls made by any irreversibility classifier or curiosity/surprisal scorer),
     at the same $/token rate as the acting policy.
   - Graph construction/maintenance compute: any offline processing (dedup, canonicalization,
     type-layer induction) after the crawl, including human-in-the-loop labeling time costed at a
     stated hourly rate if any curation step is manual.
   - Per-episode execution cost: identical across conditions — every condition's own LLM calls
     during the eval task itself, tool calls included (this is where confound 1.1 above must be
     controlled, or the cost accounting is exactly where the confound resurfaces as "the graph
     condition costs less per task but only because we let it call fewer expensive tools").
   - Storage/retrieval infrastructure cost is out of scope unless it materially differs (e.g., a
     vector DB vs. plain files) — state this exclusion explicitly rather than silently.
2. **How to plot success vs. cumulative cost.** X-axis: cumulative $ spent *on that site*, starting
   from $0 (no graph, no crawl) and increasing along two paths — (a) the naive/no-memory condition,
   whose cumulative cost is just N tasks × per-task inference cost, flat marginal cost, and (b) the
   graph condition, whose cumulative cost starts with a fixed one-time crawl/construction cost
   (a vertical jump at task 0) then increases at the graph condition's own (hopefully lower)
   per-task marginal cost. Y-axis: cumulative successes (or success rate over the tasks run so far,
   with a CI band — see Q5). Both curves on one plot per site per task-archetype stratum (§1.5).
3. **Defining the crossover point rigorously.** The crossover point is the smallest N such that
   `construction_cost + N × marginal_cost_graph < N × marginal_cost_naive` **and**, separately and
   not implied by the first, the smallest N at which the success-rate curves' confidence intervals
   stop overlapping (i.e., the performance gain is statistically resolved, not just cost-favorable).
   Report both N's — they can differ, and a paper that only reports the cost-crossover while the
   performance difference is still statistically indistinguishable at that N is overclaiming.
   If construction cost is never recouped within the largest N tested (e.g., a site only ever gets
   50 tasks run against it), say so as a first-class result, not a limitation buried in future work
   — this is itself the archetype-dependent finding §1.5 anticipates (repeat/routine tasks amortize;
   one-off transactional tasks may never cross over).

---

## 4. Cost-matched comparison methodology (Q4)

The clearest transferable methodology is the **iso-FLOP / compute-matched comparison** from the
LLM test-time-compute scaling literature:

**Snell et al., "Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model
Parameters"** (arXiv:2408.03314). Retrieved detail: the paper "conducts a FLOPs-matched comparison
between a smaller model with additional test-time compute and pretraining a 14x larger model,"
finding that "in a FLOPs-matched evaluation, on problems where a smaller base model attains
somewhat non-trivial success rates, test-time compute can be used to outperform a 14x larger
model," while "on challenging questions or under higher inference loads, pretraining is likely more
effective." The transferable pattern for this project: **hold total compute (or $) fixed and ask
which condition gets more success per unit of that fixed budget, rather than fixing task count and
reporting whichever condition happens to spend less** — i.e., invert the usual axis. Concretely
for P4: instead of (or in addition to) "success at equal total cost" as one number, sweep a compute
budget B and report `success(condition | budget ≤ B)` as B varies, mirroring the "compute-optimal
scaling curve adaptively allocated per prompt" idea in that paper (their reported >4x efficiency
gain over best-of-N came specifically from *adaptive* allocation, not a fixed recipe — the graph
condition's macro-with-fallback design in §4 P2 is structurally the same idea: spend little when
confident, more when uncertain, and the comparison should credit that adaptivity rather than
average it away).

**How to combine tokens, steps, wall-clock, and dollars:** recommend **report separately, never
collapse into one scalar for the primary result**, for the same reason §3.7 of the foundations doc
already distrusts single-bar-chart summaries. Rationale: tokens and dollars are highly correlated
(same rate card) so combining them is mostly redundant; wall-clock and steps diverge from both
whenever code-as-action or macro execution batches multiple browser actions per LLM call — which is
exactly the layer-5 macro mode this project is testing (§2.1's "5–10x step reduction... where the
5-10x step reduction lives," §4 P2). If macro mode wins on wall-clock and steps but not on tokens
(because the macro plans use a bigger, pricier scoring pass), or wins on dollars but not on
wall-clock (many cheap sequential tool calls), that dissociation is itself a finding a single
composite metric would erase. **Recommended reporting table columns per condition, per task, per
seed:** LLM calls, input tokens, output tokens, tool calls, wall-clock seconds, USD at a stated rate
card — with the primary success-vs-cost plot (Q3) built on USD as the x-axis (it is the only unit
that meaningfully sums across a heterogeneous mix of scorer calls, actor calls, and tool
executions) but every other column reported in an appendix table so a reader can recompute the
plot on their preferred axis.

**`[could not verify]`**: a search specifically for agent-domain (as opposed to reasoning-benchmark)
iso-cost/iso-FLOP comparisons (e.g., "HELM agent," a dedicated cost-controlled leaderboard for
WebArena-style tasks) did not complete — the session's web search budget was exhausted before this
query ran. Worth a follow-up search for: `cost-controlled evaluation LLM agents dollars per task
Pareto frontier accuracy vs cost agent benchmark`.

---

## 5. Statistics (Q5)

**Correct test for the core paired comparison.** For two conditions on the same tasks (e.g.,
condition 4 vs. condition 2), **McNemar's test** is the right default: it "compares the number of
discordant pairs in the two sets of pairwise outcomes by creating a 2×2 contingency table" and
tests "the null hypothesis that the two classifiers have identical marginal distributions,
focusing on discordant outcomes where the two methods disagree" — appropriate because it "does not
assume independent samples," which per-task paired outcomes are not
(sources: [MachineLearningMastery](https://machinelearningmastery.com/mcnemars-test-for-machine-learning/),
[jameshoward.us](https://jameshoward.us/2024/12/17/mcnemars-test-the-hidden-gem-for-paired-binary-data)).
For >2 conditions simultaneously (this project has 6 arms), McNemar generalizes to **Cochran's Q
test** across all conditions on the same tasks, followed by pairwise McNemar with correction (below)
for the specific contrasts that matter (condition 4 vs. 2 is the headline; the rest are secondary).

**Paired non-parametric bootstrap** is the standard complement/alternative in NLP practice: "compute
95% bootstrap confidence intervals with 10,000 resamples, resampling case-level indices in lockstep
across methods to preserve per-instance pairing," and mark significance "at α=0.05 when zero is not
contained in the 95% confidence interval." This is preferable to McNemar alone when you also want a
continuous effect-size CI (e.g., for the crossover-point analysis in Q3) rather than just a binary
reject/fail-to-reject.

**Mixed-effects logistic regression with a task random intercept** is appropriate once you want to
(a) pool across seeds and (b) explicitly separate "condition effect" from "which tasks happen to be
easy," which matters a great deal here because of a specific finding from the **Deployment Decision
Reliability** paper (found via `pith.science/paper/2608.11323`, applying generalizability theory to
agent leaderboards across TheAgentCompany, τ²-bench, and AppWorld): *"the agent main effect accounts
for less than 3% of total variance"* while *"the agent-by-task interaction accounts for 7–23%,"*
and *"reliability substantially deteriorates on harder tasks (aggregate reliability dropped from
0.752 to 0.000)."* Translated to this project: **most of the variance in a WebArena-style agent
comparison is task-to-task variance and condition-by-task interaction, not a stable condition main
effect** — which is precisely the argument for (i) paired-per-task analysis over aggregate deltas
(already specified in §4 P4 — good), and (ii) a random-intercept-for-task model rather than a naive
pooled proportion test, because the naive test's effective sample size is inflated by treating
correlated per-task outcomes as independent. Worked pattern for (ii), cited from a related
multi-agent-pipeline evaluation: "a mixed-effects model with task as random intercept yielded
virtually identical coefficients to OLS" in a case where task-level variance was near zero — the
useful takeaway is that fitting the mixed model and *checking whether it collapses to the simpler
one* is itself diagnostic; do not skip straight to the simple test and assume independence holds.

**Multiple-comparison correction across 6 arms.** With C(6,2)=15 possible pairwise contrasts but a
pre-registered primary contrast (condition 4 vs. condition 2, per P4's own framing — "this is what
must be beaten"), the cleanest design is: **one primary, pre-registered, uncorrected test (4 vs.
2)**, plus **Benjamini–Hochberg FDR control** across the remaining secondary pairwise contrasts —
recommended explicitly in the retrieved "Practical Playbook for Defensible Results"
(arXiv:2605.00428): *"Use Benjamini-Hochberg False Discovery Rate control rather than family-wise
error rate methods when conducting multiple comparisons across several conditions"* — because
family-wise (Bonferroni-style) correction over 15 contrasts would be needlessly conservative for an
exploratory secondary analysis, while still controlling the false-discovery problem a 6-arm design
otherwise invites. **Never let condition 2 vs. 4 be selected post hoc from among the 15 possible
pairs after seeing which one looks best** — the pre-registration is the actual control here, not
the correction formula.

**Multiple seeds per task.** Nest seeds within task within condition in the mixed model (task and
task×seed as random effects, or a task random intercept with seed-level residual variance) rather
than treating each seed as an independent additional task — otherwise N is inflated exactly as
described above.

**Sample size for 80% power on a 10pp absolute difference.** Retrieved concrete anchors rather than
a single number, because the required N is sensitive to the *discordant-pair* rate, which is
unknown until you have pilot data: Stata's paired-proportions power documentation example needs
"162 respondents... to detect a difference of 0.0880 between discordant proportions of 0.037 and
0.125 with 80% power" at a two-sided 5% level, and a different worked example needs "82 subjects...
to detect a change from proportion 0.53 to 0.4293 (a difference of 0.1007) with 80% power"
([Stata power–pairedproportions](https://www.stata.com/manuals/pss-2powerpairedproportions.pdf)),
while a cross-over-trial example with "20% of cases shift from positive to negative and 10% shift
from negative to positive" needs a minimum total sample size of 234
([MeasuringU](https://measuringu.com/sample-sizes-for-the-mcnemar-test/)). **Recommendation for
this project:** run Phase 0's ~50-task calibration pilot first (already planned), use its observed
per-task success rates for conditions 1 and 2 to estimate the discordant-pair proportions, then
compute the McNemar-exact sample size with a tool such as the `pwrss` R package's
`power.exact.mcnemar` / `proportions.mcnemar`
([rdrr.io/cran/pwrss](https://rdrr.io/cran/pwrss/man/proportions.mcnemar.html)) or MedCalc's
[McNemar sample-size calculator](https://www.medcalc.org/en/manual/sample-size-mcnemar-test.php).
As a planning-stage placeholder before that pilot exists: **for a base success rate in the
20–60% band (which §3.7 of the foundations doc already flags as the noisy regime, ±13pp CI at
n≈50) and a 10pp absolute target difference, expect the required N to be in the 150–300 paired-task
range**, not the ≥50 tasks/condition floor P4 currently states — 50 is very likely underpowered for
a 10pp effect given the retrieved worked examples above, and should be treated as a floor for
*detecting anything at all* (a much larger true effect), not as the number that supports an 80%-power
claim at 10pp. State this explicitly rather than silently keeping "≥50" as if it were power-justified.

---

## 6. Reproducibility (Q6)

**What must be logged/pinned, and evidence that the field currently fails at exactly this.** The
most directly useful source found is a pilot audit of twelve LLM-agent benchmark papers against a
five-field disclosure schema (arXiv:2605.21404, fetched and read as PDF): *benchmark identity*
(benchmark + version + subset + grader version), *harness specification* (scaffold name/version or
commit, verbatim system prompt, tool inventory, stopping rule, and — critically — **a
content-addressed container image**, not just a repo tag), *inference settings* (model, engine,
sampling config, seed or an explicit acknowledgment that no seed is exposed, run date), *cost
reporting* (input/output tokens, tool calls, wall-clock, USD), and *failure breakdown* (a
structured taxonomy of why each task failed, per-category counts, attributed to task/class). Their
headline numbers: *"the mean audit score across the eight agent-benchmark papers is 0.38 (out of
1.0)... the largest gap is on cost (none of the eight agent benchmark papers disclose cost in any
form) and on harness specification (none of the eight disclose a content-addressed container image
of the evaluation environment)."* Also load-bearing: *"across the eight agent benchmark papers we
scored, zero used [container] digests; several used repository tags; many used neither"* — i.e.
even papers that mention Docker do not pin the actual bytes that ran. This is a direct, sourced
warning for this project: **pin container images by digest (`sha256:...`), not by tag**, log the
exact commit hash of the harness (not just "Playwright"/"BrowserGym" by name), log the run date
(closed-API model aliases silently re-point over time), and treat "greedy decoding" alone as
insufficient disclosure of inference settings — the audit paper explicitly rejects that as
under-specified because it doesn't pin the inference engine or per-task token cap, both of which
change trajectories.

**Concrete pin list for this project, synthesized from the above plus §4 P4's own stated
requirements ("full trajectory replay"):**
- Model: provider, exact model string/version, and run date (not just "used at time of writing").
- Inference: engine (if self-hosted: vLLM/TGI/llama.cpp — these "handle stop sequences, KV caching,
  and batch determinism differently" per the audit paper), temperature/sampling params, seed (or an
  explicit statement that the API exposes none), per-task token cap, aggregation rule if any
  best-of-n or majority-vote is used anywhere (P3's separate open-weights scorer is exactly the kind
  of detail this schema wants named).
- Harness: scaffold name + version/commit, full verbatim system prompt (hashed if too long to
  print), tool inventory, stopping rule (max steps/tokens/wall-clock — already specified in §2.4/§5),
  environment container digest.
- Environment: WebArena instance snapshot/version, any seed data reset procedure between tasks.
- Cost: full table per Q4 above — this project should not repeat the "none of eight papers
  disclosed cost" failure mode; it is cheap to fix and directly serves the paper's own thesis.
- Failure taxonomy: per-task, per-condition failure category (grounding error, wrong-page
  navigation, tool-call error, verifier disagreement, timeout) — this both satisfies the audit
  schema and feeds the "verification: side effects, not just final answers" requirement already in
  §4 P4.

**A benchmark that already does the reproducible-environment half well:** **WebArena Verified**
(fetched via search, `openreview.net/pdf?id=CSIo4D7xBG`) — "audited variants... are preferable when
available because they retain the reproducible WebArena environment while repairing evaluator and
instruction artifacts," reports Wilson 95% CIs for success rates and t-intervals for step/tool-call
counts, and produces a 258-task "Hard" subset that preserves rankings at 68.2% lower evaluation
cost. Recommend building on WebArena Verified rather than raw WebArena for exactly the reasons §3.2
of the foundations doc already gives it primacy, and citing its evaluator-artifact repair work
directly (audited task set) rather than re-discovering the same broken tasks.

---

## 7. The negative-result plan (Q7)

**If the graph does not help, the publishable finding is the crossover-point-never-reached result,
stratified by task archetype** — i.e., "graph memory amortizes for repeat/routine and
configuration-style tasks within N≈[X] repetitions, but does not amortize for transactional tasks
within any budget tested, and the type-layer transfer claim (Phase 3) does not survive a shuffled
control." This is informative rather than a failure *only if* the negative result is produced by a
design that could have shown a positive result and didn't — which requires (a) the amortization
curve (Q3) run to a budget large enough that a true effect would have crossed over, (b) the
condition-2 baseline built to the standard in Q2 (a strawman condition 2 makes any null result
uninformative — you don't know if the graph failed or the baseline was too weak to lose to), and
(c) the calibration gate (§5 Phase 0, "if nothing separates, redesign before building anything
else") passed first, so a null in Phase 2 isn't just inherited noise from an uncalibrated
uncertainty signal. The Environment Maps paper's own most useful negative result — multi-site tasks
stuck at 0/48 across *every* condition including baseline — is exactly this shape: a cleanly
reported null that rules out "per-site representations help with cross-site workflows" rather than
being buried as a footnote. This project's own multi-site/Phase-3 transfer claim ("does the type
layer learned on shopping-clone-A help on shopping-clone-B") is the single most likely place for
exactly this kind of honest null, and §5 already frames it as "the claim with the longest legs" —
meaning it is also the easiest one to quietly under-report if it comes back negative. Pre-register
the transfer experiment's success criterion now, before Phase 1 results are known.

**Smallest experiment that would falsify the core hypothesis fastest (kill it cheaply before
building infrastructure):** run **Phase 0 exactly as specified** (the AUROC-of-surprisal-vs-failure
calibration gate) but extend it minimally to also test **condition 2's cheapest form** — a flat
list of the last N successful action sequences for structurally similar tasks, retrieved by naive
embedding similarity, injected into context, no graph, no crawl — against condition 1, on the same
~50-task pilot, before any crawl/graph infrastructure is built. If flat retrieval of raw
trajectories already captures most of the gain a graph would later claim (this is plausible: the
Environment Maps result shows raw trajectory access alone got 23.3% against the map's 28.2% — a
9.1pp graph benefit but a much larger 9.1pp-out-of-14pp share already captured by flat access), the
marginal value of building the full type/instance graph, the tool API (P2), and the uncertainty
gating (P3) may not be worth the engineering cost this project is about to commit to. This is the
single cheapest test that could kill the project's central bet before Phase 1's crawl
infrastructure exists at all, and it reuses Phase 0's own harness and task set — effectively free
given what's already planned.

---

## 8. Prior claims to check (Q8)

**Claims that structured/graph memory beats flat retrieval:**
- **Environment Maps** (arXiv:2603.23610): map 28.2% vs. raw-trajectory-access 23.3% vs. no-memory
  14.2% on 812 WebArena tasks — a positive result for structure over flat trajectory access, but
  confounded by unequal tool-call budgets (§1.1) and not amortized (§3).
- **Infini Memory** (arXiv:2606.10677, read in full as PDF): on MemoryAgentBench, the structured
  topic-document agentic reader (Infini Memory-A) scores **64.7% overall**, beating the strongest
  prior baseline in their table — **HippoRAG-v2, itself a graph-based method, at 45.5%** — by
  19.2 points, and beating flatter baselines (RAPTOR 29.8, MemGPT 31.2, Mem0 25.0) by a wider
  margin still. Their own ablation: disabling structural maintenance (no split/merge, "flat"
  append-only) while holding the retrieval path fixed drops accuracy on LongMemEval(S*) from
  76.0% to 69.3% — a **6.7-point structure-specific ablation**, and single-shot summary-only
  retrieval (no agentic multi-step search) reaches only 41.7% vs. 79.3% for the full agentic
  reader — the paper's own claim that "structural maintenance contributes more than the retrieval
  upgrade, and neither component is sufficient on its own" is directly supported by this ablation
  table, not just asserted.
- **RAGSearch / "Do We Still Need GraphRAG?"** (arXiv:2604.09666, read via WebFetch): GraphRAG
  "substantially outperforms dense retrieval on multi-hop QA" (+27.23 average), a strong positive
  result, but *specifically on multi-hop reasoning tasks*.

**Claims that found no benefit, or a benefit that disappears under scrutiny:**
- **RAGSearch**, same paper: *"dense RAG achieves competitive performance on general QA benchmarks,
  and GraphRAG yields only marginal improvements in this setting, with an average gain of +0.47"*
  — i.e. the graph advantage is task-type-dependent and near-zero on single-hop/general QA. Also:
  *"agentic search substantially improves dense RAG and narrows the performance gap to GraphRAG"*
  — meaning a better-designed flat-RAG agent loop erodes much of graph memory's apparent edge, and
  under an RL-trained setting, **the graph-based Graph-R1 scored *worse* than the flat Search-R1**
  on NQ (46.71 vs. 48.72, a −2.01 regression), with GraphRAG additionally showing *higher variance*
  (53.71±0.18 vs. 34.82±0.95 on HotpotQA reported the other direction — note the source variance
  figures are inconsistently signed across the two systems in the fetched summary; treat the
  direction of the variance comparison as `[could not verify without the source table]` while the
  accuracy regression number itself is quoted directly from the fetched text).
- **Infini Memory's own related-work framing** of a documented failure mode in this space: prior
  memory-as-isolated-fragments systems ("vector similarity, keyword matching, or a fixed top-k
  procedure... may return isolated fragments rather than enough evidence for temporally grounded
  reasoning") is presented as a known, citeable weakness of naive retrieval, i.e. the field's own
  consensus is that unstructured retrieval underperforms on multi-hop/temporal tasks specifically —
  consistent with, not contradicting, the RAGSearch task-type-dependent finding above.
- **Agent Workflow Memory** (arXiv:2409.07429): reports large positive deltas (+24.6% relative on
  Mind2Web, +51.1% relative on WebArena) for induced-workflow memory over a no-memory baseline, but
  — as flagged in Q3 — no visible cost/amortization accounting was found in the fetched
  abstract/metadata, so this is a positive-result data point whose **causal cleanliness under this
  project's own P4 standard could not be verified** without a full-text read of the PDF body
  (extraction failed via WebFetch for this paper specifically — flagged for a follow-up direct
  fetch or local PDF read, not asserted as either supporting or undermining the claim).

**Honest summary for the deliverable:** the graph/structure-vs-flat-retrieval question is **not a
settled yes** in the literature surveyed — it resolves in favor of structure specifically on
multi-hop, temporally-extended, or cross-reference-heavy tasks (RAGSearch's multi-hop QA numbers,
Infini Memory's ablation), and is marginal-to-negative on general/single-hop tasks and under
RL-trained retrieval policies (RAGSearch's NQ numbers, Graph-R1 regression). Given that this
project's WebArena/computer-use setting plausibly sits closer to the multi-hop/long-horizon end of
that spectrum (per §1.5's archetypes — "authoring/configuration... most graph-shaped of all"), this
is grounds for cautious optimism about P4's core bet, **conditional on the confounds in §1 actually
being controlled** — the Environment Maps result, the closest analogue found, shows a real but
modest (14pp) advantage for structure that shrinks to a smaller (5pp) advantage over an already-
memory-augmented flat baseline, under an uncontrolled compute-budget confound. A well-controlled
version of this experiment could plausibly land anywhere in the 0–15pp range on the condition-4-vs-2
contrast, not a clean multiple-of-baseline win.

---

## Corrections to docs/01-foundations.md

> "**Conditions** (same actor model, same harness, same rung): 1. Naive per-step agent, no memory.
> 2. Naive + flat text memory of past trajectories. *The real competitor...* 3. Graph agent,
> context mode. 4. Graph agent, macro mode with uncertainty-gated fallback. 5. Shuffled-graph
> control... 6. Oracle graph..." (§4 P4)

Correction: "same actor model, same harness, same rung" is necessary but not sufficient; it does not
pin **tool-call budget** or **token budget on tool returns**, and the one directly comparable prior
experiment found (Environment Maps, arXiv:2603.23610) shows an 12x tool-call disparity between its
map and flat-trajectory conditions in exactly this setup. Add "same tool-call budget, same token
budget on tool returns" to the list of things held fixed, and specify the token-matching rule for
conditions 2/2a as well as condition 5 (currently the doc only requires token-matching for the
shuffled control).

Correction: condition 2 needs a sub-specification. As written it is ambiguous between "dump all
past trajectories" and "retrieve top-k by similarity," and the one close prior-work analogue used a
third, weaker reading (grep over raw Playwright trace files). Recommend either splitting into 2
(retrieval-only, no structure, over a clean flat log) and 2a (token-matched raw dump), per §2
above, or at minimum stating explicitly which of these three condition 2 refers to.

> "**Budget accounting.** Report success at *equal total cost*, amortizing graph construction across
> the task set. An agent that received a free 500-step crawl is not comparable to one that did not.
> **The right plot is success (and cost/task) vs. number of tasks executed on that site; the
> crossover point where the graph pays for itself is the actual result**..." (§4 P4)

Correction: this is the right instinct, and per §3 above it appears to be genuinely underserved in
the literature (the two closest analogues, Environment Maps and RAGSearch, each report half of the
needed accounting but neither actually plots the crossover curve). The doc should say explicitly
*what counts as cost* (this section currently doesn't define the unit or what's included/excluded —
see the accounting rules proposed in §3 of this document) and should define the crossover point on
**two axes simultaneously** — cost-crossover and statistical-significance-crossover — since these
can differ and reporting only the cheaper one overclaims.

> "**Stats:** ≥50 tasks/condition, ≥3 seeds, CIs, paired per-task comparisons rather than aggregate
> deltas." (§4 P4)

Correction: ≥50 tasks/condition is very likely underpowered for detecting the kind of 10pp effect
this project's own §0 motivating question implies mattering (and is in the noisy 20–60% band §3.7
already flags, ±13pp CI at n≈50 per the doc's own arithmetic). Per the worked sample-size examples
in §5 above, plan for a power calculation off the Phase 0 pilot's observed discordant-pair rate
rather than treating 50 as power-justified; expect the true requirement to be in the 150–300 range
for a 10pp target. Also missing: a stated correction procedure for the 6-arm/15-contrast comparison
space (recommend one pre-registered primary contrast, condition 4 vs. 2, plus Benjamini–Hochberg FDR
on the rest — see §5) and a stated model for pooling seeds (task random-intercept mixed model, not
naive pooling — seeds are not independent additional tasks).

---

## Design implications

A concrete, numbered analysis plan, incorporating the corrections above:

1. **Pre-register before Phase 1 starts:** the task archetype stratification (§1.5's five
   archetypes, minimum info-seeking vs. transactional split), the crawl/eval task firewall (§1.6),
   the primary statistical contrast (condition 4 vs. condition 2, per P4's own framing), and the
   Phase 3 transfer success criterion — all before any graph is built, hash-committed to the repo.
2. **Extend Phase 0** to include a cheap flat-retrieval condition 2 pilot (§7's falsification
   experiment) alongside the existing surprisal-calibration gate, on the same ~50-task pilot, before
   committing to building crawl/graph infrastructure.
3. **Specify condition 2 precisely** as either 2 (naive top-k retrieval over a clean flat log,
   token-budget-matched to the graph) and 2a (full token-matched raw dump), not "flat text memory"
   left ambiguous; add a random-walk-graph condition and a same-token-budget-raw-trajectories
   condition per §2, expanding six conditions to eight.
4. **Fix a hard tool-call and token-on-tool-return budget** shared identically across all eight
   conditions (§1.1, §1.2); log actual consumption per condition as a first-class output column,
   not an afterthought.
5. **Run the Phase 0 pilot, then compute McNemar-exact sample size** off its observed condition-1
   vs. condition-2 discordant-pair rate (via `pwrss::power.exact.mcnemar` or MedCalc's calculator)
   before fixing the Phase 2 task count; do not proceed with the ≥50/condition floor as if it were
   power-justified for a 10pp target.
6. **Primary analysis:** McNemar (or task-random-intercept mixed-effects logistic, checked against
   McNemar for consistency) on condition 4 vs. condition 2, uncorrected, pre-registered as primary;
   Cochran's Q across all eight conditions plus pairwise McNemar with Benjamini–Hochberg FDR control
   for all secondary contrasts; paired bootstrap CIs (10,000 resamples, case-level pairing
   preserved) reported alongside every point estimate.
7. **Report the amortization curve** per site per archetype stratum: cumulative USD cost (with
   token/step/wall-clock/tool-call counts in an appendix table, not collapsed into the primary
   metric) on the x-axis, cumulative success rate with CI band on the y-axis, for condition 2 and
   condition 4 at minimum; report both the cost-crossover N and the statistical-significance-
   crossover N, and state plainly if the site's task volume never reaches either.
8. **Report every archetype/subgroup unconditionally**, including nulls (per the Environment Maps
   0/48 multi-site precedent) — no averaging across archetypes in the headline number without also
   showing the per-archetype breakdown.
9. **Pin and disclose per Q6's five-field schema**: model+version+date, harness scaffold+commit+
   verbatim prompt+tool inventory+stopping rule, container digest (not tag), inference engine+
   sampling params+seed-or-explicit-absence, full cost table, structured failure taxonomy per task.
10. **Minimal falsification experiment (run first, cheapest):** the Phase-0-plus-condition-2-pilot
    described in point 2 / §7 — if flat retrieval already captures most of the no-memory-to-graph
    gap on the pilot's ~50 tasks, treat that as a strong prior against the marginal value of the
    full graph/tool-API/uncertainty-gating build, and require a specific, pre-stated reason
    (e.g., "the pilot's tasks are all single-hop/general, and P3's own literature suggests the
    graph's real edge is multi-hop/configuration-style") before proceeding to build Phase 1's crawl
    infrastructure anyway.

## Open questions

- Does the Agent Workflow Memory paper (arXiv:2409.07429) report any cost/amortization accounting
  in its full body? The abstract/metadata fetch here found none, but PDF text extraction failed;
  this needs a direct read (local PDF or HTML mirror) rather than the WebFetch summarizer used here.
- What is the actual sign/magnitude of the GraphRAG-vs-dense-RAG variance comparison on HotpotQA in
  RAGSearch (arXiv:2604.09666)? The fetched summary produced numbers that read inconsistently
  ("53.71±0.18 on HotpotQA vs 34.82±0.95 for Search-R1" attributed in a way that doesn't clearly
  match which system is which) — flagged in §8 as `[could not verify]`; needs a direct look at the
  paper's Table/Figure rather than a fetched summary.
- Is there a dedicated cost-controlled / iso-cost leaderboard specifically for WebArena-style agent
  tasks (analogous to HELM's cost reporting for LLMs, but for multi-step agents)? Not found within
  this session's search budget — flagged in §4 as a needed follow-up search.
- The Deployment Decision Reliability paper's variance-decomposition result (agent main effect <3%
  of variance, task interaction 7–23%) was drawn from TheAgentCompany/τ²-bench/AppWorld, not
  WebArena specifically — worth confirming the same variance pattern holds on WebArena before
  leaning on it too heavily for this project's specific power calculation.
- This session's WebSearch budget (200 calls, apparently shared across the parallel R0–R5 workers)
  was exhausted before several planned queries ran (iso-cost agent leaderboards, direct AWM
  full-text, additional reproducibility exemplars beyond WebArena Verified). If another worker's
  budget has headroom, or a follow-up pass is run later, prioritize the iso-cost-agent-leaderboard
  query first — it is the single biggest remaining gap in Q4.
