# Foundations: the computer-use problem, its layers, and a graph-memory experiment

**Status:** v0.1, frozen. Written before the literature-verification pass. **Superseded by
`docs/02-design-v0.2.md`.** Kept unchanged because the research dossiers quote its lines.
**Scope rule:** public, clean-room. No proprietary or employer-internal knowledge enters this
project. Claims should be grounded in publicly citable sources; unverified claims are marked
`[unverified]` and are the input to the research workers.

---

## 0. Why this document exists

We want to test one idea: **if an agent first explores a website and saves a graph representation
of it, does a later agent equipped with tools over that graph outperform a naive per-step agent —
and can uncertainty (perplexity/surprisal) be used both to drive the exploration and to measure
the benefit?**

Before that is testable, four things have to be pinned down, and one thing has to be pinned down
*before* those four. This document fixes the substrate (§2), gives the taxonomy and eval landscape
we are operating in (§1, §3), states the four technical problems (§4), and proposes the first
experiment (§5).

---

## 1. What "computer use" decomposes into

It is not one problem. Three orthogonal axes, plus five sub-problems that get conflated.

### 1.1 Axis A — observation (what the model sees)

- **Pixels.** Screenshot only. Maximally general (canvas apps, PDF viewers, remote desktops,
  native apps). Expensive per step. Requires visual grounding.
- **Text structure.** DOM or accessibility tree. Cheap and precise; brittle on custom widgets;
  raw trees are frequently 100k+ tokens, so pruning is mandatory and pruning is lossy.
- **Hybrid / set-of-marks.** Screenshot with numbered overlays on interactable elements. The model
  reasons visually, acts on a symbolic index. Currently the pragmatic default.
- **Programmatic.** Skip perception; drive an API/SDK/MCP server. Fastest and most reliable where
  available, but arguably not "computer use" at all.

### 1.2 Axis B — action space

See §2 for the full ladder. Summary of the families:

- **Low-level:** `click(x,y)`, `type`, `scroll`, `key`. Universal, long horizons, needs grounding.
- **Mid-level:** `click(element_id)`. Shorter horizons, needs a valid element index.
- **Code-as-action:** emit a Playwright/Python snippet per step. Efficiency win (loops, batching);
  harder to verify and to recover from.
- **Macro / replay:** execute a previously induced workflow open-loop. Cheapest, most brittle.
  **This is the family the graph idea lands in.**

### 1.3 Axis C — control loop

- Single-agent ReAct loop (observe → think → act). The baseline everyone reports.
- Planner/executor split; sometimes a third dedicated grounder model.
- Reflection / retry on failure (Reflexion lineage).
- **Search over states:** tree search / MCTS with backtracking; or *simulated* search using an LLM
  as a world model instead of executing (WebDreamer). `[verify: Koh et al. 2024 tree search on
  VisualWebArena; WebDreamer]`
- **Memory-augmented:** induce reusable workflows from past trajectories and inject them
  (Agent Workflow Memory; in-context experience replay; skill induction). **Nearest neighbour to
  this project — the delta we claim is graph structure + uncertainty gating.**
- **Trained:** SFT on trajectories, or RL with execution rewards (WebRL, DigiRL lineage).

### 1.4 The five sub-problems hiding inside all of it

1. **Grounding** — "the blue Submit button" → coordinates/element. Its own literature and
   benchmarks. Often the single largest error source in pixel agents.
2. **State estimation** — what page am I on, did the last action work, is this a modal or a
   navigation? Chronically under-modeled.
3. **Verification** — did the task actually complete, *including side effects*.
4. **Memory / transfer** — across steps, across episodes, across sites.
5. **Safety** — prompt injection from page content, irreversible actions, over-permissioned
   sessions.

### 1.5 Task archetypes

The graph pays off very differently per archetype. Naming them so we can scope.

- **Read-only information seeking** (find, compare, aggregate across pages). Navigation-heavy,
  exploration-heavy, cheap to retry. *Graph-friendly.*
- **Transactional** (form fill, book, purchase, CRUD in a SaaS admin). Short navigation, high
  precision, irreversible side effects. *Graph may not amortize.*
