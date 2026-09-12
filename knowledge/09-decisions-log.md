# Decisions log

One entry per design decision. **Status:** `Decided` (settled; reopen only with new evidence) ·
`Proposed` (recommended in design v0.2; not yet confirmed by the operator) · `Open` (needs an
operator call or data). Add a new entry rather than editing history; mark superseded entries.

| ID | Decision | Status | Date | Rationale | Sources |
|---|---|---|---|---|---|
| D1 | **Clean-room public project.** No employer-internal technology, data, or unreleased work informs anything; public citations only. | Decided (operator) | 2026-09-12 | IP protection, stated by the operator | `dev_public/CLAUDE.md` |
| D2 | **Agent action space = layer 2** (element-targeted over an actionability-filtered a11y candidate set), executed by Playwright via BrowserGym. Pixel agents are future work. | Decided | 2026-09-12 | Categorical entropy needs an enumerable set; pixel grounding error (ScreenSpot) would swamp the signal | Note 02; R0 §7 |
| D3 | **Reads may use layer 6** (page's own XHR responses, declared, also given to baselines). **No layer-6 writes or request forging.** | Decided | 2026-09-12 | Write-side fragility, ToS, non-transferable results | Note 02 |
| D4 | **Fixed open-weights scorer separate from the actor.** vLLM with prefix caching disabled + golden regression, or HF transformers offline. | Decided | 2026-09-12 | Forced: no Anthropic logprobs; vLLM crash ✓ | Note 06; F11 |
| D5 | **Two-layer graph.** Node key = (URL template, stripped DOM-skeleton hash); embedding for merges only; clustered type layer; **hidden state as episode context gating edge preconditions**. | Proposed | 2026-09-12 | Crawljax/WebEmbed prior art; avoids node explosion; type layer untested | Note 04; R1 |
| D6 | **HIGH-risk edges excluded from exploration;** executable only when a task targets them, after first-traversal confirmation. | Proposed | 2026-09-12 | WebGuard 76% HIGH recall ✓ is a gate, not a safeguard | Note 04; F12 |
| D7 | **Tool API:** `search(k=5)`, single-hop `neighbors`, pre-computed `path` or `None`, `execute_macro` with per-step termination check and resume-from-step-*i*, `landmarks`, `record`; token-capped returns. | Proposed | 2026-09-12 | GraphWalk (multi-hop flails); Context Rot (distractors); convergent replay architecture | Note 05; R2 |
| D8 | **Uncertainty gating is the experiment, not the default.** Signal order: action entropy → verbalized → disagreement → type-label surprisal. Granularity chosen by a pre-registered rule on step vs episode AUROC. | Proposed | 2026-09-12 | Last Step Matters ✓ | Note 06; F4 |
| D9 | **Crawl stopping rule = learning progress** over same-type windows of type-label surprisal. | Proposed | 2026-09-12 | Noisy TV; LPM ✓ | Note 06; F5 |
| D10 | **Eight arms; primary contrast 4 vs 2;** hard identical tool-call and token budgets; byte-identical non-tool prompts; arms frozen before eval. | Proposed | 2026-09-12 | Confound audit; Environment Maps budget disparity | Note 07; R5 |
| D11 | **Arms 2 and 4 use the same source data;** crawler is task-agnostic, so every task is held out by construction. | Proposed | 2026-09-12 | Isolates structure; cheap firewall | Note 07 |
| D12 | **Primary benchmark: WebArena GitLab + CMS (362 tasks, corrected labels); WorkArena L1 as replication** (template-level analysis). | Proposed — **conflicts with R4**, which recommends WorkArena primary | 2026-09-12 | Independence (33 templates), reproducibility (hosted pool ✓), and site-level evidence ✓ | Note 03; F13 |
| D13 | **Statistics:** exact McNemar primary + task-random-intercept mixed model; Cochran's Q + BH-FDR secondary; paired bootstrap; Wilson CIs; seeds as repeated measures; size Phase 2 from pilot ψ. | Proposed | 2026-09-12 | Note 07 ✓ tables | Note 07 |
| D14 | **Kill tests before infrastructure:** Phase 0a noisy-TV saturation + step-vs-episode AUROC; Phase 0b arm 1 vs arm 2 pilot with a pre-registered proceed rule. | Proposed | 2026-09-12 | Cheapest falsification of F2/F4/F5 risks | Design v0.2 §8 |
| D15 | **Reproduce Environment Maps' GitLab numbers** (8.3 / 11.7 / 22.8) before any novel arm, with a pre-set tolerance. | Proposed | 2026-09-12 | Anchors the harness to a published result | Design v0.2 §9 |
| D16 | **Report amortization as dual crossover** (cost N and significance N) with USD primary axis. | Proposed | 2026-09-12 | Not standard practice; overclaiming risk | Note 07; F8 |
| O1 | Primary benchmark: WebArena GitLab + CMS vs WorkArena (see D12). | **Open** | — | Operator's call | — |
| O2 | Deliverable shape: paper vs working system. Decides whether the calibration gate is binding. | **Open** | — | — | — |
| O3 | Which open-weights scorer model, and its size relative to the actor. | **Open** | — | — | — |
| O4 | Is a ~76%-recall risk gate + first-traversal confirmation acceptable for unattended exploration, or is a human always in the loop for LOW/HIGH edges? | **Open** | — | Policy call | Note 04 |
