# Benchmarks and evaluation

Sources: R4, R5 §6, and root spot-checks (✓). Almost every benchmark named in v0.1 exists;
exceptions are listed at the bottom.

## Landscape

**Offline / action-matching** (no execution; measures imitation, under-credits alternative correct paths)

| Benchmark | Size |
|---|---|
| Mind2Web (NeurIPS'23) | >2,000 tasks, 137 sites |
| WebLINX (ICML'24, conversational) | ~2,300 demos |
| AITW (NeurIPS'23) | 715K episodes |
| GUI-Odyssey | 8,334 cross-app mobile episodes |

**Online, deterministic, self-hosted** (the only tier for causal claims)

| Benchmark | Size | Validator | License |
|---|---|---|---|
| WebArena | 812 tasks, 6 sites; per site: E-Commerce 187 · **CMS 182 · GitLab 180** · Map 109 · Reddit 106 ✓ | Hybrid: URL, HTML state, fuzzy/exact string, LLM | Apache-2.0 |
| WebArena-Lite | 165 curated tasks | Cleaned hybrid | Apache-2.0 |
| WebArena Verified | Audited; 258-task "Hard" subset keeps rankings at 68.2% lower cost | Repaired evaluators; Wilson CIs | — |
| VisualWebArena | 910 tasks, adds Classifieds | Hybrid | Apache-2.0 |
| **WorkArena L1** ✓ | **33 templates → 19,912 instances**, one ServiceNow instance | Programmatic record/UI state | Apache-2.0 |
| **WorkArena++** ✓ | 682 compositional tasks | Programmatic | Apache-2.0 |
| TheAgentCompany | 175 tasks across GitLab/Plane/ownCloud/RocketChat | Checkpoints + 50% full-completion bonus | MIT |
| MiniWoB++ | ~100–125 toy templates | Exact | MIT |
| WebShop | 1 synthetic site, 12,087 instructions | Attribute match | CC BY 4.0 |

**Online, live web** (drifts; appendix only)

| Benchmark | Notes |
|---|---|
| WebVoyager | 643 tasks, 15 sites, GPT-4V judge |
| Online-Mind2Web | "An Illusion of Progress?" |
| AssistantBench | 214 tasks |
| WebCanvas / Mind2Web-Live | ~542 tasks, 2,439 key-node states |
| GAIA | 466 tasks, partly browsing |

**OS / desktop / mobile**

| Benchmark | Notes |
|---|---|
| OSWorld | 369 tasks, 134 checker functions, CC BY-SA 4.0 |
| OSWorld-Verified | 300+ issues fixed |
| WindowsAgentArena | 150+ tasks |
| AndroidWorld | 116 tasks; near-saturation claims by 2026 |

**Component:** ScreenSpot (1,272 pairs), ScreenSpot-Pro (1,581 pairs, 23 pro apps, SOTA <60%), AgentRewardBench.
**Safety:** AgentDojo, WASP, ST-WebAgentBench (375 tasks, Completion-under-Policy).

## Known problems

- **WebArena labels:** a manual audit corrected **71/812 tasks (≈8.7%)**, and a 5-judge GPT-4.1
  ensemble replaced the single judge (Surfer 2). Part of recent SOTA gains is evaluation change.
- **Leaderboard numbers aren't comparable:** 74.3% (Steel.dev), 71.6% (OpAgent), and 69.6% (Surfer 2)
  use different judges and harnesses.
- **OSWorld-Verified:** 300+ fixes, including overly narrow ground truth that rejects valid paths.
- **Validators and judges fail in opposite directions:**
  - **Rule-based validators under-credit** ✓ ("tends to underreport the success rate"). AgentRewardBench
    reports precision 83.8 / recall 55.9 / F1 67.1.
  - GPT-4o scores 16.7pp lower on WebArena under rule-based scoring than under expert labels.
  - **LLM judges over-credit:** none exceeds 70% precision.
  - Human inter-annotator agreement is 89.3%.
  - WorkArena's validator hit 100% precision, the one clean exception.
- **Illusion of progress:** ~90% on WebVoyager drops to 30% (Browser Use) and 61% (Operator) on
  Online-Mind2Web. Their WebJudge (o4-mini) reports 85.7% human agreement.
- **Summarizers fabricate numbers.** R4's first WebFetch summary of AgentRewardBench invented plausible
  agreement figures; reading the PDF caught it. Read tables directly.
- Contamination: no WebArena/WorkArena-specific study found [unverified].

## Choosing a benchmark for this project

Requirements: deterministic and self-hostable · DOM/a11y · **many tasks per site** · programmatic
validator · permissive license.

| Option | For | Against |
|---|---|---|
| **WebArena GitLab + CMS (recommended primary)** | 362 tasks; structure beat flat memory exactly here ✓; Docker-reproducible; can anchor against Environment Maps | Hybrid validators; must use corrected labels |
| **WorkArena L1 (recommended replication; R4's primary)** | One site; routine-repeat regime; clean validator | **Effective n is 33 templates**, not 19,912 (instances share paths); **hosted instance pool behind Hugging Face auth** ✓, not self-hosted; proprietary platform |
| WorkArena++ | Compositional on the same instance | Heavy, long-horizon (33.8 steps/episode) |
| WebShop | Cheap tool-API pilot | One task type; not evidence |

## Harness: BrowserGym + AgentLab

- **Status:** maintained (PyPI 0.14.3, Jan 2026), Apache-2.0.
- **Observations:** HTML, AXTree, screenshot, set-of-marks.
- **Tooling:** AgentLab adds Ray parallelism and a trace viewer.
- **Extension:** a custom `action_mapping` exposes the graph tools.
- **Gap:** no built-in per-step logprob or candidate-set logging; build it and thread it through
  agent-info fields.
- **Cost reference** (Claude 3.5 Sonnet): $23.11 for 625 MiniWoB episodes · $100.03 for 330
  WorkArena-L1 episodes (9.0 steps) · $299.44 for 235 WorkArena-L2 episodes (33.8 steps).

## Metrics to report

Per condition:
- success with a **Wilson** 95% CI
- steps/task, LLM calls, input/output tokens, tool calls, wall-clock, USD at a stated rate card
- partial credit (TheAgentCompany checkpoints or WebCanvas key nodes)
- the amortization curve (note 07)
- validator precision/recall against a human-labeled subset, **checked per arm**

### Wilson 95% CI full width (pp) ✓

| n | p=0.20 | p=0.35 | p=0.50 |
|---|---|---|---|
| 50 | 21.8 | 25.6 | 26.7 |
| 100 | 15.5 | 18.4 | 19.2 |
| 200 | 11.0 | 13.1 | 13.7 |
| 400 | 7.8 | 9.3 | 9.8 |
| 812 | 5.5 | 6.5 | 6.9 |

"±13pp at n=50" is the worst case in the 20–60% band (p=0.5, CI [36.6, 63.4]). At the edges it's ~±11pp.

### Paired tasks needed to detect 10pp (McNemar, α=.05 two-sided, 80% power) ✓

| Discordant rate ψ | 0.15 | 0.20 | 0.25 | 0.30 | 0.40 |
|---|---|---|---|---|---|
| Tasks | 116 | 155 | 194 | 234 | 312 |

Unpaired needs ~330–390 *per arm*, so pairing roughly halves the requirement. **50 tasks is enough
for AUROC calibration, not for a 10pp significance test.**

## Unresolved names

- VisualWebBench — author/paper not pinned.
- BrowserART — secondary citation only.
- ScreenSpot-v2 — introducing paper not pinned.
- WebChoreArena — search snippets only.
- OpenApps, TimeWarp — BrowserGym README listing only.
- WASP — exists, author list unconfirmed.

Don't cite these as fact.