- **Long-horizon multi-app workflows** (email → spreadsheet → internal tool).
- **Authoring / configuration** (settings panels, deep menu trees). *Most graph-shaped of all.*
- **Repeat / routine execution** — same task, N times. *The regime where a site map should
  dominate, and the regime our amortization curve is about.*

---

## 2. Layer zero: the action-space ladder

This is the substrate choice. It is not part of the four problems — it sits underneath them,
because a graph edge *is* an action, and the rung decides how durable that edge is.

| # | Layer | The agent emits | Who executes it |
|---|---|---|---|
| 0 | OS input events | `click(842,316)`, `type("hi")`, `key(Enter)` | xdotool / pyautogui / CGEvent — real cursor moves |
| 1 | Browser input events | same coordinates via CDP `Input.dispatchMouseEvent` | Chrome, scoped to tab, no real cursor |
| 2 | Element-targeted | `click(element_id=42)` / `click("button:has-text('Submit')")` | Playwright/Selenium: hit-test → scroll → actionability check → synthesize real events |
| 3 | DOM/JS manipulation | `el.click()`, `el.value = "x"` | The page's own JS engine |
| 4 | Accessibility actions | `AXPress(node_17)` | Platform a11y API (macOS AX, Windows UIA, Android AccessibilityService) |
| 5 | Semantic / macro | `add_to_cart(sku)`, `login(user)` | Site-specific script expanding into layer-2 steps |
| 6 | Private network API | `POST /api/cart {sku}` with the page's cookies/CSRF | HTTP client — the "curl" rung |
| 7 | Public API / MCP | `create_issue(...)` | Documented, supported endpoint |

### 2.1 The governing tradeoff

**Monotone.** Going *down* buys generality (layer 0 works on anything with pixels) and costs
reliability and speed. Going *up* buys reliability and speed and costs generality — because every
rung above 0 requires a **binding** (a selector, a node id, an endpoint) that is app-specific and
can go stale.

**Grounding does not disappear as you climb; it changes shape.** At layer 0 it is "which pixel."
At layer 2, "which selector, and is it still valid after the refactor." At layer 6, "which
endpoint, and did the payload schema change." You choose which version of the problem to debug.

### 2.2 Three distinctions that resolve most confusion

1. **The agent's action space ≠ the executor's action space.** They are almost always different
   rungs, and the gap is the harness. An agent emitting `click(id=42)` still ultimately dispatches
   a mouse event. The real question is *where the line falls between what the model decides and
   what the harness resolves.* Line low → the model bears the grounding burden. Line high → the
   harness bears it, but the harness had to be written per site. **That per-site harness cost is
   exactly what the graph is supposed to amortize away.**

2. **Reads and writes belong at different rungs.** Reading is cheap and safe high up: capturing the
   JSON the page already fetched (layer 6, read-only) yields clean structured data with no parsing
   risk, and performs no request the page did not already perform. Writing is different — layers 3
   and 6 bypass client-side validation, CSRF flows, and multi-step state machines, so you end up
   reimplementing the frontend's logic and silently corrupting state when wrong.
   **Default: navigate and write at layer 2, read at layer 6.**

3. **The "curl" rung carries non-technical cost.** Forging requests to a private API means rotating
   auth/CSRF tokens, bot protection, drift on every redeploy, and possible terms-of-service
   conflict. It also breaks the premise of operating the interface a human operates, making results
   non-transferable. Right tool when you control the service or it is your own test environment;
   wrong tool as a general strategy.

### 2.3 You do not pick one rung — the options formalism

The right formalism is **options / semi-MDPs** from hierarchical RL: an option is
*(initiation set, policy, termination condition)*. That is exactly what a graph edge should be.

Execution is top-down with graceful degradation: try the macro, check the termination predicate,
and on failure drop one rung and let the base per-step agent take over. The graph does not replace
the low-level action space — it **caches successful policies over it**, and cache misses degrade
instead of failing.

```
task goal
  └─ graph lookup → option (layer 5 macro)          ← the research object
       └─ element-targeted steps (layer 2)          ← the agent's action space
            └─ synthesized input events (layer 1)   ← the harness's problem, not ours
```

### 2.4 Decision for this project

