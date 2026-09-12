# Open questions

Consolidated from all dossiers and the synthesis. **Priority:** P1 = blocks or could invalidate the
plan; P2 = shapes the design; P3 = citation hygiene. **Resolved by** names the phase or action.

## P1 — could invalidate the plan

| # | Question | Resolved by | Origin |
|---|---|---|---|
| Q1 | Does **path switching** transfer to web agents? Is episode-outcome AUROC informative before the last bucket? | Phase 0a/0b | R3, F4 |
| Q2 | Does **type-label surprisal saturate** on a real dynamic site, or does the noisy TV survive abstraction? | Phase 0a | R3, F5 |
| Q3 | On WebArena, does **graph beat token-matched flat retrieval** with controlled budgets? No paper has run it. | Phase 0b → 2 | R2 addendum, F2 |
| Q4 | Does the **type layer compress and transfer** across sites? | Phase 3 | R1 |
| Q5 | Is a **~76%-recall risk classifier** an acceptable exploration gate? | Operator policy (O4) | R1 |

## P2 — shapes the design

| # | Question | Resolved by | Origin |
|---|---|---|---|
| Q6 | Right **structural-fingerprint granularity**? The fine-vs-coarse tradeoff has no universal winner. | Phase 1 tuning | R1 |
| Q7 | Should novelty detection (crawl) and node lookup (task) use **different abstraction functions**? A coarse one suppresses surprisal and confounds P3. | Phase 1 design | R1 |
| Q8 | Can hidden-state factors be **enumerated in advance** (wizard steps, A/B buckets, flags)? | Phase 1 | R1 |
| Q9 | Optimal **token budget per tool return**? | Phase 1–2 ablation | R2 |
| Q10 | Does **actionability filtering** change entropy calibration? | Phase 0a | R0 |
| Q11 | Is a **layer-1 vs layer-2** (`coord` vs `bid`) entropy ablation worth running? It's a config change. | Phase 0 optional | R0 |
| Q12 | Does WorkArena's 100%-precision validator generalize, or is it an artifact of ServiceNow's structured records? | Phase 2r | R4 |
| Q13 | Does the variance decomposition (agent main effect <3%) hold on WebArena? | Pilot data | R5 |
| Q14 | Is there a published **matched-entropy distractor / permutation-test** method for in-context PPL? | Literature search | R3 |
| Q15 | Do RND/learning-progress fixes transfer from toy RL to **LLM-scored web surprisal**? | Phase 1 | R3 |
| Q16 | Should Phase 0 include a **verbalized-confidence arm**? Recommended: yes. | Decided in design (D8) | R3 |
| Q17 | Is there an **iso-cost leaderboard** for WebArena-style agents? | Literature search | R5 |
| Q18 | Real **cost-per-step** and **pruned-tree token counts** for the chosen models and sites? | Phase 0b measurement | R0 |
| Q19 | Environment Maps per-site numbers came from the paper's text (figure only); E-Commerce not stated. | Read Figure 2b / contact authors | Root |

## P3 — citation hygiene (verify before citing externally)

| # | Item | Origin |
|---|---|---|
| Q20 | VisualWebBench, BrowserART, ScreenSpot-v2 authorship, WebChoreArena, OpenApps/TimeWarp, WASP authors | R4 |
| Q21 | AWM full text: any flat baseline (none found) and any cost accounting? | R2, R5 |
| Q22 | RAGSearch HotpotQA variance direction (inconsistent in the fetched summary) | R5 |
| Q23 | Semantic entropy exact AUROC table (Nature, paywalled) | R3 |
| Q24 | Prior art for reading **XHR responses as observations** (academic search found none; try harness READMEs and blogs) | R0 |
| Q25 | Do bot-detection systems check `isTrusted`? Only matters for the live-web appendix. | R0 |
| Q26 | Synapse OpenReview cross-check (rate-limited) | R2 |
| Q27 | Worker-only numbers used in design docs: AgentRewardBench Table 1 values; Environment Maps tool-call counts; Surfer 2 71/812; OSWorld-Verified 300+; WebJudge 85.7%; LPM step counts | Root log |
