# Verification log — root spot-checks of worker dossiers

Workers were told to cite only sources they retrieved. The root session independently re-fetched
the claims that would change the design if wrong. Everything below was fetched by root on
2026-09-12. Anything not listed here rests on the worker's own retrieval only.

## Verified

| Claim (worker) | Source fetched | Result |
|---|---|---|
| Early/step-level uncertainty cannot predict long-horizon agent failure; AUROC <0.60 at 50% progress vs 0.85 verbal confidence at completion; mechanism = path switching (R3) | [arXiv:2608.29685](https://arxiv.org/abs/2608.29685) — *Last Step Matters: Early Uncertainty Cannot Predict Failure in Long-Horizon Agents*, Li et al., 30 Aug 2026 | **Confirmed verbatim.** Paper also recommends final-step confidence for *restart* decisions over intermediate intervention. |
| Learning-progress (error reduction) as a noisy-TV-robust intrinsic reward (R3) | [arXiv:2509.25438](https://arxiv.org/abs/2509.25438) — *Beyond Noisy-TVs: Noise-Robust Exploration Via Learning Progress Monitoring*, Hou, An, Du; ICLR 2026 | **Confirmed.** |
| GraphRAG global search underperforms plain RAG on reference-based metrics; LLM-judge position bias inflated earlier wins (R2) | [arXiv:2502.11371](https://arxiv.org/html/2502.11371) | **Confirmed.** QMSum ROUGE-2 F1: RAG 6.32 vs Community-GraphRAG (Global) 3.23; SQuALITY 10.08 vs 6.99. Position bias "leads to substantially different, and in some cases opposite, judgments." |
| WebGuard fine-tuned classifier ≈80% accuracy / ≈76% HIGH-risk recall (R1) | [arXiv:2507.14293](https://arxiv.org/abs/2507.14293) — *WebGuard: Building a Generalizable Guardrail for Web Agents*, Zheng et al., Jul 2025 | **Confirmed.** Frontier LLMs <60% accuracy and <60% HIGH-risk recall; fine-tuning 37%→80% accuracy, 20%→76% HIGH recall. |
| An existing paper already ran graph-vs-flat-vs-none on WebArena (R5) | [arXiv:2603.23610](https://arxiv.org/html/2603.23610) — *Environment Maps: Structured Environmental Representations for Long-Horizon Agents*, Feng, Sharma, Maamari, Mar 2026 | **Confirmed.** See details below. |
| WILBUR ablation: flat embedding-retrieved demonstrations vs learned ranker (R2 addendum) | [ar5iv 2404.05902](https://ar5iv.labs.arxiv.org/html/2404.05902) — *WILBUR: Adaptive In-Context Learning for Robust and Accurate Web Agents*, Lutz et al., Apr 2024, Table 1 (WebVoyager) | **Confirmed.** Zero-shot 34.4 · ++Backtrack 40.6 · ++Demonstrations 48.4 · ++Synthesis 49.9 · WILBUR 52.6. Flat retrieval (+7.8) is ~65% of the 12.0pp memory gain over ++Backtrack. |
| BrowserGym exposes rung as a config knob via `ACTION_SUBSETS` with `bid` and `coord` subsets (R0) | [BrowserGym `action/highlevel.py`](https://raw.githubusercontent.com/ServiceNow/BrowserGym/main/browsergym/core/src/browsergym/core/action/highlevel.py) | **Confirmed.** `bid`: scroll, fill, select_option, click, dblclick, hover, press, focus, clear, drag_and_drop, upload_file. `coord`: scroll_at, mouse_*, keyboard_*. Also has per-benchmark subsets incl. `webarena`, `workarena`, `workarena++`, `assistantbench`. |
| McNemar sample sizes for a 10pp paired effect (R4 §7) | Root recomputed (Connor 1987 approximation, α=.05 two-sided, power .80) | **Confirmed.** Discordance ψ=0.15 → 116 tasks · 0.20 → 155 · 0.25 → 194 · 0.30 → 234 · 0.40 → 312. Matches R4 within rounding. |
| Wilson 95% CI half-width ≈13.4pp at n=50, p=0.5 (R4 §5) | Root recomputed | **Confirmed.** Full width 26.7pp at n=50 and p=0.5; 21.8pp at p=0.2. |
| WorkArena has 33 L1 tasks; WorkArena++ has 682 tasks, both on ServiceNow (R4) | arXiv API: [2403.07718](https://arxiv.org/abs/2403.07718), [2407.05291](https://arxiv.org/abs/2407.05291) | **Confirmed**, plus [WorkArena README](https://github.com/ServiceNow/WorkArena): "WorkArena-L1 includes `19,912` unique instances drawn from `33` tasks." Instances are reached through a hosted pool with Hugging Face authentication, not a self-hosted container. |
| Rule-based benchmark evaluators under-report web-agent success (R4 §6) | [arXiv:2504.08942](https://arxiv.org/abs/2504.08942) — *AgentRewardBench*, Lù et al., abstract | **Direction confirmed:** "rule-based evaluation used by common benchmarks tends to underreport the success rate." R4's exact Table 1 numbers (precision 83.8 / recall 55.9) are *not* root-verified. |

### Environment Maps — details root confirmed

- WebArena, 812 tasks, 5 environments; Claude Agent SDK on claude-sonnet-4-5 with Read/Grep/Glob/Bash.
- Overall: no map **14.2%** [11.9, 16.7] · raw trajectory access **23.3%** [20.5, 26.3] · environment map **28.2%** [25.2, 31.4].
- Map built from **179 human recordings** (19–45 per environment) from WebArena's released trajectory set; $1–4 and 13–31 min per environment. **Not built by autonomous exploration.**
- Per-site (from text; E-Commerce not stated): Reddit 13.2 → 58.5 → 60.4 · GitLab 8.3 → 11.7 → 22.8 · CMS 11.5 → 15.4 → 22.5 · Map 32.1 → 34.9 → 34.9.
- Multi-site tasks: baseline 1/48; trajectories and map 0/48.
- **Contamination not ruled out.** Human trajectories cover ~22% of WebArena tasks; the paper does not state those tasks were excluded from the 812 evaluated. It partitions results by trace-covered vs not, but reports no held-out firewall.

## Corrections root made to worker dossiers

- **R5 §7 arithmetic.** R5 writes "a 9.1pp graph benefit but a much larger 9.1pp-out-of-14pp share
  already captured by flat access." The structure-over-flat benefit is **28.2 − 23.3 = 4.9pp**;
  flat access captured **9.1pp of the 14.0pp** total gain (65%). R5's conclusion stands and is
  stronger with the correct number.

- **R3 §6 vLLM characterization.** R3 says cached-prefix `prompt_logprobs` "can silently go
  missing." The issues it cites show something different. [#3251](https://github.com/vllm-project/vllm/issues/3251)
  (Mar 2024) is a *hard RuntimeError* (logits size mismatch), closed as a duplicate of
  [#8268](https://github.com/vllm-project/vllm/issues/8268) (Sep 2024, AssertionError), which was
  **closed as stale / not planned, with no fix recorded.** [#16838](https://github.com/vllm-project/vllm/issues/16838)
  is unrelated to prefix caching (V1 engine returns `Ġ` in `decoded_token`). Practical upshot is the
  same or stronger: disable prefix caching for scoring requests, pin the vLLM version, and run a
  golden-logprob regression test (score a fixed prompt with caching off vs on) before trusting any
  number. Also normalize `decoded_token` rather than relying on its surface form.

## Observation root drew from the verified numbers

Structure's marginal value over flat trajectories is **not uniform across sites**: ~0 on Map
(34.9 → 34.9) and Reddit (58.5 → 60.4), but large on GitLab (11.7 → 22.8) and CMS (15.4 → 22.5) —
the configuration/admin-heavy sites. This is consistent with the foundations doc's archetype
hypothesis (§1.5) that authoring/configuration tasks are the most graph-shaped, and it argues for
choosing a configuration-heavy site for Phase 1–2.

**Flat memory captures roughly two-thirds of the memory win, in three independent results.**
Environment Maps (WebArena): flat trajectory access is 9.1 of the 14.0pp gain (65%). WILBUR
(WebVoyager): flat demonstrations are 7.8 of 12.0pp (65%). ExpeL (per R2 addendum, *not
root-verified*): flat retrieve-only matches or beats structured on WebShop and ALFWorld. Condition 2
in P4 is therefore a strong competitor, not a strawman, and the primary contrast must be
graph-vs-flat.

**The unit of independence in WorkArena L1 is the task template, not the instance.** R4 counts
WorkArena's 33 L1 tasks as thousands of instances. But instances of one template share their
navigation path, so they are not independent observations for McNemar, and a graph that has seen
one instance has in effect seen them all. Any use of WorkArena needs (a) template-level clustering
in the analysis (task-template random effect) and (b) a crawl/eval firewall split by template, not
instance. R4 did not flag either.

## Not independently re-checked by root

All other citations, including: R1's Crawljax /
WebEmbed "56% F1" figure and the arXiv:2606.16650 survey; R2's Muscle-Mem / PreAct / Agentic
Compilation / SkillDroid convergence and GraphWalk; R0's Playwright issue #39955; R2 addendum's ExpeL, AWM, Synapse and SkillWeaver
baseline readings; R5's claimed 12× tool-call disparity in Environment Maps; R4's Surfer 2 "71/812 corrected
tasks" (arXiv:2510.19949), OSWorld-Verified "300+ issues", Online-Mind2Web WebJudge 85.7%
agreement, and AgentRewardBench Table 1 values. Re-verify any of these before citing externally.