- **Agent action space: layer 2.** Element-targeted over an enumerated candidate list from a pruned
  accessibility tree: `click(id)`, `type(id, text)`, `select(id, option)`, `scroll(dir)`,
  `goto(url)`, `back()`, `stop(answer)`.
- **Executor: Playwright/CDP.** Real events, actionability checks, no JS injection for writes.
- **Reads may use layer 6** (the page's own XHR responses) — declared explicitly in the method
  section, and granted to the naive baseline too.
- **No layer-6 writes, no request forging.**
- **Graph edges are layer-5 options** over the layer-2 primitives, each with an explicit
  termination predicate so macro execution is *verified*, not hoped.
- **Layer 0 is future work.** Pixel generality is the right long-term target, but grounding error
  there is large enough to swamp the graph signal we are trying to measure.

**Consequence to state up front:** results will be a claim about *DOM-accessible web apps*, not
about computer use in general. Fine scope; must be declared, not discovered by a reviewer.

### 2.5 Why the substrate gates the four problems

- **P1:** edge durability is a function of the rung. Coordinate edges die on layout shift; selector
  edges die on CSS refactor; role+text edges are ambiguous with three "Next" buttons; endpoint
  edges are near-immortal and near-meaningless as UI claims. Fix the rung and "what is an edge"
  answers itself.
- **P3:** uncertainty over an **enumerable candidate set** (layer 2) is a clean categorical
  distribution with well-defined, step-comparable entropy. Uncertainty over **continuous
  coordinates** (layer 0) is not — you must discretize, and entropy becomes a grid-size artifact.
  *If the perplexity story is to be rigorous, layer 2 is close to mandatory.*
- **P4:** cost-per-step varies by roughly 50× across the ladder and is the denominator of the whole
  amortization argument. A graph agent and a naive agent on different rungs cannot be compared —
  that comparison measures the rung.

---

## 3. Evals and benchmarks

Grouped by what they measure. Pre-2025 entries are high-confidence; later ones are pointers to
verify. `[verify]` markers are the research workers' job.

### 3.1 Offline / action-matching
Predict the human's next action from a logged trajectory; no execution.
Mind2Web; WebLINX (conversational); AITW / Android-in-the-Wild; GUI-Odyssey.
*Cheap and reproducible, but measures imitation, not competence: many correct paths exist, so
step-accuracy under-credits good agents and over-credits mimics.*

### 3.2 Online, deterministic, self-hosted — **the only place causal claims can be made**
WebArena (Reddit/GitLab/shopping/CMS/maps clones); VisualWebArena; WebArena-Lite;
WorkArena / WorkArena++ (ServiceNow); TheAgentCompany (multi-app, checkpoint partial credit);
MiniWoB++ (toy but controllable); WebShop.
**Harness:** BrowserGym / AgentLab — adopt rather than write our own runner. `[verify]`

### 3.3 Online, live web — realistic, non-reproducible
WebVoyager (LLM-judge scored); Online-Mind2Web; AssistantBench; WebCanvas / Mind2Web-Live
(key-node scoring under drift); GAIA (general assistant, partially browsing).
*Drifts week to week. Generalization appendix only, never the primary metric.*

### 3.4 OS / desktop / mobile
OSWorld (+ OSWorld-Verified); WindowsAgentArena; AndroidWorld.

### 3.5 Component-level
Grounding: ScreenSpot, ScreenSpot-v2, ScreenSpot-Pro, VisualWebBench.
Judges/reward models: AgentRewardBench — do automatic judges agree with humans? Reportedly less
than one would like. `[verify]`

### 3.6 Safety / adversarial
AgentDojo; WASP (web prompt injection); ST-WebAgentBench (policy compliance); BrowserART.

### 3.7 Metric families and their pathologies

- **Success rate via programmatic validator** — gold standard, but validators are brittle and some
  WebArena tasks are reported unsolvable or mis-specified; audited subsets exist. `[verify]`
- **Key-node / checkpoint progress** — partial credit, survives drift, rewards trajectory-shape
  conformity.
- **Efficiency** — steps, tokens, wall-clock, $/task. Under-reported, and it is exactly what this
  experiment is about.
- **Judge agreement** — an LLM judge without reported human agreement on a subset is not a metric.
- **Variance** — success in the 20–60% band at n≈50 carries roughly ±13pp CIs. Most reported deltas
  in this field are noise. `[verify the arithmetic and state the exact interval used]`

---

## 4. The four technical problems

### P1 — State abstraction and graph construction

A website is a POMDP; we want to compress it into a graph that is small, predictive, and stable
under change.

**What is a node?** Candidates and their failure modes:
- *Canonical URL* — explodes on `/product/{id}`; misses state not in the URL (modal open, cart
  contents, auth state, applied filter).
- *DOM-skeleton hash* (structure minus content) — same page with different data hashes
  differently unless text is stripped; strip too aggressively and distinct pages collide.
- *Screenshot embedding cluster* — robust to markup changes, opaque and threshold-sensitive.
- *LLM-generated semantic label* — stable and small, non-deterministic and uncheckable.

**Recommendation: a two-layer graph.** A *type layer* (abstract: "product listing, filtered";
"checkout step 2") over an *instance layer* (concrete URLs/states). The reusable, transferable,
compressible knowledge lives in the type layer; the instance layer is a cache. This is effectively
*learning the site's schema*, which tells us what to extract: entity types, page types, and the
affordance transitions between them.

**What is an edge?** `(source_state, affordance, action) → target_state`, where the affordance
carries a durable locator (text + role + structural path, never bare coordinates), plus: success
probability, observed cost, reversibility flag, preconditions (auth, cart non-empty),
`last_verified` timestamp, and a **termination predicate** (per §2.3).

**How to build it.** Budgeted BFS/DFS crawl (broad, task-agnostic, expensive, dangerous on
transactional edges) vs. accretion from task trajectories (cheap, task-biased, maps only what was
already needed). **Hybrid:** shallow crawl to seed landmarks, then accrete.

**Safety constraint:** an exploring agent must not click Delete or Purchase. An **irreversibility
classifier gating exploration** is a real sub-project, not a footnote.

**Prior art not to reinvent:** unsupervised-exploration-then-relabel work (NNetNav and similar);
Agent Workflow Memory; Go-Explore's archive-of-states (closest conceptual ancestor); skill
induction. `[verify all]`

### P2 — Making the graph usable inside a context window

A 5k-node graph cannot be pasted into a prompt. The graph is only useful through a **tool API**,
and designing that API *is* a contribution.

Minimum viable tool set:
- `search(goal_text) → candidate nodes` (semantic index over node summaries)
- `neighbors(node) → affordances`
- `path(from, to) → action sequence` (this is the macro)
- `landmarks() → hubs / entry points`
- `record(observation)` — the write path, so exploration compounds

**Central design fork:**
- *Context mode* — hints injected into the prompt; agent still acts per-step. Safe, small win.
- *Macro mode* — execute `path()` semi-open-loop. Where the 5–10× step reduction lives. Brittle.
- *Recommended middle* — execute the macro with a cheap per-step verifier and **fall back to naive
  exploration the moment verification fails or uncertainty spikes.** This is where P3 plugs in.

Also required: staleness/invalidation policy; per-edge confidence; and a **token budget on tool
returns** — a tool that dumps 8k tokens of subgraph has undone the point.

### P3 — Perplexity / uncertainty as control signal *and* as measurement

"Perplexity while exploring" can mean at least three different things with different properties.

**(a) Policy confidence.** Entropy or NLL over the *next action*. Make it a proper categorical
distribution by scoring over enumerated candidate elements rather than free-form text; free-text
perplexity is confounded by length and phrasing. *Use: a gate.* High entropy → consult the graph,
explore, or ask.

**(b) World-model surprisal.** NLL of the *actual next observation* (its summary/type label) under
a model conditioned on the graph vs. not conditioned. **This is the quantity that directly tests
the hypothesis:** does having the map reduce surprise about what is behind the link? Cleaner still:
**Bayesian surprise** = KL(posterior ‖ prior) over next-state predictions, which is less sensitive
to token-length artifacts than raw PPL.

**(c) Ensemble disagreement.** Sample k rollouts, measure spread. Needs no logprobs, works with any
closed API, and is often better calibrated than raw NLL.

**Three instrumentation points that decide whether this works at all:**

1. **Use a fixed open-weights scorer as the measuring instrument** (vLLM/llama.cpp with logprobs),
   separate from the acting policy. Otherwise the metric moves whenever the actor is swapped — and
   most frontier APIs do not expose logprobs anyway.
2. **The length confound is fatal if unhandled.** Conditioning on a graph adds tokens, and more
   context mechanically lowers perplexity. The **mandatory control is a shuffled/scrambled graph of
   identical token count.** Without it, any PPL reduction reported is uninterpretable.
3. **Validate calibration before building control logic on it.** *Experiment zero:* does surprisal
   predict step failure? Report AUROC of surprisal → next-step failure. If it is ~0.55, the signal
   cannot gate anything and we switch to (c) or to an explicitly trained verifier.

**The most novel-feeling use, if calibration holds:** surprisal as an **exploration reward**
(curiosity-driven crawl — the ICM/RND lineage applied to site exploration), giving a principled
**stopping rule**: stop crawling when marginal surprisal reduction per action falls below a
threshold. *"When is the map good enough" is a publishable result on its own,* independent of any
downstream task gain.

### P4 — Experimental design and causal attribution

The headline claim is "graph beats naive." The naive version of that experiment is confounded at
least four ways: the graph condition gets more context, more compute, prior site exposure, and a
different prompt.

**Conditions** (same actor model, same harness, same rung):
1. Naive per-step agent, no memory. *(the stated baseline)*
2. Naive + flat text memory of past trajectories. ***The real competitor — this is what must be
   beaten, not #1.***
3. Graph agent, context mode.
4. Graph agent, macro mode with uncertainty-gated fallback.
5. **Shuffled-graph control** — token-matched, semantically wrong. *(isolates information from
   token count)*
6. Oracle graph — hand-built, perfect. *(upper bound: is the ceiling worth chasing?)*

**Budget accounting.** Report success at *equal total cost*, amortizing graph construction across
the task set. An agent that received a free 500-step crawl is not comparable to one that did not.
**The right plot is success (and cost/task) vs. number of tasks executed on that site; the
crossover point where the graph pays for itself is the actual result** — a more honest and more
interesting claim than a single bar chart.

**Environment:** deterministic self-hosted for causal claims; live sites as a generalization
appendix only. **Stats:** ≥50 tasks/condition, ≥3 seeds, CIs, paired per-task comparisons rather
than aggregate deltas. **Verification:** side effects, not just final answers. **Logging:** full
trajectory replay.

---

## 5. First experiment

**Phase 0 — calibration gate (no graph).** Instrument a plain BrowserGym ReAct agent on ~50
WebArena tasks. Log per step: candidate-action distribution, action NLL, ensemble disagreement at
k=5, and step success. *Deliverable:* AUROC of each uncertainty signal against step failure.
**If nothing separates, redesign before building anything else.**

**Phase 1 — map building.** Budgeted curiosity-driven crawl of one WebArena site (e.g. the shopping
clone) with the irreversibility filter. *Deliverable:* the two-layer graph, plus a
surprisal-vs-crawl-budget curve showing saturation.

**Phase 2 — the comparison.** Conditions 1–6 on held-out tasks for that site. *Primary metric:*
success at matched cost. *Secondary:* steps/task, and the amortization crossover point.

**Phase 3 — transfer.** Does the type layer learned on shopping-clone-A help on shopping-clone-B?
The claim with the longest legs.

---

## 6. Open decisions

1. **Task archetype.** Information-seeking and configuration are graph-friendly; transactional
   tasks are short and the map may not amortize. Picking one sharpens everything downstream.
2. **Observation modality.** DOM/a11y tree (cheaper, faster iteration, logprob-friendly) vs. pixels
   (general, expensive, grounding error may swamp the graph signal). *Leaning DOM.*
3. **Context vs. macros** for the graph's output. Safe-and-small vs. big-win-and-brittle.
4. **Deliverable shape.** Paper-shaped result or working system? Decides whether the Phase 0
   calibration gate is a hard gate or a nice-to-have.

---

## 7. Research questions handed to workers

Each `[verify]` above, plus one dossier per section:
R0 substrate/action layers · R1 state abstraction & graph construction · R2 graph-as-memory &
retrieval · R3 uncertainty, perplexity & curiosity · R4 benchmarks & metrics ·
R5 experimental design & baselines.
