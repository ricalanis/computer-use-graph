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
