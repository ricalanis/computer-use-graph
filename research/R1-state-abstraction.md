# R1 — State Abstraction & Site-Graph Construction

**Worker:** R1. **Target:** `docs/01-foundations.md` §4 P1 ("State abstraction and graph construction").
**Method:** live web search + direct fetch of primary sources (arXiv/ACM/GitHub) in September 2026.
Every citation below was retrieved; anything I could not retrieve or verify is marked
`[could not verify]` with the search that failed. No employer-internal or proprietary system is
referenced.

---

## 1. Prior art: explicit graph/map representations for GUI/web agents

Verified as real, one by one, with node/edge/build/measurement summarized.

### 1.1 NNetNav (NNetscape Navigator)
[NNetNav: Unsupervised Learning of Browser Agents Through Environment Interaction in the Wild](https://arxiv.org/abs/2410.02907) (Murty et al., Stanford, Oct 2024).
- **Node:** *not a persistent graph node at all* — a state is the flattened DOM/accessibility tree of
  the current page, used only within one exploration episode.
- **Edge:** an action taken by a prompted-LLM exploration policy (`π_LM`), seeded with a random
  "persona" per episode to diversify behavior.
- **Build:** unsupervised interaction → retroactive relabeling. A trajectory summarizer (`Δ_LM`)
  describes what changed at each step; a labeler (`Lf_LM`) infers what instruction the sub-trajectory
  would satisfy; an outcome reward model filters trajectories whose behavior doesn't match the
  inferred instruction. This produces synthetic (instruction, trajectory) pairs for SFT — **no
  cross-episode map or graph is built or reused.** This is the single most load-bearing correction to
  §4 P1's citation of NNetNav as "prior art not to reinvent" for graph construction: NNetNav does not
  build a graph. It is exploration-then-relabel for **training data generation**, not for a persisted
  site model.
- **Measured on:** WebArena (Llama-3.1-8B: 16.3% vs. zero-shot GPT-4's 14.1%, vs. 1.0% untrained
  baseline), WebVoyager (35.2% vs. 33.5% zero-shot GPT-4), and MiniWoB++ (0.48 vs. 0.28 mean reward).

### 1.2 Agent Workflow Memory (AWM)
[Agent Workflow Memory](https://arxiv.org/abs/2409.07429) (Wang, Mao, Fried, Neubig, Sept 2024);
[code](https://github.com/zorazrw/agent-workflow-memory).
- **Node/edge:** none — AWM's unit is a **workflow**: an induced, reusable natural-language routine
  abstracted from one or more trajectories, injected as in-context guidance. It is a flat memory of
  procedures, not a graph of states.
- **Build:** induce workflows offline (from training trajectories) or online (from the agent's own
  successful test-time trajectories), then retrieve relevant workflows into the prompt.
- **Measured on:** Mind2Web and WebArena; +24.6% relative success on Mind2Web, +51.1% relative on
  WebArena, plus fewer steps to success. This is exactly the family §1.3 of the foundations doc
  calls "nearest neighbour" to the project — confirmed, and confirmed to be **memory of procedures,
  not a site graph.** The graph idea is a genuine structural delta over AWM, not a restatement of it.

### 1.3 Go-Explore
[Go-Explore: a New Approach for Hard-Exploration Problems](https://arxiv.org/abs/1901.10995)
(Ecoffet et al. 2019); Nature version ["First return, then explore"](https://arxiv.org/pdf/2004.12919);
extension [Intelligent Go-Explore](https://arxiv.org/abs/2405.15143) (ICLR 2025).
- **Node:** an entry in an **archive of previously-visited states** (in the original Atari work, a
  hand-designed low-dimensional state abstraction — e.g. a downsampled image cell); Intelligent
  Go-Explore replaces this with foundation-model similarity judgments so no hand-designed abstraction
  is needed.
- **Edge:** implicit — the policy trajectory taken from an archived state to a new one.
- **Build:** iteratively (1) select a promising archived state, (2) *return* to it deterministically
  (this requires a resettable simulator), (3) *explore* randomly/with a policy from there, (4) archive
  any newly reached state that is novel/interesting. Named failure modes it fixes: **detachment**
  (losing track of a frontier) and **derailment** (stochastic re-entry drifting off the intended
  state). This is the correct "closest conceptual ancestor" claim in §4 P1 — but it depends on a
  literal environment reset, which the live web does not offer (see §5 below; this is the crux of why
  graph-building on a real website is a harder problem than Go-Explore's).
- **Measured on:** Atari hard-exploration games (Montezuma's Revenge, Pitfall) — **not web/GUI** at
  all in the original work. It is imported into this project by analogy, not by transfer of results.

### 1.4 LASER
[LASER: LLM Agent with State-Space Exploration for Web Navigation](https://arxiv.org/abs/2309.08172)
(Ma et al., Tencent AI Lab, Sept 2023).
- **Node:** a small, **hand-authored, task-specific set of abstract states** (e.g., "search page,"
  "results page," "item page") the designer defines in advance for a given site/task family.
- **Edge:** state-specific action sets, explicitly including a "backtrack" action, so the agent can
  recover from an error instead of only moving forward — this is presented as the core fix over prior
  agents that assumed forward-only trajectories.
- **Build:** *not learned* — the state space is manually specified per domain (WebShop, amazon.com).
  This is important context for the "type layer" question in §3: LASER shows the *value* of having
  named abstract states (it improves recovery and performance), but it is evidence that the design was
  hand-engineered, not evidence that page-type induction has been solved.
- **Measured on:** WebShop and live amazon.com; reported to close the gap to human performance on
  WebShop.

### 1.5 Explorer
[Explorer: Scaling Exploration-driven Web Trajectory Synthesis for Multimodal Web Agents](https://arxiv.org/abs/2502.11357)
(Pahuja et al., Microsoft Research, Feb 2025).
- **Node/edge:** none persisted. A four-agent pipeline (**Task Proposer → Task Refiner → Task
  Summarizer → Task Verifier**) generates one trajectory per episode from a homepage; **no shared
  graph or map is built or reused across episodes** — each trajectory is independent.
- **Safety-relevant detail (feeds RQ5):** the pipeline is explicitly instructed to **halt on CAPTCHA,
  login prompts, or payment requests**, so "no actual transactions or bookings occur" during
  synthesis. This is a coarse, rule-based safety gate, not a learned irreversibility classifier.
- **Measured on:** produced 94K trajectories, 49K unique URLs, 720K screenshots, 33M web elements, at
  ~$0.28/successful trajectory; used to train multimodal web agents.

### 1.6 Synatra
[Synatra: Turning Indirect Knowledge into Direct Demonstrations for Digital Agents at Scale](https://arxiv.org/abs/2409.15637)
(NeurIPS 2024). Converts indirect knowledge (tutorials, human-written how-tos) into direct
observation-action demonstrations via LLM relabeling. No graph; relevant only as another
"trajectory synthesis without a persisted map" data point. 100k synthetic demos beat GPT-3.5 on
Mind2Web/WebArena when used to fine-tune a 7B model, at ~3% the cost of human demonstrations.

### 1.7 AutoWebGLM
[AutoWebGLM: A Large Language Model-based Web Navigating Agent](https://arxiv.org/abs/2404.03648)
(KDD 2024). An **HTML-simplification algorithm** (a per-page pruning/compression procedure, not a
cross-page graph) plus curriculum RL/rejection sampling. Relevant to P1 only as prior art on
observation compression, not state identity or graph structure. Introduces the AutoWebBench
benchmark.

### 1.8 Agent-E
[Agent-E: From Autonomous Web Navigation to Foundational Design Principles in Agentic Systems](https://arxiv.org/abs/2407.13032)
(Emergence AI, July 2024); [code](https://github.com/EmergenceAI/Agent-E). Hierarchical
planner/executor architecture with **"change observation"**: it explicitly diffs the DOM/state before
and after an action to detect what actually changed — directly relevant to "did the last action work"
(§1.4 sub-problem 2 in the foundations doc) but again per-step, not a persisted graph. Beats prior
SOTA on WebVoyager by 10–30% in most categories.

### 1.9 WILBUR
[WILBUR: Adaptive In-Context Learning for Robust and Accurate Web Agents](https://arxiv.org/abs/2404.05902)
(2024). Notable for being **"the first agent that can backtrack to a previous state during
execution"** in a live-web (non-resettable) setting, using a learned ranking model over past
successful/failed demonstrations to populate the prompt. 53% on WebVoyager, text-only SOTA at
publication. No persisted graph; its "backtrack" is a live re-navigation, not an archive replay —
relevant precedent for how graph "termination predicates" (§4 P1's own proposal) might detect and
recover from failed macro execution.

### 1.10 Agent Skill Induction (ASI)
[Inducing Programmatic Skills for Agentic Tasks](https://arxiv.org/abs/2504.06821) (Wang, Gandhi,
Neubig, Fried — COLM 2025). This is very likely the paper the foundations doc's "skill induction"
reference points at (same first author and lineage as AWM). **Node/edge:** none — the unit is a
**program-shaped skill** (e.g. `search_product(name)`) synthesized from a trajectory, verified by
re-running it, and stored for reuse; the paper frames this as executable-program memory, one rung
above AWM's natural-language workflows. Directly relevant to P2 (graph-as-tool-API) more than P1
(graph-as-structure): a "skill" is much like a layer-5 macro/option in the foundations doc's own
formalism (§2.3), but it is retrieved from a flat skill library, not a graph with typed nodes.
Sibling systems in the same "skill induction" sub-paradigm, also verified real: [SkillWeaver](https://arxiv.org/abs/2504.07079)
(web agents self-improve by discovering/honing skills as APIs; +31.8%/+39.8% relative success on
WebArena/real sites) and [AppAgentX](https://arxiv.org/html/2503.02268v3) (mobile GUI agent evolving
repetitive operations into higher-level actions from purely visual information, no backend access).

### 1.11 ExACT (R-MCTS)
[ExACT: Teaching AI Agents to Explore with Reflective-MCTS and Exploratory Learning](https://arxiv.org/abs/2410.02052)
(Oct 2024); [code](https://github.com/microsoft/ExACT). Reflective Monte Carlo Tree Search: extends
MCTS with contrastive reflection over past mistakes and multi-agent-debate state-value estimation.
**Node:** an MCTS tree node = an observation reached during search (not deduplicated across search
trees or episodes — see also §1.13 below, same issue as Koh et al.). 6–30% relative improvement over
prior SOTA on VisualWebArena with GPT-4o.

### 1.12 WebDreamer
[Is Your LLM Secretly a World Model of the Internet? Model-Based Planning for Web Agents](https://arxiv.org/abs/2411.06559)
(Nov 2024). Uses the LLM itself as a *simulated* world model: for each candidate action it generates
a natural-language description of the likely resulting page, scores the candidates, and only then
acts — explicitly framed as an alternative to tree search because **"real-world environments such as
the web are rife with irreversible actions, which undermines the feasibility of backtracking, a
cornerstone of (tree) search."** This is the single clearest statement in the literature of exactly
the concern raised in §4 P1's "safety constraint," and it is offered as a structural workaround
(simulate instead of execute) rather than a solved classifier. 4–5× more efficient than tree search
at comparable performance; ships a fine-tuned Dreamer-7B trained on 3.1M web interactions.

### 1.13 Tree search for web agents (Koh et al.)
[Tree Search for Language Model Agents](https://arxiv.org/abs/2407.01476) (Koh, McAleer, Fried,
Salakhutdinov, 2024); [code](https://github.com/kohjingyu/search-agents). Best-first tree search
**in the actual environment**, not a simulator. Two details are directly load-bearing for this
project:
- **Backtracking mechanism:** because naive `go_back()` can silently lose scroll offset and typed
  text, the paper **resets the environment and replays the entire recorded action sequence** to
  return to a prior node. This is only possible because WebArena/VisualWebArena are deterministic,
  resettable sandboxes — it is **not available on a live website**, which is exactly the gap between
  "online, deterministic, self-hosted" and "online, live web" in the foundations doc's own §3.2/§3.3
  taxonomy.
- **Explicit acknowledgment of the safety gap:** the paper states that for real-world deployment
  *"we will need to restrict the search space to actions that are not destructive,"* and proposes
  (but does not implement) a **classifier that predicts when certain actions are destructive**, folded
  into the value function. This is a direct, citable confirmation that **the irreversibility
  classifier §4 P1 calls "a real sub-project, not a footnote" is recognized in the literature as
  unsolved, not solved** — reinforcing rather than contradicting the foundations doc.
- **Value function:** a prompted GPT-4o scores states as success/failure/"on track" (0/0.5/1),
  averaged over 20 sampled reasoning paths (self-consistency), no logprob access needed.
- **Measured on:** VisualWebArena (26.4% success, +39.7% relative over baseline), WebArena (19.2%,
  +28.0% relative).

### 1.14 Not verified / distinguish from real prior art
- **"WebCanvas"** and **"AgentDojo," "WASP," "BrowserART"** are already independently listed and cited
  correctly in §3 of the foundations doc (checkpoint scoring and safety/adversarial benchmarks
  respectively) — real, but out of R1's scope (R4/safety, not state abstraction).
- I found **no evidence of a published system called exactly "site map for web agents" or "world
  model" that matches §4 P1's two-layer type/instance proposal** — see verdict in §7.

---

## 2. State abstraction / state aliasing — what identifies "the same page state"

### 2.1 The pre-LLM literature already has a mature answer, and it predates this project's framing
by 10–15 years. **Crawljax** ([Mesbah, van Deursen, Lenselink, *Crawling Ajax-Based Web Applications
through Dynamic Analysis of User Interface State Changes*](https://dl.acm.org/doi/10.1145/2109205.2109208),
ACM TWEB 2012; [code](https://github.com/crawljax/crawljax)) treats a Rich Internet Application as a
**finite state machine**: states are distinct DOMs, transitions are fired DOM events
(`onclick`/`onsubmit`/`mouseover` etc.), and the crawler incrementally infers a **state-flow graph**.
Crucially, Crawljax formalizes exactly the node-identity question §4 P1 poses, under the name
**"state abstraction function."** It is *configurable*, because no single equivalence relation is
correct for all sites:
- Plain string/edit-distance comparison of the DOM (Levenshtein/RTED) — collides too rarely to be
  cheap at scale, and is exactly the "explodes on distinct data" failure mode §4 P1 warns about for
  raw DOM hashing if used without stripping.
- **Oracle Comparator Pipelining** — a configurable chain of strippers that remove known-irrelevant
  substrings (timestamps, ad banners, session tokens) before hashing, closely paralleling the "strip
  too aggressively and distinct pages collide" tension the foundations doc names for DOM-skeleton
  hashing — Crawljax's answer is that the stripping rules are **hand-tuned per site**, which is a real
  cost, not a solved problem.
- Newer Crawljax-pluggable abstraction functions, confirmed via a recent empirical study
  ([*Understanding Automated Web GUI Testing: An Empirical Study Across Exploration Strategies and
  State Abstractions*](https://arxiv.org/abs/2606.16650), 2026): **StrCmp, Gestalt, RTED, PDiff,
  WebEmbed, and Judge** are named, comparable, swappable abstraction functions in this literature —
  i.e., "what counts as the same state" is treated as a **first-class, benchmarkable design
  parameter**, exactly the framing §4 P1 should adopt rather than picking one method a priori. The
  study's key finding, directly relevant to design choice: **"strict, fine-grained abstractions favor
  model-based [BFS/graph] exploration strategies, while compact ones better support RL-based
  strategies,"** and *"code coverage is weakly correlated with failure-revealing ability"* — a
  warning that whichever node-identity scheme is chosen should be validated against the downstream
  task (macro reuse, in this project's case), not just against a coverage/parsimony proxy.
- **WebEmbed** ([*Neural Embeddings for Web Testing*](https://arxiv.org/abs/2306.07400), ICST 2026)
  is the visual/learned-embedding line: a transformer-based Siamese network learns a similarity
  embedding over rendered page structure+text jointly, explicitly to fix near-duplicate/state-alias
  errors that string- and structure-based methods miss. Reports a 56% average F1 improvement on
  near-duplicate detection and 6–21% (avg. 12%) code-coverage improvement over prior state-of-the-art
  model-based crawling, evaluated on 9 web applications. This is direct, load-bearing evidence *for*
  the foundations doc's "screenshot embedding cluster" node candidate — it is not merely a
  hypothesis, it has a name, an evaluated implementation, and a reported effect size.
- **Judge** ([*Judge: Effective State Abstraction for Guiding Automated Web GUI Testing*](https://dl.acm.org/doi/10.1145/3736162),
  ACM TOSEM 2025/2026 — abstract and citing context verified via secondary sources; the ACM page
  itself returned HTTP 403 to automated fetch, so full-text detail is `[could not verify]` beyond what
  the citing survey above reports) uses structure-merging plus contrastive learning and is reported
  by the 2606.16650 survey as the most effective abstraction technique for guiding Crawljax-style
  exploration among the six compared.

**Implication for §4 P1:** the "canonical URL / DOM hash / embedding / LLM label" list in the
foundations doc is correct as a taxonomy, but it is *reinventing categories that already have named,
evaluated instances in the web-testing literature* (StrCmp≈string/edit-distance,
Gestalt/RTED/PDiff≈structural diffing variants, WebEmbed≈screenshot/structure embedding,
Judge≈learned contrastive abstraction). This body of work should be treated as the baseline set to
beat or reuse, not reinvented from scratch.

### 2.2 What none of the above solves: LLM semantic labels as node identity
No source found treats "ask an LLM to name this page state" as a *primary* dedup key with reported
precision/recall — it appears only as a secondary annotation layer on top of a structural/visual
equivalence check (e.g., NNetNav's trajectory summarizer labels *changes*, not states; LASER's
states are hand-named, not LLM-induced). §4 P1's own listed failure mode for this candidate
("non-deterministic and uncheckable") is unrefuted by anything found — it should be treated as
weak evidence, i.e. a label to attach to a node whose *identity* is decided by a structural or visual
method, never the identity criterion itself.

### 2.3 URL canonicalization
Not separately treated as a research topic in the GUI-testing or web-agent literature I could find
(it is treated as solved/standard practice — strip session params, sort query keys, resolve
redirects — inside crawling infrastructure, not published as a contribution). `[could not verify:
searched for "URL canonicalization" + "web agent state" specifically and found only generic SEO/crawl
-budget guidance, not a research contribution addressing agent state identity]`. This matches §4 P1's
own framing of canonical URL as a naive baseline that "explodes on `/product/{id}`" — correct, and
apparently nobody has published a fix that isn't "combine URL with a DOM/visual signal," which is
what Crawljax/WebEmbed/Judge already do.

---

## 3. The two-layer (type/instance) proposal — is it supported, contradicted, or unexplored?

**Mostly unexplored as stated, but each half has real precedent that the doc should cite.**

- **Precedent for the *type* layer existing as a useful abstraction:** LASER (§1.4) hand-authors a
  small set of named abstract page types per task family and shows it improves recoverability/
  performance — evidence that a type layer is *useful*, but not evidence that it can be *induced*
  automatically; LASER's types are hand-engineered.
- **Precedent for automatic induction of "the same kind of page" from structure:** the wrapper-
  induction and web-page-classification literatures, which predate LLM agents by two decades and
  solve a closely related (not identical) problem:
  - **Wrapper induction** ([Kushmerick, Weld & Doorenbos, *Wrapper Induction for Information
    Extraction*](https://homes.cs.washington.edu/~weld/papers/kushmerick-ijcai97.pdf), IJCAI 1997;
    survey: [*Web wrapper induction: a brief survey*](https://dl.acm.org/doi/10.5555/1218702.1218707))
    learns extraction rules for a **site's record structure** from labeled examples — i.e. it induces
    a schema for *what data a page type contains*, which is adjacent to but not the same question as
    §4 P1's "what page type is this, and what affordances does it expose." Follow-on work explicitly
    addresses **wrapper maintenance** as sites change (schema-guided repair) — directly relevant to
    RQ6/staleness (§6 below).
  - **Web page genre/template classification** (e.g. [*Web page genre classification*](https://dl.acm.org/doi/10.1145/1363686.1364247),
    2008; template-detection patents/papers) clusters pages by structural+stylistic features into
    types like "product page," "article," "login form" — this is close kin to the "type layer," but
    it targets a fixed, small taxonomy decided in advance (genre labels), not an open-ended, site-
    specific, agent-discoverable type space, and it is not connected to *affordances* (what actions
    are available) at all — only to content/genre.
  - Clustering literature on structurally similar pages (e.g. "Clustering Web pages based on their
    structure") is the closest direct antecedent to "unsupervised page-type induction," but again
    predates and is disconnected from the agent-affordance framing.
- **What is genuinely unexplored (as far as this search found):** a system that (a) unsupervised-ly
  clusters pages into types using structure/visual/semantic signals, (b) attaches to each type the
  *affordance transitions* observed across its instances (not just content schema), and (c) uses that
  type layer as the durable, transferable object while treating concrete URLs as an evictable
  instance cache — i.e., exactly §4 P1's proposal, end to end, for agentic web navigation. The
  individual pieces (page clustering, wrapper/schema induction, LASER's hand-built types, AriGraph's
  triplet-based semantic graph for text-world agents — see below) exist; **the specific combination
  is not published**, which makes §4 P1 a genuine, stateable contribution rather than a restatement
  of known work — but it also means there is no existing evaluation to lean on for "does this
  actually transfer/compress well," which is a real risk to flag (see Open Questions).
- **Adjacent but distinct:** [AriGraph](https://arxiv.org/abs/2407.04363) (2024) builds a semantic
  knowledge graph (entity/relation triplets) plus episodic memory for LLM agents in **text-adventure
  games** (TextWorld), not the web — it is evidence that a "learned schema + instance memory" split
  is a productive general pattern for LLM-agent world models, but its nodes are entities/facts, not
  page types, and its domain has no DOM/URL/browser-state complications at all. [Web Agents with
  World Models](https://arxiv.org/abs/2410.13232) (WMA) is the nearest web-specific relative: it
  trains a model to predict a **transition-focused abstraction** of the next observation (only what
  changed, not the whole page) rather than a full observation — this is a different axis (compress
  the *prediction target*, not compress *many instances into a type*), but it is strong independent
  evidence that naive full-page representations are too redundant/costly to use directly, which
  supports §4 P1's instinct to compress.

**Verdict on this sub-question:** the two-layer idea is **not published as such** in either the
web-agent or the classical web-crawling literature I could retrieve, but every individual assumption
it rests on (page clustering works; schema/wrapper induction is tractable and needs maintenance;
hand-built type layers help; compressing to "what changed" beats full-observation prediction) has
independent, citable support. Treat it as a plausible, motivated, but empirically untested design,
not a validated one.

---

## 4. Partial observability specifics: what published systems do about state not in the URL

- **Modals, applied filters, cart contents, auth state:** no system found treats these as a first-
  class part of node identity. The closest are:
  - Crawljax's DOM-based state machine *does* capture these implicitly, because a modal open/closed
    or a filter applied changes the DOM and therefore (if the abstraction function is sensitive
    enough) counts as a different state — but this is a side effect of DOM-hashing, not a deliberate
    design for these categories, and the state-abstraction survey's own finding (§2.1) that "strict
    abstractions" vs. "compact abstractions" trade off coverage vs. tractability shows this is exactly
    where over- or under-collision happens in practice.
  - Agent-E's "change observation" mechanism (§1.8) explicitly diffs before/after DOM to detect that
    *something* changed post-action, which is a mechanism that would catch a modal opening, but the
    paper does not specifically discuss modal-vs-navigation classification as a named problem.
  - I found **no published system that explicitly models "auth state" or "cart contents" as
    orthogonal hidden state variables composed with a visible page type** (i.e., a POMDP belief-state
    factorization). This is a real gap, and §4 P1's flat "modal open, cart contents, auth state,
    applied filter" list is accurate as a list of failure modes but is **not something the literature
    has a factored solution for** — everyone folds it back into "just hash more of the DOM/observation
    and hope the abstraction function is sensitive enough," which the empirical survey (§2.1) shows is
    a real, measured trade-off (fine-grained abstraction costs state explosion; compact abstraction
    costs missed distinctions), not a solved dimension.
- **Infinite scroll:** not directly addressed in the fetched sources; `[could not verify: no
  paper found that treats infinite-scroll pagination as a state-identity problem specifically for
  agents]`. It is a special case of "same DOM skeleton, unboundedly more instances," which is exactly
  the failure mode the foundations doc names for DOM-skeleton hashing, but I found no dedicated
  treatment.
- **SPA client-side routing:** confirmed as a known, general pain point in web testing/security
  tooling (not agent-specific): traditional crawlers "can't discover new UI routes" because navigation
  is JS-driven rather than URL-driven, and testing tools solve it by running a real browser and
  triggering interactions rather than parsing links — i.e., the same "DOM-event-driven state machine"
  approach Crawljax pioneered for Ajax apps in 2012 is the standing answer for SPAs specifically
  because URL-only node identity structurally fails there. This directly *validates* §4 P1's listed
  failure mode ("misses state not in the URL") rather than adding anything new to it.

---

## 5. Exploration safety: classifying irreversible/destructive actions before taking them

This is the best-supported and most actively-developing area found. Confirmed real, with details:

- **The problem is explicitly named as open** by [Tree Search for Language Model Agents](https://arxiv.org/abs/2407.01476)
  (§1.13): *"For real world deployment, we will need to restrict the search space to actions that are
  not destructive"* — proposed as future work (a classifier folded into the value function), not
  implemented.
- **[WebDreamer](https://arxiv.org/abs/2411.06559)** (§1.12) sidesteps the problem structurally by
  never executing speculative actions at all — it simulates them in text and only executes the
  chosen one. This is a legitimate alternative strategy to a classifier: **don't explore destructively
  in the first place, imagine instead.**
- **[ST-WebAgentBench](https://arxiv.org/abs/2410.06703)** (Levy et al., 2024;
  [code](https://github.com/segev-shlomov/ST-WebAgentBench)) is the safety *benchmark*, extending
  WebArena/BrowserGym with 222 tasks paired with policy constraints, scored on 6 dimensions (including
  user consent and robustness), with a **Completion-under-Policy (CuP)** metric and a **Risk Ratio**.
  Reported finding: agents' CuP is less than two-thirds of their nominal completion rate — i.e.
  agents that "succeed" by the task metric routinely violate safety policy along the way. This is the
  right benchmark to adopt for RQ5/P4-safety evaluation, and it is already correctly cited in §3.6 of
  the foundations doc.
- **Dedicated action-risk-classification systems (2025–2026, all verified):**
  - [WebGuard: Building a Generalizable Guardrail for Web Agents](https://arxiv.org/abs/2507.14293) —
    **the most directly relevant hit for "what is the state of the art for a 'do not click Delete'
    filter."** A human-annotated dataset of 4,939 actions across 193 websites/22 domains with a
    three-tier risk schema (SAFE/LOW/HIGH). Frontier LLMs zero-shot achieve **under 60% accuracy**
    predicting action outcomes; a fine-tuned Qwen2.5-VL-7B reaches **80% overall accuracy and 76%
    recall on HIGH-risk actions** (up from 20% zero-shot recall). This is a quantified answer: current
    state of the art for pre-execution destructive-action classification is "a fine-tuned 7B
    classifier gets ~3/4 recall on high-risk actions" — good enough to be useful, nowhere near good
    enough to be the sole safeguard.
  - [InferAct](https://arxiv.org/abs/2407.11843) (2024) — Theory-of-Mind-style preemptive critic that
    flags likely-misaligned actions before execution and can request human feedback; up to 20% Macro-F1
    improvement in misaligned-action detection over baselines.
  - [SeerGuard](https://arxiv.org/abs/2607.15550) and [CORA](https://arxiv.org/abs/2604.09155)
    (2026, mobile GUI) — pre-execution, world-model-based and conformal-risk-controlled guardrails,
    respectively; CORA specifically targets *statistical guarantees* on the rate of harmful executed
    actions, which is a materially stronger safety framing than a bare classifier accuracy number.
  - [Magentic-UI](https://arxiv.org/abs/2507.22358) — ships an "Action Guard" that routes any
    irreversible/harmful action to human review via a two-stage heuristic-plus-LLM-judge pipeline;
    notable as a deployed, human-in-the-loop design rather than a pure classifier.
- **Historical crawler practice (pre-LLM):** crawlers avoid destructive actions largely *by
  construction*, not by classification — they only issue `GET` requests, and the HTTP spec's
  safe/idempotent contract for `GET` (vs. `POST`/`PUT`/`DELETE`) is the load-bearing assumption; a
  server that violates this contract (a `GET` that deletes) is considered a server-side bug, not
  something the crawler must detect. `robots.txt`/`nofollow` additionally let a site operator mark
  paths as off-limits, but compliance is voluntary and not a safety guarantee (crawler traps and
  malicious/misconfigured sites exist precisely because this is advisory). **This does not transfer
  to GUI agents**, because a layer-2 `click()` has no HTTP-verb-level safety contract at all — a
  "Delete" button and a "Next page" button are both just `<button>` elements. This is a clean,
  citable argument for why the irreversibility-classifier sub-project is *necessary* for a GUI/browser
  agent in a way it never was for a URL-following crawler: **the safety invariant crawlers relied on
  for 30 years (GET is safe) has no analogue at the click level, so an explicit classifier is not
  optional.**

**Bottom line for RQ5:** §4 P1 is right that this is "a real sub-project, not a footnote." The
literature now has purpose-built datasets and baselines (WebGuard's 4,939-action dataset is the one
to build/evaluate against), fine-tuned classifiers reaching ~80% accuracy / ~76% high-risk recall, and
at least one benchmark (ST-WebAgentBench) to measure downstream effect — but no system reaches
reliability that would justify unsupervised exploration with zero human oversight on transactional
affordances. A hybrid (classifier gate + conservative default-refuse on low-confidence + human
confirmation for anything above a HIGH-risk threshold, à la Magentic-UI) is the state of the art, not
a solved classifier alone.

---

## 6. Graph staleness: maintaining a site model as the site changes

- **Wrapper maintenance** (schema-guided wrapper repair, part of the classical wrapper-induction
  literature cited in §3) is the most mature published treatment: when a site's markup changes, use
  the previously-learned schema to detect the wrapper has broken (extraction no longer matches
  expected structure) and re-induce/repair it — directly analogous to what a "type layer" would need
  to do when a page type's DOM structure shifts.
- **Crawljax-style re-crawling:** the state-flow graph is not a one-shot artifact in this literature;
  standard practice is periodic re-crawl and diff against the previous state-flow graph, using the
  same state-abstraction function (§2.1) to decide whether an update is a "new state" or "the same
  state with fresh content." The tunability of the abstraction function directly determines
  false-staleness-alarm rate.
- **General web change-detection tooling** (e.g. open-source [changedetection.io](https://github.com/dgtlmoon/changedetection.io),
  commercial monitoring services) confirms the standard architecture: content hashing, revisit
  scheduling driven by observed change frequency per page (a per-node "expected drift rate," directly
  reusable as the `last_verified` + decay policy the foundations doc's edge schema already proposes),
  and webhook-driven re-scrape triggers. Nothing agent-specific was found beyond this — i.e. **the
  graph-staleness problem for an agent's site model is currently expected to be solved by importing
  classical web-monitoring infrastructure wholesale**, not by anything published specifically for
  LLM-agent site graphs. `[could not verify: searched specifically for "agent site graph staleness"
  and "world model drift" restricted to agent literature; found only generic ML "concept drift"
  results and classical web-monitoring tooling, no agent-graph-specific invalidation policy paper]`.
- **Implication:** the edge schema's `last_verified` timestamp plus a decay/re-verification policy
  (§4 P1 already proposes this) is the right shape and matches classical practice; what's missing from
  the doc is a re-crawl *trigger* policy — e.g. per-node observed drift rate, or trigger-on-macro-
  failure (a macro's termination predicate failing is itself the cheapest staleness signal, since it
  costs nothing extra to detect — this should be stated explicitly as the primary staleness detector,
  with scheduled re-crawl as a fallback for pages that are never visited by a macro).

---

## Corrections to docs/01-foundations.md

> "**Prior art not to reinvent:** unsupervised-exploration-then-relabel work (NNetNav and similar);
> Agent Workflow Memory; Go-Explore's archive-of-states (closest conceptual ancestor); skill
> induction."

- **NNetNav does not build or persist a graph.** It is exploration-then-retroactive-relabeling
  *for synthetic training-data generation* (SFT demonstrations), operating within single episodes.
  There is no cross-episode map. If cited as prior art for *graph construction* specifically, this is
  inaccurate; it should be cited (correctly) as prior art for *safe unsupervised exploration policy
  design and trajectory relabeling*, which is a different, real, and still-relevant contribution to
  this project (Phase 1's curiosity-driven crawl needs an exploration policy, and NNetNav's
  persona-seeded `π_LM` plus prune-on-unlabelable-subtask is a reasonable candidate).
- **AWM's unit is a flat natural-language workflow, not a graph.** Correctly described in the
  foundations doc's §1.3 ("nearest neighbour... the delta we claim is graph structure"), so no
  correction needed there — but §4 P1's "prior art not to reinvent" line should not imply AWM has
  graph structure; it explicitly does not, which is precisely what makes the graph proposal a
  structural delta rather than a relabeling of AWM.
- **Go-Explore's archive-of-states mechanism fundamentally depends on a resettable simulator**
  ("return" step requires deterministically resetting to a prior state). A live website is not
  resettable this way; even WebArena-style deterministic sandboxes require explicit environment
  resets, as confirmed by Koh et al.'s tree-search implementation (§1.13), which resets-and-replays
  rather than using a native "undo." §4 P1 calls Go-Explore "closest conceptual ancestor" without
  flagging this gap; it should, because it is exactly the reason "budgeted BFS/DFS crawl... dangerous
  on transactional edges" (the doc's own next sentence) is a harder version of the problem Go-Explore
  solved — Go-Explore never had to worry about an action being unrecoverable.
- **Skill induction is not primarily graph-shaped either.** The clearest citable instance
  ([Inducing Programmatic Skills for Agentic Tasks](https://arxiv.org/abs/2504.06821)) produces a
  flat library of callable programs, not typed nodes with affordance edges. It is better understood
  as prior art for **P2 (the tool API over the graph)** — a skill is close to the layer-5 "option"
  the foundations doc's own §2.3 formalism defines — than for P1 (graph structure) as filed.

> "**Recommendation: a two-layer graph.**"

No factual correction — see §3 above: this is not contradicted by anything found, but it is also not
independently validated by any existing system; treat the confidence level in the doc's phrasing
("Recommendation") as appropriately hedged, and do not upgrade it to "established" without running
the type-induction experiment described in Design Implications below.

---

## Verdict: is §4 P1's design defensible?

**Yes, directionally — the taxonomy of node candidates and their failure modes is accurate and
consistent with 15+ years of prior art in classical web-application testing, which the doc currently
under-cites. The two-layer proposal is a genuine, motivated, unpublished combination of known parts,
not an already-solved problem and not a fantasy. The weakest links are (a) the "prior art not to
reinvent" citations, three of which (NNetNav, AWM, skill induction) do not actually build graphs and
should be recharacterized as prior art for adjacent sub-problems (exploration policy, tool API,
macro/option representation) rather than for P1 itself, and (b) the absence of any factored treatment
of hidden state (auth/cart/filters/modals) anywhere in the literature, which the doc should flag as an
open risk rather than a solved list of failure modes.** The safety constraint is not a footnote — it
is an acknowledged-open problem at the frontier of current publications (Koh et al.'s own paper says
so), with the best available baseline being WebGuard's fine-tuned classifier (~80% accuracy, ~76%
high-risk recall) — good enough to gate, not good enough to trust unsupervised.

---

## Design implications

A concrete node-identity and edge schema, justified from the sources above:

**Node identity — layered, not singular (borrowing Crawljax's "configurable abstraction function"
insight rather than picking one method):**
1. **Primary key = (canonicalized URL pattern, structural fingerprint).** Canonicalize the URL by
   template-izing path/query variables observed to vary across many instances with identical DOM
   skeleton (this is exactly what wrapper induction and template detection already do — reuse rather
   than reinvent). The structural fingerprint should be a **Crawljax-style Oracle-Comparator-Pipeline
   hash**: strip known-irrelevant substrings (timestamps, prices, ad slots, CSRF tokens), then hash
   the remaining DOM skeleton (tag+role+structural-path, matching the foundations doc's own edge-
   locator recommendation in §4 P1).
2. **Secondary signal = a WebEmbed-style learned visual/structural embedding**, used only to *merge*
   candidate nodes the primary key over-splits (e.g. A/B-tested layouts, minor markup churn) — not as
   the primary key, because it is reportedly effective (56% F1 gain on near-duplicate detection) but
   "opaque and threshold-sensitive" exactly as the foundations doc warns; use it as a second-pass
   clustering step with a human/LLM-reviewed merge decision, not a silent auto-merge.
3. **Type layer = unsupervised clustering over (2)'s embeddings across all instances of a site**,
   labeled post-hoc with an LLM-generated name for readability (never for identity, per §2.2's
   finding that no source treats LLM labels as a reliable identity key). Each type node carries the
   union of affordances observed across its instances — this is the concrete mechanism this project
   would need to invent, since nothing found does exactly this for agent affordance graphs.
4. **Hidden-state factors (auth, cart, filters, modal) are NOT folded into node identity.** Instead,
   model them as **named boolean/enum context variables attached to the *episode*, not the node**
   (a small explicit belief-state vector: `{authenticated: bool, cart_nonempty: bool, active_filters:
   set, modal_open: bool}`), checked as **edge preconditions** (already in the foundations doc's edge
   schema) rather than multiplying the node space. This directly avoids the node-explosion failure
   mode of "fine-grained abstraction" that the 2606.16650 survey found to hurt model-based
   exploration, while still respecting partial observability. This is the one concrete design change
   this research motivates beyond what §4 P1 already states: **don't try to make hidden state part of
   node identity at all; make it a separate factored context that gates edges.**

**Edge schema (confirms and slightly extends §4 P1's own proposal):**
```
edge = {
  source_type, source_instance,
  affordance: { role, accessible_name/text, structural_path },  # never bare coordinates
  action: {type, params},
  target_type, target_instance,
  preconditions: {auth: bool|None, cart_nonempty: bool|None, filters: set|None, modal_open: bool|None},
  risk_tier: SAFE | LOW | HIGH,        # WebGuard-style classifier output, gates exploration
  success_prob, observed_cost,
  reversibility: bool,                  # or explicit "undo affordance" if one exists
  termination_predicate,                # per §2.3 options formalism, also doubles as staleness probe
  last_verified, decay_policy
}
```
**Staleness policy:** treat a failed termination predicate during normal macro use as the primary,
free staleness signal (no extra crawl cost); fall back to scheduled re-verification only for
type-layer nodes with no recent macro traffic, at a rate proportional to observed historical drift
(reusing classical web-monitoring re-crawl scheduling, §6).

**Safety gate:** every edge above `LOW` risk_tier requires either (a) a human confirmation the first
time it is traversed during exploration, or (b) exclusion from the *exploration* policy entirely
while remaining executable only when a task explicitly and deliberately targets it (mirrors
Magentic-UI's Action Guard pattern and WebDreamer's "simulate, don't execute speculatively" stance).
Do not rely on a classifier alone — current SOTA recall on HIGH-risk actions is ~76% (WebGuard),
which is not adequate as a sole safeguard for exploration that runs unattended.

---

## Open questions

1. **Does the type layer actually compress/transfer?** No existing system tests this for web
   affordance graphs. The project's own Phase 3 ("transfer... the claim with the longest legs") is
   exactly the missing experiment; nothing in the literature de-risks it in advance.
2. **What is the right granularity for "structural fingerprint"?** The empirical survey (2606.16650)
   shows fine-vs-coarse abstraction is a real, measured trade-off with no universal winner — this
   needs to be tuned per-site or learned, not fixed a priori.
3. **Can hidden-state factors realistically be enumerated in advance?** The proposed design (§ above)
   assumes a small, named set of context variables (auth/cart/filters/modal). Real sites may have
   more idiosyncratic hidden state (wizard step, A/B bucket, feature flags) that this factoring
   misses; no published system was found that discovers hidden-state factors automatically rather
   than having them hand-specified.
4. **Is a fine-tuned 7B risk classifier (WebGuard-class, ~76% HIGH-risk recall) an acceptable
   exploration gate, or does the ~24% miss rate mean unsupervised exploration on transactional
   affordances is simply not viable without a human in the loop at all, ever?** This is a policy
   decision the project needs to make explicitly, since no published system claims a higher bar.
5. **Infinite scroll and SPA route explosion**: no dedicated published treatment was found for
   agent-specific state identity here beyond "run a real browser and treat DOM-event-driven changes
   as the state machine" (Crawljax's general answer). Whether that generalizes cheaply to modern
   infinite-scroll feeds (effectively unbounded instance count under one type) is untested.
6. **Should the "same" abstraction function be used for exploration-time novelty detection and for
   task-time node lookup?** Crawljax's literature treats these as the same function; this project's
   two-layer design implies they might legitimately differ (coarse for the type layer at retrieval
   time, fine for novelty detection during crawling) — worth flagging as a design fork for R2/R3 to
   pick up, since it interacts with P3's uncertainty/surprisal signal (a coarse abstraction function
   would mechanically suppress surprisal, confounding exactly the quantity P3 wants to measure).
