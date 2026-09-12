# Key findings

The findings that changed the design, each with evidence strength and consequence.
✓ = root-verified. Ordered by impact on the project.

| # | Finding | Evidence | Consequence |
|---|---|---|---|
| F1 | **Graph vs flat vs none has already been run on WebArena:** 14.2 → 23.3 → 28.2 | Environment Maps ✓ (2603.23610) | "Graph beats naive" isn't a contribution. Novelty moves to autonomous exploration, a held-out firewall, amortized cost, gating, and transfer. |
| F2 | **Flat memory takes ~2/3 of the memory win** wherever a flat baseline exists | Environment Maps 9.1/14.0 ✓; WILBUR 7.8/12.0 ✓; ExpeL flat ≥ structured | The primary contrast is graph vs flat (arm 4 vs 2). Arm 2 must be strong. |
| F3 | **Structure's marginal value is site-dependent:** ~0 on Map and Reddit; +11.1pp GitLab, +7.1pp CMS | Environment Maps per-site ✓; RAGSearch multi-hop vs general | Target configuration-heavy sites (D12). |
| F4 | **Early uncertainty doesn't predict long-horizon failure:** no signal >0.60 AUROC at 50% progress; 0.85 at completion; path switching | Last Step Matters ✓ (2608.29685) | Phase 0 reports step *and* episode AUROC by progress bucket. Restart gating is a first-class alternative (D8). |
| F5 | **Noisy TV defeats raw-surprisal crawling;** learning progress fixes it | RND; LPM ✓ (2509.25438) | Stopping rule = learning progress over type-label surprisal (D9). |
| F6 | **Replay + per-step check + resume-from-failure is established;** all four systems gate on binary divergence | Muscle-Mem, PreAct, Agentic Compilation, SkillDroid | The architecture isn't novel. A continuous gate is unclaimed but conditional on F4. |
| F7 | **Environment Maps' map arm used ~10× more tool calls** than the flat arm, with no held-out statement | Tool calls (worker); held-out absence ✓ | Hard shared budgets; task-agnostic crawler as firewall (D10, D11). |
| F8 | **Nobody plots the amortization crossover** | Environment Maps, RAGSearch report halves | Dual crossover (cost and significance) is a methodological contribution (note 07). |
| F9 | **Validators under-credit; LLM judges over-credit** | AgentRewardBench direction ✓ | Human-labeled subset per site; validator recall checked per arm. |
| F10 | **≥50 tasks is underpowered 2–6×** for a 10pp paired effect | McNemar recomputed ✓ | Phase 2 on all 362 GitLab + CMS tasks; 50 only for calibration. |
| F11 | **No logprobs from Anthropic, reportedly none from OpenAI Responses;** vLLM `prompt_logprobs` + prefix caching crashed and was never fixed | R3 API fetch; vLLM #3251/#8268 ✓ | Fixed open-weights scorer; caching off; golden regression (D4). |
| F12 | **Best destructive-action classifier reaches 76% HIGH-risk recall** | WebGuard ✓ (2507.14293) | HIGH-risk edges excluded from exploration (D6). |
| F13 | **WorkArena's 19,912 instances are 33 templates on a hosted pool** | WorkArena README ✓ | Replication site, not primary; template-level analysis (D12). |
| F14 | **The two-layer type/instance affordance graph is unpublished;** web testing (Crawljax, WebEmbed, Judge) solved parts of state identity | R1 | Reuse abstraction-function prior art; validate the type layer on the downstream task. |
| F15 | **Per-site maps don't transfer:** multi-site 0/48 in every arm | Environment Maps ✓ | Pre-register the Phase 3 transfer criterion; expect a null. |
| F16 | **GraphRAG's headline win came from biased LLM judges** | 2502.11371 ✓ | Cite the mechanism, never the headline number. |
| F17 | **Rung is a harness config**, not a stack property | BrowserGym `ACTION_SUBSETS` ✓ | Layer-1 vs layer-2 entropy ablation is a config change. |
| F18 | **Options/semi-MDP vocabulary is absent** from GUI/web literature | R0 search | Present it as a formal import. |
| F19 | **A11y trees include unreachable elements** | Playwright #39955 | Filter for actionability before computing entropy. |
| F20 | **Research summarizers fabricate numbers** | R4 incident (AgentRewardBench) | Read tables directly; root spot-checks stay mandatory. |

## Key papers

The load-bearing sources. ✓ = root-verified (see `../research/00-verification-log.md`); full list
with statuses in [`../bibliography/references.md`](../bibliography/references.md).

**The experiment's direct lineage:**

