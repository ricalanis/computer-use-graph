# Uncertainty and exploration

Sources: R3, and root checks (✓). The most technically delicate area, and where the design
changed most.

## Uncertainty signals for LLMs — calibration reality

| Signal | Behavior | Evidence |
|---|---|---|
| Raw NLL / perplexity (free text) | **Worst-behaved.** Grows ~linearly with length as an artifact | UQ surveys (2306.04459, 2002.07650) |
| Length-normalized NLL | Partial fix; tends to overcorrect toward long completions | 2505.19060 |
| Predictive entropy | Length-confounded on free text; **well-behaved over a small enumerable set** | Supports action entropy over candidates |
| Semantic entropy (Farquhar et al., Nature 2024) | Beats naive entropy and P(true) on AUROC | Exact table paywalled [unverified numbers] |
| Hidden-state probes (CCS, SAPLMA, SEP) | Good in-distribution; **AUROC 0.53–0.57 out of distribution** | 2605.09195 |
| Self-consistency | Pooled hallucination AUROC ~0.638 | 2604.17112 |
| Verbalized / self-evaluation | ~0.688 in the same aggregation; cross-model disagreement beats both | 2604.17112 |
| Conformal prediction | **Only family with coverage guarantees**; possible without logits ("API Is Enough") | 2306.10193, 2305.18404, 2403.01216 |

## Agent-specific: the finding that reshaped Phase 0

**Last Step Matters** ✓ (arXiv:2608.29685, Aug 2026), on long-horizon agents:
- Verbal confidence at trajectory completion: mean **AUROC 0.85**.
- **No signal exceeds AUROC 0.60 at 50% trajectory progress.**
- Mechanism: **path switching.** Agents abandon and later recover directions, severing the link
  between early uncertainty and the final outcome.
- The authors recommend final-step confidence for **restart** decisions over mid-course intervention.

Related work:
- **TRACER:** prefix-level failure prediction is harder than episode-level.
- **Clarification decomposition** (2606.19559): action confidence vs request uncertainty; +73% F1 on
  ALFWorld-Clarification. It is prompt-based, not logprob-based.
- **The field's direction:** verbalized and self-evaluated confidence tends to beat raw NLL for agents.

**Open transfer question:** web trajectories are shorter and more revisitable than deep-research
agents'. Does path switching bite less? Phase 0a answers it.

## The length confound and its control

- **More context mechanically lowers per-token loss.** One analysis attributes 10–60% of year-over-year
  loss reduction to context length alone (2403.05812). PPL across different context setups isn't
  comparable (RSQ, 2503.01820).
- **A token-count-matched shuffle is necessary but not sufficient.** Shuffled text has different
  intrinsic perplexity than fluent-but-wrong text, so it can bias the comparison either way.
- **Control (D8):** a distractor matched on **token count and its own unconditioned perplexity under
  the scorer**, averaged over ≥5 draws into a null band. This is synthesized from permutation-test
  methodology; no on-point paper was found.

## Bayesian surprise

- **Itti & Baldi:** surprise = KL(P(M|D) ‖ P(M)), meaning belief update rather than rarity.
- **VIME:** the RL instance (BNN information gain); expensive and never scaled beyond small control tasks.
- **In our setting:** KL between with-graph and without-graph predictive distributions over a fixed
  label set is well-defined and less length-confounded. **It is a proxy**, though: two prompts, not a
  Bayesian update of a persistent belief. No LLM-agent precedent exists. Don't build literal Bayesian
  surprise.

## Curiosity-driven exploration and the noisy TV

| Method | Intrinsic reward |
|---|---|
| ICM (Pathak 2017) | Forward-model error in learned features |
| RND (Burda 2019) | Error predicting a fixed random network; robust to dynamics noise |
| Count/hash (#Exploration) | Novelty bonus ∝ 1/√count |
| Empowerment | Mutual information between actions and future states |
| **Learning progress** (Oudeyer, Schmidhuber) | **Rate of predictor improvement** |

**The noisy TV is fatal to naive surprisal crawling.** Raw prediction error stays permanently high on
unlearnable randomness. On websites that means ads, timestamps, randomized carousels, CSRF and session
tokens, A/B variants, live widgets. A curiosity crawler camps there forever. The underlying confusion
is aleatoric uncertainty mistaken for epistemic.

**Fix:** reward the *derivative*. **Learning Progress Monitoring** ✓ (arXiv:2509.25438, ICLR 2026)
rewards model improvement, not error, and converges to zero reward on noise:
- ~150 steps on Noisy-MNIST vs 400+ for baselines (worker).
- 3.9% performance drop under noise vs a baseline's 100% (worker).

**Project design (D9):**
- Compute surprisal over **type labels**, not raw content. Abstraction does RND's de-noising.
- Stop when `mean_surprisal(window t−1) − mean_surprisal(window t) < ε`, with windows made of newly
  crawled states *of the same inferred type*.

**Stopping-rule grounding:**
- Value-of-information stopping (2205.06583).
- Coverage-based crawl stopping, e.g. coverage ≥0.85 sustained, or marginal discovery below a
  threshold (2602.24262).
- "Stop when marginal surprisal reduction < ε" is a special case of both, **provided it is learning
  progress, not level**.

## Instrumentation

- **Anthropic Messages API: no logprobs** (R3 fetched the API reference).
- **OpenAI:** Chat Completions supports `logprobs`/`top_logprobs`; the newer Responses API reportedly
  doesn't (community thread).
- **Conclusion:** a **fixed open-weights scorer separate from the actor is mandatory** (D4).
- **Candidate-set scoring:** use prompt/echo logprobs. One prompt per candidate, summing the
  candidate span's token logprobs. In vLLM that's `prompt_logprobs` on `/completions`.
- **vLLM gotchas** ✓:
  - `prompt_logprobs` + prefix caching **crashed**: #3251 (Mar 2024, RuntimeError, duplicate of #8268);
    #8268 (Sep 2024, AssertionError) **closed stale, no fix recorded**.
  - #16838: the V1 engine emits `Ġ` in `decoded_token`.
  - **Mitigation:** disable prefix caching for scoring, pin the version, run a golden-logprob
    regression (caching off vs on), and work from token IDs.
- **HF transformers** is the simplest correct option for offline Phase 0 (no serving-layer bugs).
  llama.cpp returns logprobs from server mode.
- **BOS / leading-space handling** must be *identical across arms*; it only confounds if it differs.

## Signal build order (D8)

1. **Normalized action entropy** H(p)/log N over the actionability-filtered candidate set. Primary.
2. **Verbalized confidence.** Free; strongest end-of-trajectory signal; the baseline to beat.
3. **Sampling disagreement** (k≈5, clustered by action equivalence). No logprobs needed.
4. **Type-label world-model surprisal** with the matched-PPL distractor control. Build it last.

**Calibration gate:** report AUROC against **step failure** *and* **episode failure** by progress
bucket (0–25/25–50/50–75/75–100%). Pre-registered rule:
- Episode AUROC ≥0.70 by the 50% bucket → step gating.
- Informative only in the last bucket → episode restart gating.
- Neither → binary verifier.
