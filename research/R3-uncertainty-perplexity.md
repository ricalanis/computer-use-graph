# R3 — Uncertainty, Perplexity, and Curiosity-Driven Exploration

**Scope:** verification and stress-test of `docs/01-foundations.md` §4 P3 (perplexity/uncertainty
as control signal and measurement). Public sources only, retrieved live. Every claim below is
either sourced with a URL I actually fetched, or marked `[could not verify]` with what I searched.

---

## 1. Uncertainty quantification for LLMs — what actually works

No single method is well-calibrated across the board; calibration quality is method-,
task-, and length-dependent, and several widely-cited numbers are much weaker than the intuitive
story suggests.

- **Token-level NLL / raw perplexity.** Baseline, cheapest, and the *worst-behaved* signal in the
  survey literature for free-text answers, precisely because it conflates two different things:
  how surprising the content is and how long/how common the phrasing is. Length bias is
  well-documented: sequence-level joint likelihood decreases roughly exponentially with length, so
  raw NLL grows roughly linearly with length purely as an artifact, independent of correctness.
  ([Uncertainty in NLP survey, arXiv:2306.04459](https://arxiv.org/pdf/2306.04459); [Uncertainty
  Estimation in Autoregressive Structured Prediction, arXiv:2002.07650](https://arxiv.org/pdf/2002.07650))

- **Length-normalized NLL (mean per-token log-prob / "perplexity").** The standard fix — divide by
  length — is only a partial fix: naive length normalization is well documented to *overcorrect*,
  flipping the bias to favor long completions instead of penalizing them.
  ([length-normalization discussion, arXiv:2505.19060 "UNCERTAINTY-LINE"](https://arxiv.org/pdf/2505.19060);
  general discussion collected via search, medium.com summary of normalization tradeoffs)

- **Predictive entropy over next-token / next-answer distributions.** Same length confound as NLL
  when computed over free text; better-behaved when computed over a small enumerable set (this is
  exactly the argument §4 P3(a) makes for scoring over enumerated candidate actions rather than
  free text — see §3 below, this is *correct*).

- **Semantic entropy (Farquhar, Kuhn, Kossen, Gal et al., *Nature* 2024, "Detecting hallucinations
  in large language models using semantic entropy").** Clusters sampled generations by semantic
  equivalence (via NLI entailment) before computing entropy, removing surface-form/paraphrase
  variance from the entropy estimate. Reported to beat naive predictive entropy, lexical
  similarity, and P(true) baselines on AUROC/AURAC across QA, biography, and math datasets and
  across GPT-4, LLaMA-2, and Falcon. I could not retrieve the exact numeric AUROC table (Nature is
  paywalled; the arXiv preprint and OATML blog summarize but do not repeat the table) — treat the
  magnitude claim as **directionally sourced but the exact numbers `[could not verify — searched
  nature.com (403/login-walled) and OATML blog which describes but doesn't tabulate]`**.
  ([OATML blog summary](https://oatml.cs.ox.ac.uk/blog/2024/06/19/detecting_hallucinations_2024.html))
  A follow-up, **Semantic Entropy Probes** (Kossen et al.), trains a linear probe on hidden states
  to *predict* semantic entropy without sampling — cheap, but its own AUROC is modest: on a later
  independent evaluation (temporal-knowledge-drift study), SEP reaches only **AUROC 0.57**, in the
  same range as SAPLMA (0.53) and CCS (0.54) — i.e., trained hidden-state probes for
  truthfulness/hallucination are only weakly better than chance in that harder, out-of-distribution
  setting. ([Semantic Entropy Probes, arXiv:2406.15927](https://arxiv.org/abs/2406.15927);
  comparison numbers from [arXiv:2605.09195, "Geometry of Forgetting"](https://arxiv.org/html/2605.09195))
  This is an important calibration warning: **probe-based and even semantic-entropy-based signals
  degrade a lot outside their original eval distribution.**

- **Self-consistency / sampling disagreement.** Sample k completions, measure answer agreement.
  Needs no logprobs, works with closed APIs. Pooled AUROC for hallucination detection reported at
  **~0.638**, below "self-evaluation"/verbalized-confidence prompting at **~0.688**, in one recent
  aggregation. Cross-model disagreement (ensembling different model families rather than just
  temperature-sampling one model) is reported to outperform both on AUROC and on selective
  abstention. ([arXiv:2604.17112, "Complementing Self-Consistency with Cross-Model
  Disagreement"](https://arxiv.org/html/2604.17112))

- **Verbalized confidence ("how sure are you, 0–100%").** Kadavath et al. 2022 ("Language Models
  (Mostly) Know What They Know") established that models *can* express roughly calibrated
  confidence when prompted, especially in the P(true) self-evaluation form. Lin et al. 2022
  established the verbalized-percentage variant. In the agent-failure-prediction literature (§2
  below), verbalized confidence at the *end* of a trajectory is the single best-performing signal
  found (AUROC ≈0.85), but it is markedly worse mid-trajectory. `[Kadavath/Lin papers found via
  search summaries, not directly fetched — see search log; treat citation as correct based on
  well-known paper titles cross-confirmed by multiple independent search results, but I did not
  open the arXiv PDF directly]`

- **P(true).** Prompt the model to judge its own output's truth and read off the normalized
  probability of the "True" token. Same Kadavath et al. 2022 origin. Same caveat as above on direct
  verification.

- **Trained probes on hidden states (CCS — Burns et al. 2022; SAPLMA — Azaria & Mitchell 2023;
  Semantic Entropy Probes).** All exploit an apparent (roughly) linear "truthfulness direction" in
  activation space. All three land at **AUROC ≈0.53–0.57** in the harder out-of-distribution
  benchmark cited above — barely above chance — despite being reported much higher in-distribution
  in their original papers. This is a genuine calibration warning about generalization, not just
  an artifact of one paper. ([arXiv:2605.09195](https://arxiv.org/html/2605.09195))

- **Conformal prediction.** Two distinct lines: (1) Kumar et al., "Conformal Prediction with LLMs
  for Multi-Choice QA" (arXiv:2305.18404) — conformal calibration over an MCQ answer set, reports
  uncertainty tightly correlated with accuracy; (2) Quach et al., "Conformal Language Modeling"
  (arXiv:2306.10193) — a genuinely different mechanism: calibrates a *stopping rule* for how many
  samples to draw and a *rejection rule* for pruning candidates, producing a set of generations
  with a statistical coverage guarantee (not a single-point confidence score). A third line, "API
  Is Enough" (arXiv:2403.01216), shows conformal calibration is achievable **without logit access**
  at all (black-box API only), using resampling. This matters directly for the P3 instrumentation
  question: **conformal methods are the one UQ family with actual statistical coverage guarantees**,
  as opposed to "AUROC looks good on this benchmark."
  ([arXiv:2306.10193](https://arxiv.org/abs/2306.10193), [arXiv:2305.18404](https://arxiv.org/abs/2305.18404),
  [arXiv:2403.01216](https://arxiv.org/html/2403.01216v1))

**Which are known to be poorly calibrated, and why:**
1. Raw free-text NLL/perplexity — length confound (above).
2. Naive predictive entropy over free text — same confound, plus surface-form variance (two
   paraphrases of the same correct answer look like "disagreement").
3. Hidden-state probes (CCS/SAPLMA/SEP) — good in-distribution, close to chance
   out-of-distribution; the "linear truthfulness direction" doesn't transfer across time/domain
   shift as well as originally reported.
4. Self-consistency alone — moderate AUROC (~0.64), beaten by verbalized self-evaluation and by
   cross-model ensembles.

---

## 2. Uncertainty for LLM *agents* specifically

This is the most important — and most damaging to §4 P3's optimism — finding of this survey.

**"Last Step Matters: Early Uncertainty Cannot Predict Failure in Long-Horizon Agents"**
(Li, Yu, Zang, Zhuang, Mo, Gan; arXiv:2608.29685, retrieved directly) tests exactly the question
P3's Phase 0 gate wants answered, on deep-research-style long-horizon agent tasks:
- **Verbal confidence at trajectory completion**: mean **AUROC ≈ 0.85** for predicting whether the
  finished trajectory succeeded.
- **All evaluated signals (verbal confidence, perplexity, others) at 50% trajectory progress**:
  **none exceed mean AUROC 0.60.**
- Mechanism identified: **"path switching"** — agents frequently abandon their current search
  direction mid-trajectory, which breaks the causal link between an early uncertainty spike and the
  final outcome (an agent that looked uncertain at step 3 may have simply recovered by step 20).
- Practical recommendation from the authors: use **final-step** confidence to decide whether to
  *restart the whole trajectory*, not in-trajectory intervention — the opposite of what a
  step-level gating architecture (as sketched in P3/P4) assumes is possible.
  ([arXiv:2608.29685](https://arxiv.org/html/2608.29685))

This is a direct, quantified counter-example to the implicit assumption in P3/§5 Phase 0 that a
step-level uncertainty signal, once validated, can be used for **within-episode** gating
("consult the graph, explore, or ask" — P3(a); "fall back to naive exploration the moment...
uncertainty spikes" — P2). If this generalizes to a web-agent + graph-lookup setting (browsing
trajectories are exactly the kind of long-horizon, replannable task where "path switching" happens
— an agent that gets confused, backtracks, and finds the right page later is the norm, not the
exception), then **Phase 0's AUROC gate as designed (per-step, not per-trajectory) may show a
signal that does not survive being used for in-episode gating**, even if the AUROC number itself
looks acceptable.

**"Uncertainty Quantification in LLM Agents: Foundations, Emerging Challenges, and Opportunities"**
(arXiv:2602.05073, retrieved directly) is a framing paper making the case that agent UQ needs its
own formalism distinct from single-turn QA UQ, for four reasons it names explicitly: (1) choice of
estimator is harder because trajectories have both discrete actions and free text; (2) uncertainty
attaches to heterogeneous entities (a tool call, an observation, a final answer — not one score);
(3) uncertainty *dynamics* over an interactive multi-turn process behave differently from a
single-shot QA distribution; (4) benchmarks for fine-grained (step-level) agent UQ are largely
missing. It reports numbers on a "τ²-bench"-style benchmark but I could not extract the actual
figures from the fetched excerpt `[could not verify exact numbers — abstract/intro only]`.

**Other agent-UQ papers found (titles/abstracts only, not deep-read):**
- **TRACER** (arXiv:2602.11409) — "Trajectory Risk Aggregation for Critical Episodes" — reports
  AUROC for both episode-level and prefix-level failure prediction; explicitly frames 0.5 as
  chance. Consistent with the "Last Step Matters" finding that prefix-level (early) prediction is
  harder than episode-level.
- **"Agentic Uncertainty Quantification"** (arXiv:2601.15703) — claims a "Dual-Process" system
  beats baselines on AUROC using internal confidence signals. `[could not verify magnitude — not
  deep-fetched]`
- **"Uncertainty Decomposition for Clarification Seeking in LLM Agents"** (arXiv:2606.19559,
  retrieved directly) — decomposes uncertainty into "action confidence" vs. "request uncertainty"
  (roughly aleatoric/epistemic for *underspecified task* vs. *hard-to-execute* step) to decide when
  to ask a clarifying question, evaluated on WebShop-Clarification and ALFWorld-Clarification
  (synthetically underspecified variants of standard benchmarks) across 5 backbones (GPT-5.1,
  DeepSeek-v3.2-exp, GLM-4.7, Qwen3.5-35B, GPT-OSS-120B). Reports **73% F1 improvement** over a
  ReAct+uncertainty-estimation baseline and **36%** over "Uncertainty-Aware Memory" on
  ALFWorld-Clarification. This is the closest published analogue to "ask for help when uncertain,"
  and it is a *prompt-based decomposition*, not a logprob-based one — worth noting because it
  suggests the actionable signal in practice is often elicited/verbalized, not measured via NLL.

**Conclusion for Q2:** published agent-uncertainty work is young (all dated 2026 by arXiv ID),
converges on **verbalized/self-evaluation confidence outperforming raw NLL/perplexity for agents**,
and the one paper that directly measured "does early uncertainty predict eventual failure"
answered **no** for step-level signals and only weakly-yes at the very end of the trajectory. This
should be read as a load-bearing risk to §4 P3, not a footnote.

---

## 3. The length/context confound

**Mechanically, yes: more context lowers per-token loss/perplexity, as a matter of course, not
because the model "understands" more.** This is well established in the scaling-laws and
long-context literature: cross-entropy loss reduction from *more context tokens* is treated as a
distinct, additive term from architectural/algorithmic improvement in decompositions of model
progress — one analysis attributes **10–60%** of year-over-year loss reduction to increased
context length alone, separate from algorithmic gains
([Algorithmic progress in language models, arXiv:2403.05812](https://arxiv.org/pdf/2403.05812)).
Separately, comparing raw perplexity numbers **across different context-length evaluation setups
is a known methodological trap**: different papers reporting different context lengths (e.g. 4096
vs. 2048 tokens) produce non-comparable absolute PPL numbers even for identical models, and
several quantization papers explicitly flag this
([RSQ, arXiv:2503.01820](https://arxiv.org/pdf/2503.01820)). The safe practice found in that
literature is: **hold context length fixed and compare relative deltas within that fixed setting**,
not absolute PPL across setups — which is effectively a weaker, less rigorous version of what §4 P3
already proposes.

**Is the "token-matched shuffled control" in P3 sufficient?** It is necessary but not sufficient,
and the literature suggests a stronger design:
- A token-matched shuffle controls for **raw context length** (the "more tokens → lower loss"
  mechanical effect above) but does not control for the **distributional statistics of the
  distractor content** (a scrambled paragraph of coherent English still differs from random noise
  in local n-gram entropy, vocabulary, and syntactic patterns that a language model partially
  exploits regardless of semantic validity).
- A **better-established control class than raw shuffling** is a **matched-entropy /
  matched-perplexity distractor**: construct the control context so that its own intrinsic
  perplexity (under the same scorer, unconditioned) equals that of the real graph context, not just
  its token count. Token-count matching controls for the length artifact; entropy/perplexity
  matching additionally controls for the "is this recognizable, low-surprisal text at all" artifact
  — a genuinely random token shuffle is *itself* unusually high-perplexity content compared to
  fluent (even semantically wrong) text, which can bias the comparison in the *opposite* direction
  from what's intended (falsely making the graph condition look better because its control is
  artificially harder to predict).
- **Permutation/randomization tests** (as used broadly in NLP eval methodology, not specific to
  this problem) — run many shuffles, build a null distribution of PPL reduction under
  "content-free but length/format-matched" conditioning, and report where the real graph's PPL
  reduction falls in that null distribution — are a more statistically rigorous version of "compare
  to one shuffled baseline," and directly answer the reviewer question "how sure are we the
  reduction isn't a fluke of this one shuffle." I could not find a paper doing exactly this for
  LLM-context PPL claims specifically; this is a design recommendation synthesized from general
  permutation-test methodology, not a citation. `[could not verify a directly on-point paper;
  searched "permutation test perplexity context conditioning" without an on-point hit]`

**Verdict on this sub-question:** the shuffled control in P3 is on the right track and better than
what most papers in this space actually do, but should be upgraded to **(a) token-count-matched AND
(b) intrinsic-perplexity-matched** distractor content, ideally with **(c) multiple shuffles** to
get a null distribution rather than one point estimate.

---

## 4. Bayesian surprise / information gain

**Canonical formulation (verified):** Itti & Baldi define Bayesian surprise as
**KL(P(M|D) ‖ P(M))** — the KL divergence between an observer's *posterior* belief over models/world-state
M after seeing data D and its *prior* belief before seeing D. The key property they emphasize:
surprise depends on how much the observation **updates belief**, not on how rare or
information-theoretically dense the observation is in Shannon's sense — a critical distinction from
raw NLL. They validated it against human eye-gaze data on natural video.
([Itti & Baldi, NeurIPS 2005 / PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC2782645/),
[NeurIPS proceedings PDF](https://proceedings.neurips.cc/paper_files/paper/2005/file/0172d289da48c48de8c5ebf3de9f7ee1-Paper.pdf))

**Application to RL/agents:** **VIME** (Houthooft, Chen, Duan, Schulman, De Turck, Abbeel, 2016,
arXiv:1605.09674) is the canonical RL instantiation: it puts a Bayesian neural network over
environment dynamics, and the intrinsic reward is the **information gain** (KL divergence between
posterior and prior over the BNN's weights) from each transition — literally Itti & Baldi's
formalism applied to a learned dynamics model instead of a perceptual model. Reported to outperform
heuristic exploration bonuses on continuous-control sparse-reward tasks. Known cost: computing it
requires a forward+backward pass through a Bayesian neural network per step, which is why it never
scaled to the pixel/Atari-scale settings that RND and ICM target — a real practicality concern for
using it as a **per-step, real-time gating signal** in a web agent, where you'd want the surprise
computation to be at least as cheap as the action itself.
([VIME, arXiv:1605.09674](https://arxiv.org/abs/1605.09674))

**Is it computable in our (LLM agent) setting, and is it better-behaved than raw NLL, as P3
claims?** Partially, with a caveat P3 elides:
- **Computable, in principle:** if "world model" = the scorer LLM's predictive distribution over
  the next-observation's type/summary label, then a **prior** (unconditioned, or graph-absent) and
  a **posterior** (graph-conditioned) distribution over that same label space can both be obtained,
  and their KL is well-defined and *is* less sensitive to raw sequence-length artifacts than NLL,
  because KL is a divergence between two distributions over the *same* support (e.g., the same
  fixed label vocabulary or same candidate set), not a joint sequence probability — so the §4 P3
  claim that this is "less sensitive to token-length artifacts than raw PPL" is basically right,
  **conditional on both distributions being computed over the same fixed candidate/label space**
  (exactly the same requirement as P3(a)'s enumerated-action-set argument).
- **The caveat:** Itti & Baldi's and VIME's surprise is a divergence between an explicit **prior
  belief distribution over a latent world model**, updated via Bayes' rule as new data arrives.
  Naively substituting "LLM's predictive distribution with graph in context" (posterior) vs.
  "without graph" (prior) is *not* actually a Bayesian update of one persistent belief state — it's
  two different forward passes with two different prompts. It is a reasonable **proxy** for
  Bayesian surprise (and probably the right practical compromise) but should not be oversold as
  literally the same quantity; the paper's phrase "Bayesian surprise... which is less sensitive to
  token-length artifacts than raw PPL" is directionally defensible but the equivalence to Itti/Baldi
  is looser than stated. No published work applying literal Itti & Baldi-style Bayesian surprise to
  LLM web/computer-use agents was found. `[could not verify — searched "Bayesian surprise LLM
  agent" and "KL divergence posterior prior LLM web agent exploration," found only the RL-era
  VIME/Itti-Baldi lineage, nothing LLM-agent-specific]`

---

## 5. Curiosity-driven exploration — canonical citations and failure modes

- **ICM** (Pathak, Agrawal, Efros, Darrell, ICML 2017, "Curiosity-driven Exploration by
  Self-Supervised Prediction") — intrinsic reward = forward-model prediction error in a *learned*
  feature space (learned via an inverse-dynamics auxiliary task, so the features only capture
  agent-controllable aspects of the environment).
  ([ICML PDF](https://proceedings.mlr.press/v70/pathak17a/pathak17a.pdf))
- **RND** (Burda, Edwards, Storkey, Klimov, ICLR 2019, "Exploration by Random Network
  Distillation") — intrinsic reward = prediction error of a trained network trying to match a
  *fixed, randomly initialized* target network's output on the current state. Deliberately removes
  environment dynamics from the prediction target, which is exactly what makes it robust to
  *action-dependent* stochasticity that defeats ICM.
  ([arXiv:1810.12894](https://arxiv.org/pdf/1810.12894), [OpenAI
  post](https://openai.com/index/reinforcement-learning-with-prediction-based-rewards/))
- **Count-based / hashing exploration** (Tang et al. 2017, "#Exploration: A Study of Count-Based
  Exploration for Deep RL") — discretize states via SimHash (or a learned autoencoder hash),
  bonus ∝ 1/√(count).
- **Empowerment** (Klyubin, Polani, Nehaniv 2005; Mohamed & Rezende 2015 variational formulation) —
  reward = mutual information between an agent's actions and future states, i.e., reward for being
  in states where the agent has maximal *causal control* over outcomes, independent of novelty.
- **Learning-progress-based** (Oudeyer & Kaplan, developmental robotics; Schmidhuber's "Formal
  Theory of Creativity, Fun, and Intrinsic Motivation," 1990–2010) — reward = **rate of improvement
  of a predictor/compressor**, not raw prediction error or novelty. This is the family that
  directly targets the noisy-TV problem (below).

**The noisy-TV problem is real and is exactly as fatal to naive surprisal-driven crawling as the
task description anticipates.** Formal statement (confirmed): an intrinsic-reward agent driven by
raw prediction error (ICM-style) gets stuck maximizing reward at a source of **unpredictable, not
just novel, randomness** — literal or figurative "static" — because such states are *permanently*
high-prediction-error (the model can never learn to predict noise), so the agent never "moves on."
This is a confusion between **aleatoric uncertainty** (irreducible randomness — ads, timestamps,
random-content-of-the-day widgets on a web page) and **epistemic uncertainty** (model's own
ignorance, which *is* reducible by more visits). Naive surprisal-driven crawling of a live website
will find exactly this: session-randomized ad content, live timestamps, "you may also like" widgets
with randomized ordering, CSRF tokens, and A/B-test variation are all maximally and *permanently*
surprising to a token-level or observation-level surprisal model, and a curiosity-maximizing
crawler will camp on them forever instead of mapping the site's actual navigable structure.
([noisy-TV description via multiple sources including
arXiv:2509.25438](https://arxiv.org/html/2509.25438v1))

**How it's mitigated:**
1. **RND's specific fix** — predict a fixed random network's *embedding* of the state rather than
   the actual next state/observation. Since the target function contains no information about
   environment dynamics, a stochastic environment does not inflate the prediction error over time
   the way a dynamics-prediction target does — RND's error is driven by *state novelty in feature
   space*, and (for a fixed random projection) that novelty saturates once a region of state space
   has been sufficiently visited, even if the raw pixels/content are stochastic. It doesn't fully
   solve action-conditioned noisy TVs (an agent can still "choose" to look at a stochastic channel
   repeatedly) but is markedly more robust than ICM.
2. **Learning-progress monitoring (2025/2026 work, "Beyond Noisy-TVs," arXiv:2509.25438, retrieved
   directly)** — explicitly measures **improvement of the predictor over time** rather than raw
   error: reward = (previous-iteration prediction error) − (current-iteration prediction error), so
   a permanently-unpredictable source of noise correctly converges to **zero reward** once the
   model has learned it's unpredictable (converged ~150 steps in their Noisy-MNIST test), whereas
   RND-style and AMA (explicit aleatoric-uncertainty-estimation) baselines needed far more data
   (~400+ steps) and briefly favored the noisy states before correcting, and prior baselines
   degraded badly under injected noise in MiniWorld/Atari variants (one baseline showed a "100%
   performance drop" under noise vs. LPM's 3.9%).
3. Both fixes share the same underlying principle relevant to §4 P3: **the exploration signal
   should reward the derivative of predictability (learning progress), not the level of
   surprise/error itself.**

**Implication for a surprisal-driven site crawler (the exact use case in P3/Phase 1):** a crawler
that stops/continues based on raw NLL of the next observation (as literally described in §4 P3(b)
and the Phase 1 "surprisal-vs-crawl-budget curve") **will get stuck on noisy-TV-equivalents on real
websites** — infinite-scroll feeds, randomized product carousels, live chat widgets, session/CSRF
tokens embedded in DOM state, timestamped content — all of which are permanently high-surprisal and
navigationally useless. The graph-construction crawler (Phase 1) needs either (a) a
learning-progress-style reward (surprisal *reduction rate* across repeated visits to
structurally-similar states, not raw surprisal), or (b) the type-layer abstraction from P1 doing
double duty as a de-noising step — collapsing "same page type, different random content" before
surprisal is computed at all, which is effectively RND's trick (score in an abstracted feature
space, not raw content) applied to the type layer. **This is not currently in P3's design and
should be added before Phase 1 is run**, or Phase 1's "surprisal-vs-crawl-budget saturation curve"
deliverable will likely just show non-saturation (surprisal never goes down) on any real site with
dynamic content, which would be misread as "the crawl never converges" rather than correctly
diagnosed as noisy-TV.

---

## 6. Instrumentation reality check

**Which providers expose logprobs, with what limits (verified where fetched):**
- **OpenAI Chat Completions API** — supports `logprobs: true` + `top_logprobs` (integer), returning
  the log-probability of each generated token plus up to **5** alternative tokens at each position
  per the documented parameter range found. (Community threads report the newer **Responses API
  does *not* support logprobs** as of the threads found — a real gotcha if a project defaults to
  the newer API surface.) ([community thread on Responses API logprobs
  gap](https://community.openai.com/t/why-doesnt-the-responses-api-support-logprobs/1148097),
  [OpenAI cookbook](https://cookbook.openai.com/examples/using_logprobs))
- **Anthropic Messages API** — **confirmed, by direct fetch of the current API reference, that
  there is no `logprobs` or equivalent parameter** in the documented parameter list (model,
  messages, max_tokens, system, tools, tool_choice, stop_sequences, stream, temperature, top_p,
  top_k, thinking, output_config, metadata, service_tier, cache_control, container,
  inference_geo — no logprobs field present). This means **Claude cannot be used as the "measuring
  instrument" scorer** that §4 P3 point 1 requires; P3's instruction to "use a fixed open-weights
  scorer, separate from the acting policy" is not just good practice, it is **the only option** if
  Claude (or, per the community thread, OpenAI's Responses API) is anywhere in the loop.
  ([platform.claude.com/docs/en/api/messages, fetched directly](https://platform.claude.com/docs/en/api/messages))
- **Together AI, Fireworks, and most open-weights-hosting providers** — document logprobs support
  directly (e.g. [Together AI logprobs docs](https://docs.together.ai/docs/logprobs)), generally
  modeled on the OpenAI completions-API shape.
- **Scoring a constrained candidate set (i.e., "give me P(candidate) for each of these N
  enumerated actions", which is exactly what P3(a) needs):** this is supported wherever a provider
  exposes **prompt/echo logprobs** — i.e., logprobs *of the input you supply*, not just of
  newly-generated tokens. In vLLM this is the `prompt_logprobs` parameter on `/completions`; in
  legacy OpenAI Completions this was `echo=true` + `logprobs`. Practically: construct one prompt
  per candidate action (prompt + candidate-as-continuation), request prompt-logprobs, sum the
  per-token log-probs of the candidate-continuation span. This works regardless of whether the
  provider exposes top-k *sampling* logprobs, because you are scoring a candidate you supply, not
  asking the model to enumerate its own top-k.

**Practical setup for a fixed open-weights scorer:**
- **vLLM** — most production-ready option; supports `prompt_logprobs` for exactly the
  constrained-candidate-scoring use case above. **Known gotcha, confirmed via GitHub issue:**
  `prompt_logprobs` interacts badly with **prefix caching** — cached prefix tokens' logits are not
  recomputed/stored, so a naive prompt_logprobs request over a cached prefix can silently return
  logprobs only for the newly-computed suffix tokens, not the full prompt you asked about. **If
  using vLLM as the fixed scorer with prompt caching enabled (likely, since the graph context is
  repeated across many candidate-action prompts), this must be explicitly checked/disabled or
  worked around, or the reported per-candidate NLL will be wrong.**
  ([vLLM issue #3251](https://github.com/vllm-project/vllm/issues/3251))
- **Additional documented vLLM gotcha:** decoded-token strings in `prompt_logprobs` output can
  contain raw BPE artifacts (e.g. `Ġ` instead of a literal space) rather than clean detokenized
  text — a tokenizer-effect trap if you're doing any string-matching on the logprob output rather
  than working purely with token IDs. ([vLLM issue
  #16838](https://github.com/vllm-project/vllm/issues/16838))
- **llama.cpp** — supports returning per-token logprobs from its server mode (`--logprobs` on
  `/completion`); lighter-weight than vLLM, reasonable for single-GPU or CPU scoring, less
  throughput for parallel candidate scoring than vLLM's batching.
- **HF `transformers`** — most flexible/manual: run a forward pass with `labels=input_ids`,
  read `model(**inputs).loss` (mean NLL) or manually gather log-softmax at each target token index
  for exact per-token control. No serving infrastructure, but no serving-layer gotchas either
  (no prefix-cache-vs-logprobs interaction) — arguably the *simplest correct* option for offline
  calibration experiments (Phase 0) specifically because it avoids the vLLM prefix-cache bug class
  entirely, at the cost of not being production-serving-shaped.
- **General tokenizer/BOS gotchas** (synthesized from general knowledge of these libraries'
  conventions, not from a single fetched source; treat as engineering advice rather than a
  citation): different tokenizers/model families disagree on whether a BOS token is
  auto-prepended, and whether a leading space is folded into the first real token or the BOS token
  — get this wrong and the "first token's" logprob silently measures the wrong quantity. When
  scoring the *same* candidate string across "with-graph" vs. "without-graph" (shuffled-control)
  conditions, this only matters if it differs *between* conditions — as long as the harness applies
  identical tokenization/BOS handling to both arms, the length/BOS confound cancels out; the
  danger is inconsistent handling across arms, not the BOS convention per se.

**Bottom line on instrumentation:** P3's design decision ("fixed open-weights scorer, separate from
actor") is not just methodologically clean, it is close to *forced* by the fact that Anthropic
exposes no logprobs at all and OpenAI's newer API surface is also dropping the feature — the
project cannot assume logprobs will remain available from whichever frontier model is acting, even
if it's available today from some provider.

---

## 7. Stopping rules

- **"Stop when marginal surprisal reduction falls below a threshold" is not a named, established
  criterion under that exact name** in the exploration or web-crawling literature I could find, but
  it is a direct special case of two well-established, more general frameworks:
  1. **Value-of-information / optimal-stopping theory** — the general principle that one should
     continue gathering information only while its expected marginal value (Expected Value of
     Sample Information, EVSI) exceeds its cost, and stop once it doesn't; this is the formal
     ancestor of "stop when marginal [X] falls below threshold" for essentially any X, including
     surprisal. ([Value of information in stopping problems, Lehrer & Wang,
     arXiv:2205.06583](https://arxiv.org/pdf/2205.06583); general framing via [Decision-Theoretic
     Stopping Rules for Document Screening, arXiv:2606.07071](https://arxiv.org/html/2606.07071))
  2. **Learning-progress-based exploration (§5)** — reward = marginal reduction in
     prediction/model error, and by direct extension, *stop* exploring a region once that marginal
     reduction saturates near zero. This is the same quantity P3 proposes to use as a stopping
     signal, just framed as an ongoing reward in the RL literature rather than a one-shot stopping
     rule — but the mechanism is identical, and (per §5) is specifically designed to be robust to
     the noisy-TV case where raw surprisal never saturates.
- **Coverage-based crawl stopping (web-crawling literature, directly on point):** focused/domain
  crawls are documented to use explicit stopping criteria of exactly this shape — "coverage ratio ≥
  threshold (e.g., 0.85) sustained over consecutive iterations" or "marginal discovery rate falls
  below a threshold," plus simpler practical bounds (max URLs, max size, max depth, max runtime).
  ([Coverage-Aware Web Crawling, arXiv:2602.24262](https://arxiv.org/pdf/2602.24262); general
  crawler-stopping-condition survey found via search)
- **Conclusion:** P3's proposed stopping rule is **well-grounded by analogy** (value-of-information
  theory + learning-progress exploration + coverage-based crawling all converge on "stop when
  marginal gain saturates") but should explicitly be framed as **marginal reduction in
  learning-progress-style surprisal (i.e., surprisal *reduction rate* across structurally similar
  states), not raw per-step surprisal** — for exactly the noisy-TV reason in §5. As literally
  written ("surprisal reduction falls below a threshold," §4 P3, final paragraph), it is ambiguous
  between the naive (noisy-TV-vulnerable) and the learning-progress (robust) version, and should be
  disambiguated in favor of the latter before Phase 1 is built.

---

## 8. Verdict

**(a) Is the Phase 0 calibration gate the right first experiment?**
Yes, directionally — "measure AUROC of the signal against step failure before building control
logic on it" is exactly the right discipline, and is more rigorous than most of the agent-UQ
literature surveyed here, which mostly reports whichever AUROC came out and moves on. **But the
gate as specified is measuring the wrong granularity for the intervention it's meant to license.**
§4 P3 wants to gate *within-episode* behavior ("high entropy → consult the graph... fall back...
the moment uncertainty spikes" — P2/P3(a)), but the one paper found that directly measures this
(§2, "Last Step Matters") shows **early/mid-trajectory signals are close to uninformative (AUROC
<0.60) precisely because of path-switching, and only end-of-trajectory confidence is well-calibrated
(AUROC ≈0.85).** Recommendation: **change Phase 0's deliverable from "AUROC of per-step signal →
step failure" to two separate numbers: (i) AUROC of per-step signal → *step* failure, and (ii)
AUROC of per-step signal → *eventual episode* failure, measured separately at several trajectory
percentiles (25/50/75/100%).** If (ii) collapses toward 0.5 in the middle of the trajectory the way
the cited paper found, that is the actual finding that should redirect the project — toward
episode-level gating (restart, not redirect) rather than step-level gating, which is a materially
different (and less novel-feeling, but honest) system design.

**(b) Should the primary uncertainty signal be action entropy, world-model surprisal, Bayesian
surprise, or ensemble disagreement?**
Based on the survey: **action entropy over the enumerated candidate set (P3(a)) is the right
*primary* signal to instrument first** — it is cheapest, requires no persistent belief-state
machinery, has the cleanest instrumentation story (§6), and is the one place in this whole design
where the categorical-distribution argument in §2.5/P3(a) is genuinely well-founded (entropy over a
small enumerable candidate set doesn't suffer the length confound that plagues everything else in
§1). **Ensemble/self-consistency disagreement should be run in parallel as the free secondary
signal** (no logprobs needed, and §1 shows cross-model disagreement can beat single-model entropy).
**World-model surprisal / Bayesian-surprise-over-next-observation is the most theoretically apt
signal for testing the actual hypothesis** ("does the map reduce surprise about what's behind the
link") but is also the one most vulnerable to the noisy-TV failure mode (§5) and the length/context
confound (§3) simultaneously, so it should be instrumented **third**, gated on (a) passing the
type-layer de-noising step from P1 and (b) using the matched-entropy control from §3, not the raw
shuffle. Literal Bayesian surprise (KL of a persistent belief state) is likely **not worth
building** for Phase 0/1 — no LLM-agent precedent was found, VIME-style Bayesian neural network
belief tracking is expensive and was never shown to scale past small continuous-control tasks, and
the "two forward passes, subtract" proxy P3 actually proposes is a reasonable approximation that
doesn't require it.

**(c) The single most likely way this whole idea fails, and is there a cheap test for it?**
The most likely failure mode, combining §2 and §5: **uncertainty signals that look calibrated in
an offline/static evaluation (Phase 0, scored against immediate step failure) do not remain
calibrated for the actual intended use — gating live, multi-step, backtrack-capable exploration —
because (i) agents path-switch, breaking the step→outcome causal link the gate assumes (§2), and
(ii) raw surprisal on real, dynamic websites is dominated by noisy-TV content that never
saturates, misleading both the gating logic and the "surprisal-vs-crawl-budget saturation curve"
deliverable in Phase 1 (§5).** These two failure modes compound: a crawler that both can't tell
step-level uncertainty from noise *and* can't tell early uncertainty from eventual failure has no
reliable signal left to gate on, at either the exploration stage or the execution stage.

**Cheap test, before committing to Phase 0/1 as scoped:** run a **half-day pilot** on ~10 WebArena
episodes (or even simpler, 3–5 pages of one real dynamic site) that measures, using whichever
signal is already instrumented: (1) does raw next-observation surprisal actually saturate as crawl
budget increases, or does it stay flat/high because of dynamic content (a direct, cheap check for
§5's noisy-TV prediction, answerable in an afternoon without building the full graph); and (2)
compute per-step signal AUROC against step failure **and** against final-episode outcome
separately, on whatever small logged trajectory set is easiest to get — if the episode-level number
is materially worse than the step-level number the way "Last Step Matters" found, that is the
signal to redesign toward episode-level restart-gating before investing in Phase 1's crawler.
Both checks are cheap (no graph construction, no new infra) relative to the risk of building Phase
1/2 on a gating assumption that the closest published analogue directly contradicts.

---

## Corrections to docs/01-foundations.md

> "**This is the quantity that directly tests the hypothesis:** does having the map reduce surprise
> about what is behind the link? Cleaner still: **Bayesian surprise** = KL(posterior ‖ prior) over
> next-state predictions, which is less sensitive to token-length artifacts than raw PPL." (§4 P3,
> "(b) World-model surprisal")

Correct in spirit (KL over a fixed-support distribution is less length-confounded than a joint
sequence NLL) but overstates the equivalence to Itti & Baldi's Bayesian surprise, which is defined
over an explicit, persistently-updated belief distribution over a latent world model, not two
independent forward passes with different prompts (with-graph vs. without-graph). No published
work was found applying literal Bayesian-surprise belief tracking (VIME-style) to LLM agents; treat
the "two-forward-pass KL" as a practical proxy, not a citation-backed instantiation of Itti/Baldi.
Sources: [Itti & Baldi](https://pmc.ncbi.nlm.nih.gov/articles/PMC2782645/),
[VIME](https://arxiv.org/abs/1605.09674).

> "**Three instrumentation points that decide whether this works at all:** ... 2. The length
> confound is fatal if unhandled. Conditioning on a graph adds tokens, and more context mechanically
> lowers perplexity. The **mandatory control is a shuffled/scrambled graph of identical token
> count.**" (§4 P3)

The direction (more context → mechanically lower PPL; token-count matching is necessary) is
correct and literature-backed (§3 above). But a pure token-count-matched shuffle is not sufficient
on its own: a random token shuffle typically has different (usually higher) intrinsic perplexity
than fluent-but-wrong text, which can bias the comparison. Upgrade to a control matched on **both**
token count **and** the control content's own unconditioned perplexity (a "matched-entropy
distractor"), and ideally average over multiple independent shuffles to get a null distribution
rather than a single point estimate. No single paper was found doing exactly this for LLM
in-context PPL claims; this is a synthesized methodological recommendation, not a direct citation.

> "**The most novel-feeling use, if calibration holds:** surprisal as an **exploration reward**
> (curiosity-driven crawl — the ICM/RND lineage applied to site exploration), giving a principled
> **stopping rule**: stop crawling when marginal surprisal reduction per action falls below a
> threshold." (§4 P3)

Needs one addition: raw ICM-style surprisal-as-reward is exactly the formulation known to fail via
the noisy-TV problem (§5), and real websites are full of noisy-TV-equivalent content (ads,
timestamps, randomized carousels, session tokens). The stopping rule should be defined over
**learning-progress-style marginal surprisal reduction** (compare current-iteration to
previous-iteration predictive error on structurally-similar states, à la RND/learning-progress
monitoring), not raw per-step surprisal, or Phase 1's crawler is very likely to camp on dynamic
page elements instead of mapping navigable structure. Sources:
[RND](https://arxiv.org/pdf/1810.12894), ["Beyond Noisy-TVs" learning-progress
monitoring](https://arxiv.org/html/2509.25438v1).

> "**Experiment zero:** does surprisal predict step failure? Report AUROC of surprisal → next-step
> failure. If it is ~0.55, the signal cannot gate anything and we switch to (c) or to an explicitly
> trained verifier." (§4 P3, "3. Validate calibration before building control logic on it")

Right instinct, wrong granularity for the intended use. Per §2/§8(a): even a good *step-level*
AUROC does not establish that the signal is useful for in-episode gating, because published
evidence (arXiv:2608.29685) shows step-level/early-trajectory uncertainty signals can look
informative in isolation yet fail to predict eventual episode outcome (AUROC <0.60 at 50%
progress vs. ≈0.85 at completion) due to path-switching. Experiment zero should report **both**
step-level AUROC **and** episode-outcome AUROC (measured at multiple trajectory percentiles), and
the gating decision should be conditioned on the latter, not the former alone.

---

## Design implications

**Metric definitions to instrument, in priority order:**

1. **Action entropy (primary signal).** At each step, using the fixed open-weights scorer, compute
   the categorical distribution over the enumerated layer-2 candidate action set (per §2.5 of the
   foundations doc — this is already the right design) by scoring each candidate's continuation
   log-probability (sum of per-token log-probs of the candidate string given the shared prompt
   prefix). Report both **raw entropy** H(p) and **normalized entropy** H(p)/log(N) (N = number of
   candidates that step) so the signal is comparable across steps with different candidate-set
   sizes.

2. **Episode-outcome-conditioned AUROC, not just step-conditioned AUROC (Phase 0 redesign).**
   For every logged step, compute the chosen signal (entropy, or later self-consistency
   disagreement) and record **both** (i) whether *that step* succeeded/failed and (ii) whether the
   *episode* ultimately succeeded/failed. Report AUROC against both labels, broken out by
   trajectory-progress percentile bucket (0–25/25–50/50–75/75–100%). This directly operationalizes
   §8(a)/§2's finding and is the cheapest possible correction to the existing Phase 0 design.

3. **Self-consistency / cross-model disagreement (secondary, parallel signal).** Sample k≈5
   rollouts of the next action (can reuse whatever actor is already being run), cluster by
   semantic/action equivalence, measure disagreement. No logprobs required — usable even if the
   acting model is swapped to a closed frontier API without logprob access. Track alongside entropy
   to see if the two agree (§1's evidence that ensembles/cross-model disagreement often beats
   single-model entropy-based measures).

4. **World-model surprisal, instrumented only after (1)-(2), and only with de-noising.** Define it
   as: NLL of the next-observation's **type-layer label** (per P1's two-layer graph — abstracted
   summary, not raw DOM/pixels) under the scorer, with-graph vs. shuffled-control-graph in context.
   Computing surprisal over the *type label* rather than raw observation content is the practical
   implementation of the "de-noise before scoring" recommendation in §5 — it is what keeps a
   randomized ad carousel or a live timestamp from registering as permanently high surprisal, since
   those collapse to the same type-layer label as any other unremarkable view of that page type.

5. **Shuffled-graph control, upgraded per §3/Corrections.** Token-count-matched AND
   intrinsic-perplexity-matched (compute the control graph text's own unconditioned NLL under the
   same scorer and adjust/select the shuffle until it's within a small tolerance of the real
   graph's unconditioned NLL), averaged over ≥5 independent shuffles to report a null-distribution
   band, not a single number.

6. **Stopping rule, defined as learning-progress, not raw level.** `stop when
   (mean_surprisal[window t-1] − mean_surprisal[window t]) < ε`, computed over the type-layer
   surprisal in (4), where the windows are batches of newly-crawled states of the *same inferred
   type* — not a raw "surprisal < ε" threshold, which is the noisy-TV-vulnerable version.

**Instrumentation stack:** vLLM serving one fixed open-weights model (Llama-3-class or similar) as
the sole scorer, using `prompt_logprobs` for constrained candidate-set scoring (§6). Explicitly
disable or test-around prefix caching for scoring requests (known vLLM bug interacting
`prompt_logprobs` with cached prefixes — confirm on the exact vLLM version in use before trusting
any number). Do not attempt to source logprobs from Claude (confirmed unavailable) or assume
OpenAI's Responses API will provide them (community-reported gap vs. the older Chat Completions
API) — the fixed-scorer decision in P3 point 1 is correct and, per this survey, closer to mandatory
than optional.

## Open questions

1. Does the "Last Step Matters" path-switching finding (deep-research agents) actually transfer to
   web-browsing/graph-lookup agents, where trajectories are shorter and more state-revisitable? No
   study of this exact setting was found; this is the single highest-value cheap test to run before
   committing to Phase 0's design (§8(c)).
2. Is there a published matched-entropy-distractor or permutation-test methodology for in-context
   PPL comparison specifically (as opposed to the general permutation-test literature)? Not found;
   worth a targeted search before Phase 1, since the project may end up being the first to formalize
   this for the LLM-context setting.
3. How well does the RND/learning-progress noisy-TV fix, validated on Atari/MiniWorld/MNIST-scale
   toy RL environments, actually transfer to LLM-scored, type-layer-abstracted web surprisal? No
   direct precedent found; Phase 1's design should treat this as an open empirical question, not an
   assumed transfer.
4. What is the actual magnitude of the semantic-entropy AUROC improvement over naive entropy (the
   Nature paper's own table)? Paywalled; worth a follow-up read via a library/institutional
   subscription before citing specific numbers in any external-facing writeup.
5. Given that verbalized/self-evaluation confidence outperforms raw entropy/NLL in the agent
   literature surveyed (§2), should Phase 0 also instrument a verbalized-confidence arm (prompt the
   acting model to self-report confidence) as a zero-logprob-cost baseline to compare against the
   scorer-based entropy signal, given how cheap it is to add and how strong its reported numbers
   are?