| Paper | Why it's load-bearing |
|---|---|
| [Environment Maps: Structured Environmental Representations for Long-Horizon Agents](https://arxiv.org/abs/2603.23610) ✓ | The closest prior work. Ran no-map / trajectories / map on WebArena (14.2 → 23.3 → 28.2). Our micro run replicates its arm structure and ordering; our design answers its gaps (autonomous exploration, firewall, amortized cost). |
| [Last Step Matters: Early Uncertainty Cannot Predict Failure in Long-Horizon Agents](https://arxiv.org/abs/2608.29685) ✓ | Killed v0.1's step-level gating. AUROC ≤0.60 at 50% progress vs 0.85 at completion; path switching. Drives the §6.3 two-label calibration gate and restart gating (D8). Our micro run reproduced the dead verbalized-confidence signal (AUROC ~0.49). |
| [Beyond Noisy-TVs: Noise-Robust Exploration Via Learning Progress Monitoring](https://arxiv.org/abs/2509.25438) ✓ | The crawl stopping rule (D9): reward learning progress, not surprisal level, over type-abstracted states. |
| [WebGuard: Building a Generalizable Guardrail for Web Agents](https://arxiv.org/abs/2507.14293) ✓ | Best published destructive-action classifier (76% HIGH-risk recall) — a gate, not a safeguard. Drives D6 (HIGH-risk edges excluded from exploration). |
| [WILBUR: Adaptive In-Context Learning for Robust and Accurate Web Agents](https://arxiv.org/abs/2404.05902) ✓ | Second independent flat-takes-~2/3 data point (7.8 of 12.0pp), with live backtracking. |

**The methodology spine:**

| Paper | Why it's load-bearing |
|---|---|
| [WebArena](https://arxiv.org/abs/2307.13854) | The primary benchmark environment (GitLab + CMS arms, 362 tasks). |
| [Surfer 2 (WebArena label corrections)](https://arxiv.org/abs/2510.19949) | 71/812 labels corrected; part of recent SOTA is evaluation change. We use corrected labels. |
| [AgentRewardBench](https://arxiv.org/abs/2504.08942) ✓ (direction) | Validators under-credit, judges over-credit — opposite biases. Drives the per-arm validator recall check (F9). |
| [A Practical Playbook for Defensible Results](https://arxiv.org/abs/2605.00428) | The BH-FDR secondary-analysis plan (D13). |
| [Reproducibility audit of LLM-agent benchmark papers](https://arxiv.org/abs/2605.21404) | Mean disclosure score 0.38, none reported cost, none pinned digests — the disclosure schema we follow per run. |
| [Scaling LLM Test-Time Compute Optimally](https://arxiv.org/abs/2408.03314) | The iso-cost view: sweep budget B, report success(arm \| cost ≤ B). Credits adaptive spend. |

## Most promising papers for next work

Ranked by expected value for the phases ahead. Status marks apply as above.

| Paper | Why it's next |
|---|---|
| [NNetNav](https://arxiv.org/abs/2410.02907) | The exploration policy prior art for Phase 1's crawler (persona-seeded exploration + trajectory relabeling). Direct input to the crawl policy design. |
| [Agent Workflow Memory](https://arxiv.org/abs/2409.07429) | Flat NL workflow induction — the strongest arm-2/2a competitor design and the P2 context-mode baseline. Its flat-baseline gap (Q21) is still unresolved. |
| [WALT: Web Agents that Learn Tools](https://arxiv.org/abs/2510.01524) | Best-on-5/6-domains learned-tool result; the macro-mode efficiency design to beat or borrow for arm 4. |
| [ExpeL](https://arxiv.org/abs/2308.10144) | The cleanest published flat-vs-structured ablation (retrieve-only vs insights) — the arm-2 design template, and the evidence flat can beat structured. |
| [Synapse](https://arxiv.org/abs/2306.07863) | Trajectory-as-exemplar retrieval by state abstraction — the embedding-retrieval mechanism for arm 2. |
| [LASER](https://arxiv.org/abs/2309.08172) | Hand-authored abstract states + state-specific actions on WebShop — the oracle-graph (arm 7) design template. |
| [Semantic Entropy Probes](https://arxiv.org/abs/2406.15927) | Hidden-state uncertainty without logprobs — the fallback if the D4 scorer's AUROC disappoints in Phase 0b. |
| [API Is Enough: Conformal Prediction for LLMs Without Logit Access](https://arxiv.org/abs/2403.01216) | Coverage-guaranteed uncertainty from samples alone — the only signal family with distribution-free guarantees; candidate for the gate's threshold calibration. |
| [TRACER](https://arxiv.org/abs/2602.11409) | Prefix-level vs episode-level risk aggregation — directly informs the §6.3 step-vs-episode decision. |
| [Agentic Compilation](https://arxiv.org/abs/2604.09718) · [PreAct](https://arxiv.org/abs/2606.17929) · [SkillDroid](https://arxiv.org/abs/2604.14872) · [Muscle-Mem](https://github.com/pig-dot-dev/muscle-mem) | The four convergent replay systems (F6): cache → per-step check → resume-from-failure, all binary-gated. The architecture to match; the continuous gate is the unclaimed seam. |
| [Go-Explore](https://arxiv.org/abs/1901.10995) / [Intelligent Go-Explore](https://arxiv.org/abs/2405.15143) | Archive-based exploration; requires the resettable simulator WebArena provides. Candidate exploration policy upgrade if random-walk + learning-progress under-covers in Phase 1. |
| [RAG vs. GraphRAG](https://arxiv.org/abs/2502.11371) ✓ | The cautionary citation: GraphRAG's headline win was judge bias; global search underperformed plain RAG. Cite mechanisms, never headline numbers. |

## Corrections to our own earlier claims

- "5–10× fewer steps" from macro replay — **unsourced**; measure it.
- "~50× cost across rungs" — **unsourced**; measure it.
- "100k+ token a11y trees" — **unsourced**; measure it.
- "Shuffled graph is the control" — **insufficient**; match perplexity too.
- "Bayesian surprise = KL over two prompts" — **a proxy**, not Itti & Baldi.
- "NNetNav, AWM, skill induction are graph prior art" — **wrong**; none builds a graph.
- "±13pp at n=50" — **right only as the worst case**.
- "≥50 tasks/condition" — **underpowered**.
- R5's "9.1pp graph benefit" — **it's 4.9pp** over flat.
- R3's "logprobs silently missing" — **it's a crash** (#3251/#8268).
