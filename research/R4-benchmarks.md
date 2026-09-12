# R4 — Benchmarks, Harnesses, and Metrics

Verification pass against `docs/01-foundations.md` §3 (and supporting claims in §3.7). Method: direct
retrieval of papers/repos (arXiv abstracts and, where precision mattered, the primary PDF text — not
just search-snippet summaries), plus one from-scratch statistical computation. Every fact below is
either sourced with a URL I actually fetched, or marked `[could not verify]` with what I tried.

**Session note on method:** early in this pass I used an automated page-summarizer (WebFetch) to pull
numbers out of the AgentRewardBench PDF and got a table of LLM-judge agreement rates that looked
plausible (GPT-4o 82.5%, Claude 80.0%, etc.) but was **fabricated** — the summarizer invented precise
percentages that are not in the paper. I caught this by downloading the PDF and reading Table 1 myself.
The real numbers are reported in §6 below. This is itself a finding relevant to the project's own
LLM-judge design: **even a "read this PDF and report the numbers" task hallucinates specific figures.**
Treat any number in this document that isn't traceable to a quoted table or sentence with suspicion,
and treat any *other* document's summary of a paper the same way.

A note on scope: a mid-session API rate limit truncated the original research pass before the file was
written. Everything verified before the cutoff is preserved below; a handful of secondary items
(marked `[could not verify]`) were not reached and are listed honestly rather than guessed at.

---

## 1. Benchmark-by-benchmark verification of §3

### 1.1 Offline / action-matching (§3.1)

| Name | Verified? | Real name / authors / venue | Size | What it measures | Scoring |
|---|---|---|---|---|---|
| **Mind2Web** | ✅ Real | Deng, Gu, Zheng, Chen, Stevens, Wang, Sun, Su. NeurIPS 2023 (Datasets & Benchmarks). [arXiv:2306.06070](https://arxiv.org/abs/2306.06070) | >2,000 tasks, 137 websites, 31 domains | Predict next human action from a logged trajectory (offline) | Step/element-match accuracy (no execution) |
| **WebLINX** | ✅ Real | Lù, Kasner, et al. (McGill NLP). ICML 2024. [arXiv:2402.05930](https://arxiv.org/abs/2402.05930) | ~2,300 expert demonstrations, ~100K interactions, 150+ websites | **Conversational** multi-turn web navigation, offline | Action/element match against human demo |
| **AITW (Android in the Wild)** | ✅ Real | Rawles, Li, Rodriguez, Riva, Lillicrap. NeurIPS 2023. [arXiv:2307.10088](https://arxiv.org/abs/2307.10088) | 715K episodes, 30K distinct instructions, 350+ apps/sites | Mobile UI control, offline imitation | Action-match |
| **GUI-Odyssey** | ✅ Real | [arXiv:2406.08451](https://arxiv.org/abs/2406.08451) | 8,334 episodes, 6 device types, 212 apps, cross-app tasks | Cross-**app** (not just cross-page) mobile navigation | Action-match |

§3.1's cautionary note ("many correct paths exist, so step-accuracy under-credits good agents") is
consistent with what the field itself says about offline action-matching; no correction needed there.

### 1.2 Online, deterministic, self-hosted (§3.2) — the causal-claims tier

| Name | Verified? | Authors/org/venue | Size | License | Validator | SOTA (verify carefully — see caveat below) |
|---|---|---|---|---|---|---|
| **WebArena** | ✅ Real | Zhou, Xu, Zhu, X. Zhou, Lo, Sridhar, Cheng, Ou, Bisk, Fried, Alon, Neubig (CMU). 2023. [arXiv:2307.13854](https://arxiv.org/abs/2307.13854) | 812 tasks, 6 self-hosted sites (GitLab, Reddit, "OneStopShop" e-commerce, a CMS admin panel, OpenStreetMap, English Wikipedia) | Apache-2.0 ([github.com/web-arena-x/webarena](https://github.com/web-arena-x/webarena)) | Hybrid: URL match + HTML-artifact-present + "must include" fuzzy string match (176 tasks) + exact match (45 tasks) + (originally) a single LLM check | Original paper: GPT-4 agent 14.41% vs. human 78.24%. Current leaderboard numbers are **not comparable to each other**: [Steel.dev leaderboard](https://leaderboard.steel.dev/leaderboards/webarena/) claims 74.3% (WebTactix, DeepSeek v3.2, mid-2026); a separate paper claims 71.6% (OpAgent, Jan 2026, [arXiv:2602.13559](https://arxiv.org/html/2602.13559v1)); **Surfer 2** claims 69.6% pass@1 using its *own corrected evaluation* ([arXiv:2510.19949](https://arxiv.org/pdf/2510.19949)) — see §2 below, these use different judges/harnesses and are not the same measurement. |
| **VisualWebArena** | ✅ Real | Koh, Lo, Jang, Duvvur, Lim, Huang, Neubig, S. Zhou, Salakhutdinov, Fried. ACL 2024. [arXiv:2401.13649](https://arxiv.org/abs/2401.13649) | 910 tasks; adds a new Classifieds site to WebArena's set, visual-grounding-required goals | Apache-2.0 (same org/repo family) | Same hybrid family as WebArena, extended for visual answers | [could not re-verify current SOTA within budget] |
| **WebArena-Lite** | ✅ Real, not hallucinated | Liu et al., 2024 (curated cleanup of WebArena) — cited by WebRL and Plan-and-Act; shipped in BrowserGym ("Add WebArena Lite" release note) | 165 curated tasks (Shopping-Admin 35, Map 26, Shopping 45, Reddit 19, Gitlab 30, +10 elsewhere) | Inherits WebArena's Apache-2.0 | Cleaned version of WebArena's hybrid validator | — |
| **WorkArena (L1)** | ✅ Real | Drouin, Boisvert, Thakkar, Gasse, Caccia, Le Sellier De Chezelles, Cappart, Chapados, Lacoste (ServiceNow Research / Mila). ICML 2024. [arXiv:2403.07718](https://arxiv.org/abs/2403.07718) · [github.com/ServiceNow/WorkArena](https://github.com/ServiceNow/WorkArena) | **33 unique tasks, 19,912 unique instances — all on one self-hosted ServiceNow instance** | **Apache-2.0** | Programmatic: checks ServiceNow record/UI state after each task | Authors state the benchmark is "not solved"; no single clean current-SOTA number found this session |
| **WorkArena++** | ✅ Real | Boisvert, Le Sellier De Chezelles, et al. NeurIPS 2024 (D&B track). [arXiv:2407.05291](https://arxiv.org/abs/2407.05291) | 682 compositional tasks, same ServiceNow instance, requires planning across atomic WorkArena components | Apache-2.0 | Programmatic | — |
| **TheAgentCompany** | ✅ Real | Xu, Song, Li, et al. (CMU + OpenHands/All Hands AI collaborators). NeurIPS 2025 (D&B). [arXiv:2412.14161](https://arxiv.org/abs/2412.14161) | 175 tasks in a self-hosted simulated company: GitLab, Plane, ownCloud, RocketChat, all pre-baked in Docker | **MIT** | Checkpoint-based: points per checkpoint + 50% bonus only if *all* checkpoints pass | — |
| **MiniWoB++** | ✅ Real | Original MiniWoB: Shi et al. 2017; extended to MiniWoB++ by Liu et al., "Reinforcement Learning on Web Interfaces via Workflow-Guided Exploration," ICLR 2018. Now maintained by Farama Foundation ([github.com/Farama-Foundation/miniwob-plusplus](https://github.com/Farama-Foundation/miniwob-plusplus)) | ~100–125 synthetic mini-page templates | MIT (Farama standard) | Programmatic, exact | Toy-scale; near-saturated by modern agents |
| **WebShop** | ✅ Real | Yao, Chen, Yang, Narasimhan. NeurIPS 2022. [arXiv:2207.01206](https://arxiv.org/abs/2207.01206) | 1.18M products, 12,087 crowd-sourced instructions, **one** synthetic shopping site | CC BY 4.0 (per arXiv listing; verify the code repo's own LICENSE file separately before depending on it) | Programmatic reward (product-attribute match) | Original: human 59%, best model 29%, rule baseline 9.6% |

**§3.2's harness line — "BrowserGym / AgentLab — adopt rather than write our own runner. `[verify]`"**
is **confirmed real and actively maintained**; see §3 below. The `[verify]` tag can be removed.

### 1.3 Online, live web (§3.3)

| Name | Verified? | Facts | Note |
|---|---|---|---|
| **WebVoyager** | ✅ Real | ACL 2024, [arXiv:2401.13919](https://arxiv.org/abs/2401.13919). 643 tasks, 15 live websites (~40–46 tasks/site), scored by a GPT-4V LLM judge | Non-reproducible by design (live web) |
| **Online-Mind2Web** | ✅ Real | OSU NLP Group, "An Illusion of Progress? Assessing the Current State of Web Agents," [arXiv:2504.01382](https://arxiv.org/abs/2504.01382) | **Central critique paper for Q4** — see §4 |
| **AssistantBench** | ✅ Real | Yoran et al. 2024. 214 tasks total; validation split (33 tasks) is what gets reused (e.g. by AgentRewardBench) because the test set is private | Realistic internet tasks starting from a search engine |
| **WebCanvas / Mind2Web-Live** | ✅ Real | iMeanAI, ICML 2024, [arXiv:2406.12373](https://arxiv.org/abs/2406.12373). WebCanvas = the eval framework; Mind2Web-Live = the benchmark of ~542 tasks / 2,439 annotated intermediate "key-node" states | Key-node partial-credit scoring survives live-site drift |
| **GAIA** | ✅ Real | Meta AI, [arXiv:2311.12983](https://arxiv.org/abs/2311.12983) | 466 tasks, 3 difficulty levels, human 92% vs. GPT-4+plugins 15% | General-assistant benchmark, only partly web-browsing — §3's description ("general assistant, partially browsing") is accurate |

### 1.4 OS / desktop / mobile (§3.4)

| Name | Verified? | Facts |
|---|---|---|
| **OSWorld** | ✅ Real | Xie, Zhang, Chen +14 others (HKU, Salesforce Research, CMU, U. Waterloo). [arXiv:2404.07972](https://arxiv.org/abs/2404.07972), 2024. **369 tasks (361 usable)**, real Ubuntu apps (LibreOffice suite, Thunderbird, GIMP, Chrome, VS Code, VLC), 10–100 steps/task. Observation: screenshot **and** a11y tree. Scoring: **134 custom programmatic checker functions** on final file/app state. **License: CC BY-SA 4.0.** Original SOTA: best model 12.24% vs. human 72.36%. |
| **OSWorld-Verified** | ✅ Real | Refinement by the XLANG Lab team (~10 people, ~2 months): fixed **300+ issues** — env instability/CAPTCHAs/anti-crawling, ambiguous instructions, overly-narrow ground truth, decentralized-eval incomparability. Source: [xlang.ai/blog/osworld-verified](https://xlang.ai/blog/osworld-verified). Reported current leader: **CoAct-1 at 60.76%** (~84% of the ~72% human ceiling) — *sourced from the official project blog; I did not cross-check this specific number against a second primary source, flag accordingly.* |
| **WindowsAgentArena** | ✅ Real | Microsoft, [arXiv:2409.08264](https://arxiv.org/abs/2409.08264). 150+ Windows tasks; "Navi" agent 19.5% vs. human 74.5% |
| **AndroidWorld** | ✅ Real | Rawles et al. (Google DeepMind), [arXiv:2405.14573](https://arxiv.org/abs/2405.14573). 116 hand-crafted tasks, 20 real Android apps, parameterized to millions of variations, programmatic ADB-based checks. Original SOTA 30.6%. **Caveat: by 2026 there are papers claiming near-saturation** (e.g. a task-decomposition paper titled around "Achieving Perfect Accuracy on AndroidWorld") — any single SOTA number here is stale within months; check the live leaderboard before citing. |

### 1.5 Component-level (§3.5)

| Name | Verified? | Facts |
|---|---|---|
| **ScreenSpot** | ✅ Real | Introduced in the *SeeClick* paper, Cheng et al., Jan 2024, [arXiv:2401.10935](https://arxiv.org/abs/2401.10935). "First realistic GUI grounding benchmark across mobile/desktop/web." Independently confirmed size via the HF dataset card: **1,272 image–instruction pairs**, iOS/Android/macOS/Windows/Web. |
| **ScreenSpot-v2** | ⚠️ Partially verified | Widely used, dataset exists and is cited as a cleanup of annotation ambiguity in the original ScreenSpot, but I could not independently pin its own introducing paper/authors within budget. `[could not verify primary authorship]` |
| **ScreenSpot-Pro** | ✅ Real | Li, Meng, Lin, Luo, Tian, Ma, Huang, Chua. 2025 workshop paper (Reasoning & Planning for LLMs). [github.com/likaixin2000/screenspot-pro-gui-grounding](https://github.com/likaixin2000/screenspot-pro-gui-grounding), MIT license. **1,581 expert-annotated pairs, 23 professional high-resolution desktop apps.** SOTA is still under 60% (BAMI 57.8%, Phi-Ground 55.0%, GTA1-7B 50.1%, original baseline 47.2%/35.9%) — much harder than ScreenSpot-v2 (~88% SOTA), i.e. professional-app grounding is a real unsolved bottleneck, not saturated like consumer-app grounding. |
| **VisualWebBench** | ❓ Unresolved | `[could not verify within budget — ran out of session before confirming authors/paper against a primary source]` |
| **AgentRewardBench** | ✅ Real, verified from primary PDF | Lù, Kazemnejad, Meade, Patel, Shin, Zambrano, Stańczak, Shaw, Pal, Reddy (McGill/Mila/ServiceNow Research/Google DeepMind). [arXiv:2504.08942](https://arxiv.org/pdf/2504.08942). Full numbers in §6. |

### 1.6 Safety / adversarial (§3.6)

| Name | Verified? | Facts |
|---|---|---|
| **AgentDojo** | ✅ Real | Debenedetti, Zhang, Balunović, Beurer-Kellner, Fischer, Tramèr (ETH Zurich + Invariant Labs). NeurIPS 2024 (D&B). [arXiv:2406.13352](https://arxiv.org/abs/2406.13352), MIT license, [github.com/ethz-spylab/agentdojo](https://github.com/ethz-spylab/agentdojo). Prompt-injection attacks/defenses for tool-calling agents. |
| **WASP** | ✅ Real (title/existence confirmed) | "Benchmarking Web Agent Security Against Prompt Injection Attacks," [arXiv:2504.18575](https://arxiv.org/pdf/2504.18575). `[author list not independently confirmed this session]` |
| **ST-WebAgentBench** | ✅ Real | IBM Research + collaborators, targeting ICLR 2026 per IBM's page. [arXiv:2410.06703](https://arxiv.org/abs/2410.06703). Built into BrowserGym. **375 enterprise tasks, 3 apps, 3,057 policy instances across 6 safety dimensions.** Introduces "Completion under Policy" (CuP) metric. |
| **BrowserART** | ❓ Unresolved | Appears in a survey paper's list alongside the three above, but I could not fetch its own primary paper this session. `[could not verify — name only, via secondary citation]` |

### 1.7 Benchmarks §3 missed

- **Online-Mind2Web** is *already* named in §3.3, but §3 doesn't surface its single most important
  finding — see §4 below; strongly recommend pulling that finding up into the main text since it's
  the sharpest "reported vs. reproduced" data point available.
- **WebChoreArena** — a WebArena-lineage benchmark explicitly built to fix ambiguity/mis-specification
  in WebArena tasks (found via multiple independent search hits, has its own site/paper). Recommend
  adding as a named "quality-controlled successor" alongside WebArena-Lite. `[found via search
  snippets/site only; did not fetch its paper directly this session — treat facts about it as
  unverified until re-checked]`
- **OpenApps** and **TimeWarp** — appear as two more environments in BrowserGym's own default
  benchmark list (README), beyond the ones §3 names. `[could not verify further than the README
  listing — no paper fetched]`
- **AgentRewardBench**'s own environment set (WebArena, VisualWebArena, WorkArena L1/L2, AssistantBench,
  Mind2Web) is a good "if you only trust one paper's coverage" cross-section and is worth citing as
  such in the main doc.

---

## 2. Which benchmark actually fits this project

Requirements restated: deterministic + self-hostable; DOM/a11y-tree observation; **many tasks per
site** (the critical, unusual one); programmatic validator; permissive license.

| Candidate | Self-hosted/deterministic | Observation | Tasks **per site** | Validator | License | Fit |
|---|---|---|---|---|---|---|
| **WorkArena (L1) + WorkArena++ (L2)** | ✅ (one ServiceNow instance) | ✅ AXTree/DOM via BrowserGym | **33 tasks × 19,912 instances, plus 682 compositional tasks — all on the same single site** | ✅ programmatic (record/UI state) | ✅ Apache-2.0 | **Best fit.** This benchmark's entire design *is* "one site, many tasks" — it's the only candidate where the site count is literally 1. |
| **WebArena / WebArena-Lite** | ✅ (6 self-hosted sites) | ✅ AXTree/DOM | 812 tasks / 6 sites ≈ 135/site nominally (WebArena-Lite's per-domain counts: Shopping 45, Shopping-Admin 35, Gitlab 30, Map 26, Reddit 19); real per-site counts skew unevenly, not independently re-verified for the full 812-task set this session | ⚠️ hybrid — partly string/URL match, partly LLM judge (176 "must include" + growing reliance on LLM ensembles per Surfer 2's fix) | ✅ Apache-2.0 | Good secondary/generalization environment; decent per-site volume but validator is not purely programmatic, and known-brittle (§4). |
| **TheAgentCompany** | ✅ (Docker) | ✅ (real apps' DOM/UI) | 175 tasks spread across 4+ different apps (GitLab, Plane, ownCloud, RocketChat) — thin per site, and tasks are long-horizon/expensive | ✅ programmatic checkpoints | ✅ MIT | Poor fit for the amortization axis specifically — not enough tasks concentrated on one site. |
| **VisualWebArena** | ✅ | ✅ (+ visual) | 910 tasks / multiple sites — similarly thin per site as WebArena | ⚠️ same hybrid family | ✅ Apache-2.0 | Same shape as WebArena; only add if visual grounding is in scope. |
| **MiniWoB++** | ✅ | ✅ (synthetic DOM) | ~100–125 templates, but each is a synthetic toy page, not a real navigable "site" with an affordance graph worth building | ✅ programmatic | ✅ MIT | Technically DOM-based and deterministic, but there's no real site-map to amortize — disqualified in spirit even though it passes the letter of the requirements. |
| **WebShop** | ✅ (one synthetic site) | ✅ DOM | **One site, 12,087 instruction variations** — matches the "many tasks, one site" shape well | ✅ programmatic (attribute match) | ✅ CC BY 4.0 (verify repo LICENSE separately) | Strong secondary/pilot candidate: cheap, single-site, high task count, but only one task *type* (search-and-purchase), so it can't test amortization across varied affordances (forms, admin panels, multi-step workflows) the way WorkArena can. |

**Recommendation: WorkArena (L1 for raw per-site task volume, WorkArena++ for compositional/longer-horizon
tasks on the same instance) as the primary environment.** It is the only benchmark in this list whose
site count is literally 1, so every property the amortization experiment needs (repeated tasks on one
site, a real DOM/a11y-tree, programmatic ground truth, a permissive license, BrowserGym integration for
free) is satisfied simultaneously. Use **WebArena's shopping/admin/gitlab domains** as a secondary
generalization check (different real site, still self-hosted, still Apache-2.0), and consider
**WebShop** as a cheap, fast pilot for early iteration on the graph-tool API before committing to
WorkArena's heavier ServiceNow instance.

---

## 3. Harness: BrowserGym / AgentLab

**Both exist and are actively maintained.** BrowserGym: [github.com/ServiceNow/BrowserGym](https://github.com/ServiceNow/BrowserGym),
Apache-2.0 license (confirmed via LICENSE file), latest PyPI release **0.14.3, Jan 20 2026** with dev
releases into Dec 2025 — i.e., maintained within the last ~8 months of "today" (Sept 2026). AgentLab:
[github.com/ServiceNow/AgentLab](https://github.com/ServiceNow/AgentLab), same org, described as the
companion "framework to implement, test, and evaluate your web agents on all BrowserGym benchmarks."
Ecosystem paper: "The BrowserGym Ecosystem for Web Agent Research," 20 authors led by Le Sellier De
Chezelles and Gasse, [arXiv:2412.05467](https://arxiv.org/html/2412.05467v4).

**What it gives us:**
- A Gym-style environment abstraction over 6+ benchmarks: MiniWoB(++), WebArena, WebArena-Lite,
  VisualWebArena, WorkArena (L1/L2/L3), AssistantBench, WebLINX (static), plus OpenApps/TimeWarp
  (`[names only, not independently verified beyond the README listing]`).
- Multiple observation modes out of the box: HTML, AXTree, screenshot, set-of-marks.
- A `HighLevelActionSet` class with `to_python_code()` (converts high-level primitives like `click`,
  `fill`, `hover`, `scroll`, `select_option` into Playwright code) and `describe()` (builds the
  action-space text description for the agent's prompt).
- AgentLab layers on: large-scale parallel experiments via Ray, a unified LLM API across
  OpenRouter/OpenAI/Azure/self-hosted-TGI, and an "AgentXRay" trace visualizer.
- **Concrete, published cost numbers** — a real sign this harness gets used for real budgets: the
  ecosystem paper reports (Claude 3.5 Sonnet) $23.11 for 625 MiniWoB episodes (3.7 avg steps),
  $100.03 for 330 WorkArena-L1 episodes (9.0 avg steps), $299.44 for 235 WorkArena-L2 episodes
  (33.8 avg steps).

**Extension story — for our purposes:**
- *Custom tools/actions:* environments accept an optional custom `action_mapping` function, so a new
  action vocabulary (e.g. our `search`/`neighbors`/`path`/`landmarks`/`record` graph-tool calls) can be
  added without forking the library — you write a mapping from your action schema to Playwright calls,
  the same mechanism `HighLevelActionSet` itself uses. New *tasks* are added by subclassing
  `AbstractBrowserTask`. This is a low-friction extension point, not a rigid closed taxonomy.
- *Per-step logprobs / candidate action sets:* **not natively supported as far as I could verify.**
  The framework has an `AgentInfo`/"AgentXRay" mechanism for logging prompts and trace metadata, but
  I found no confirmed built-in logprob or candidate-distribution capture. **This is a real gap for
  P3's uncertainty-signal work** — we would need to wrap the acting model's call ourselves (e.g. via a
  local vLLM/llama.cpp scorer per §3(P3) of the foundations doc) and thread the logprob/entropy data
  through `AgentInfo`'s extensible fields rather than relying on anything BrowserGym gives for free.

**Alternatives** (named for completeness; **not independently verified this session** — treat as
leads, not facts): AgentBench (THUDM) is a broader, non-web-specific multi-environment suite; UK
AISI's "Inspect" is a general-purpose eval harness, not web-specific; writing a bespoke
Playwright/Selenium harness (what WebArena and OSWorld each originally shipped) gives full control at
the cost of losing the shared benchmark corpus and community tooling BrowserGym already provides.
Given the concrete extension points above and the demonstrated maintenance cadence, **BrowserGym +
AgentLab is the right default**; budget separate engineering time specifically for logprob/candidate-set
logging, since that is not something adopting the harness buys us for free.

---

## 4. Known problems with these benchmarks

- **WebArena: 71 of 812 tasks (≈8.7%) had erroneous labels**, per a manual review reported in the
  *Surfer 2* paper's appendix (verified by downloading and reading the PDF directly, not just a
  summary): "We conducted a manual review of the benchmark dataset..., resulting in the correction of
  71 tasks with erroneous labels. The scope of these modifications ranged from minor typographical
  fixes to the resolution of critical logical inconsistencies that fundamentally affected evaluation
  outcomes." Categories: data-accuracy errors (wrong quantities/names), typos, URL/focus updates,
  "evaluation flexibility" fixes (replacing brittle exact values with fuzzy placeholders), and
  formatting/consistency edits. Full table with examples in [arXiv:2510.19949](https://arxiv.org/pdf/2510.19949)
  Appendix A.2. The same paper also replaced WebArena's original single-LLM-plus-string-match judge
  with an **ensemble of 5 independent GPT-4.1 judges aggregated by majority vote**, specifically to
  reduce judge variance/bias — and reports that even *without* their manual task corrections, this
  judge-ensemble-only version already beats the prior SOTA (67.4%), i.e. some of the "improvement" in
  recent WebArena numbers is evaluation-methodology change, not agent capability change. **This is
  exactly the confound the foundations doc's P4 section warns about, but applied to the benchmark's
  own scoring, not just to agent conditions.**
- **WebArena-Lite** (165-task curated subset, Liu et al. 2024) is a second, independent community
  response to the same underlying problem (task quality), now used by WebRL and Plan-and-Act and
  shipped inside BrowserGym.
- **OSWorld → OSWorld-Verified: 300+ issues fixed**, by a ~10-person team over ~2 months — a
  much larger-scope correction (touching what looks like the majority of the 369-task set) than
  WebArena's 71/812. Categories: anti-crawling/CAPTCHA blocking automated agents, IP restrictions,
  DOM-structure drift on live dependencies, timing fragility in multi-step setups, ambiguous
  instructions, and — the one most relevant to us — **"evaluation gaps: limited ground truth
  accepting only narrow solution paths while missing valid alternatives."** Source:
  [xlang.ai/blog/osworld-verified](https://xlang.ai/blog/osworld-verified).
- **Rule-based/programmatic validators systematically under-report success, not over-report it** —
  this is the single most important, and most counter-intuitive, finding for our design. From
  AgentRewardBench (verified from primary PDF, §6 below): the *official* rule-based evaluators used
  by WebArena/VWA/WorkArena/etc. have precision 83.8% but **recall only 55.9%** against expert human
  judgment — meaning nearly half of genuinely successful trajectories get scored as failures. The
  paper's own framing: "rule-based evaluation... tends to reject many valid trajectories, which
  results in the success rate of certain web agents being lower than what an expert would perceive."
  The doc's §3.7 bullet ("Success rate via programmatic validator — gold standard, but validators are
  brittle") is directionally right but should be sharpened: the brittleness is **asymmetric and
  downward** (false negatives, not false positives) — the opposite failure mode from LLM judges, which
  *over*-credit (see §6). Treating "brittle" as one undifferentiated risk conflates two opposite biases.
- **Reported-vs-reproduced gap on live-web / LLM-judge benchmarks**: the *Online-Mind2Web* paper
  ("An Illusion of Progress? Assessing the Current State of Web Agents," [arXiv:2504.01382](https://arxiv.org/abs/2504.01382))
  reports that Browser Use and OpenAI Operator score close to 90% on WebVoyager (LLM-judge-scored, live
  web) but drop to **30% and 61% respectively** on the paper's own more rigorous Online-Mind2Web
  benchmark — a huge illusion-of-progress gap directly attributable to benchmark/judge choice, not
  agent capability. Their proposed fix, **WebJudge (built on o4-mini), reaches 85.7% agreement with
  human judgment and only a 3.8% average success-rate gap** — offered as evidence that a
  carefully-designed LLM judge *can* close most of this gap, in contrast to the older/cruder judges
  AgentRewardBench evaluates.
- **Contamination:** `[could not verify a specific contamination study within budget — this is a
  broadly-known concern in the LLM-agent-benchmark literature generally, but I do not have a citation
  to attach to it for this project, and it should be marked unverified rather than asserted]`.

---

## 5. Metrics: what the field reports, what we should report

**Efficiency (steps/tokens/cost):** under-reported, as §3.7 already says, but there is at least one
concrete positive example worth copying: the BrowserGym ecosystem paper reports **$/benchmark-run and
average-steps-per-episode side by side** (e.g. WorkArena-L2: $299.44 over 235 episodes, 33.8 avg
steps) — that is the level of granularity we should target: cost *and* step count *and* task count,
reported together, per condition, not folded into a single headline number.

**Partial-credit / checkpoint schemes actually in use:**
- *TheAgentCompany*: points per checkpoint, plus a 50% bonus reserved for full completion — explicitly
  designed so partial credit doesn't let an agent "coast" to a good score without finishing.
- *WebCanvas / Mind2Web-Live*: "key-node" scoring — annotated intermediate states that must be hit,
  designed specifically to survive live-site drift (a different problem than TheAgentCompany's, but
  the same partial-credit shape).
Both are reasonable templates for a graph-agent project that wants credit for "got most of the way
through a macro, then had to fall back to naive exploration."

**Variance reporting:** I did not find a citation quantifying how rare CI/variance reporting is across
the field, beyond what the Online-Mind2Web illusion-of-progress result already demonstrates implicitly
(single-number leaderboard entries hide huge instability). Treat "the field mostly doesn't report
variance" as consistent with everything else found here, but unverified as a standalone claim.

### §3.7's CI claim — verified and corrected

**Claim in the doc:** "success in the 20–60% band at n≈50 carries roughly ±13pp CIs." **This is
essentially correct**, computed directly (95% two-sided, z=1.96):

Naive/Wald half-width, `z·√(p(1-p)/n)`, in percentage points:

| p \ n | 20 | 30 | 50 | 75 | 100 | 150 | 200 | 300 | 500 |
|---|---|---|---|---|---|---|---|---|---|
| 0.2 | 17.5 | 14.3 | 11.1 | 9.1 | 7.8 | 6.4 | 5.5 | 4.5 | 3.5 |
| 0.3 | 20.1 | 16.4 | 12.7 | 10.4 | 9.0 | 7.3 | 6.4 | 5.2 | 4.0 |
| 0.4 | 21.5 | 17.5 | 13.6 | 11.1 | 9.6 | 7.8 | 6.8 | 5.5 | 4.3 |
| 0.5 | 21.9 | 17.9 | **13.9** | 11.3 | 9.8 | 8.0 | 6.9 | 5.7 | 4.4 |
| 0.6 | 21.5 | 17.5 | 13.6 | 11.1 | 9.6 | 7.8 | 6.8 | 5.5 | 4.3 |

Wilson score interval half-width (the statistically preferred one at small/moderate n, corrected for
the coverage problems Wald has near the tails — here p is safely mid-range so the two nearly agree):

| p \ n | 20 | 30 | 50 | 75 | 100 | 150 | 200 | 300 | 500 |
|---|---|---|---|---|---|---|---|---|---|
| 0.2 | 16.8 | 13.9 | 10.9 | 8.9 | 7.8 | 6.4 | 5.5 | 4.5 | 3.5 |
| 0.3 | 18.7 | 15.6 | 12.3 | 10.2 | 8.8 | 7.3 | 6.3 | 5.2 | 4.0 |
| 0.4 | 19.7 | 16.5 | 13.1 | 10.8 | 9.4 | 7.7 | 6.7 | 5.5 | 4.3 |
| 0.5 | 20.1 | 16.8 | 13.4 | 11.0 | 9.6 | 7.9 | 6.9 | 5.6 | 4.4 |
| 0.6 | 19.7 | 16.5 | 13.1 | 10.8 | 9.4 | 7.7 | 6.7 | 5.5 | 4.3 |

Concretely, at n=50: k=25/50 (p=0.5) → Wilson 95% CI **[36.6%, 63.4%]**, half-width 13.4pp — matching
the doc's "~13pp" almost exactly. **Correction to the doc's phrasing:** ±13pp is the *worst case* in
the 20–60% band (at p≈0.5); the band's edges (p=0.2 or 0.6) are narrower, ~11pp. State the claim as
"up to ±13–14pp at the worst point in the band, narrowing to ~11pp at the edges" rather than a flat
±13pp, and prefer Wilson over Wald when p is not known in advance to be safely mid-range (they
coincide here, but won't for p near 0 or 1, e.g. safety-benchmark pass rates).

---

## 6. Judge reliability — AgentRewardBench (verified from primary text, not a summary)

AgentRewardBench, Lù et al., [arXiv:2504.08942](https://arxiv.org/pdf/2504.08942) (McGill/Mila/
ServiceNow Research/Google DeepMind). **1,302 trajectories, 5 benchmarks (WebArena, VisualWebArena,
WorkArena L1/L2, AssistantBench, Mind2Web), 4 LLM agent backbones (GPT-4o, Claude 3.7 Sonnet,
Llama 3.3 70B, Qwen2.5-VL), each trajectory reviewed by expert human annotators on three axes: success,
side effects, repetition.**

**Human inter-annotator agreement: 89.3%** on the success label (a second annotator re-labeled the
GPT-4o/WebArena subset; disagreements resolved by discussion).

**Exact Table 1 numbers** (precision/recall/F1 on the success dimension, overall across benchmarks):
- Official rule-based evaluator: **precision 83.8%, recall 55.9%, F1 67.1%**.
- Best LLM judges (the paper's own "simplified judge," which decoupled the reasoning chain from a
  fixed system prompt): GPT-4o **precision 69.8%, F1 75.9%**; Claude 3.7 Sonnet precision 68.8%,
  F1 74.7%. **No LLM judge tested exceeds 70% precision.** Direct quote: "no judge achieves above 70%
  precision... 30% of trajectories are erroneously marked as successful."
- Rule-based vs. expert-judged success rate gap is large and *always in the same direction*
  (rule-based under-counts): "the performance of GPT-4o being 16.7% lower on WebArena and 18.5% lower
  on VWA compared to expert annotations." LLM judges go the *other* way (over-credit), with two
  exceptions noted in WorkArena++.

**Net takeaway for our project:** if any part of our scoring pipeline uses an LLM judge, budget for
it to be wrong on the success label roughly 25–30% of the time relative to expert humans (specifically,
over-crediting); if it uses a hand-written programmatic validator, budget for it to be wrong in the
*other* direction (under-crediting, roughly 15–20pp on WebArena-family tasks per the numbers above)
unless the validator is unusually well-specified (WorkArena's official rule-based evaluator hit 100%
precision in AgentRewardBench's Table 3, the one clean exception — worth emulating its validator
design specifically).

As a second, more optimistic data point: Online-Mind2Web's **WebJudge (o4-mini-based) reports 85.7%
agreement with human judgment and a 3.8% average success-rate gap** — better than any judge in
AgentRewardBench. These two results are not directly contradictory: they measure different things
(AgentRewardBench's judges assess execution-based-benchmark trajectories on 3 axes; WebJudge assesses
open-ended live-web task completion only) and WebJudge is newer/more purpose-built. Read together they
suggest LLM-judge quality is very sensitive to task design and judge scaffolding, not a fixed property
of "using an LLM as a judge" — so if we adopt one, it should be validated against a human-labeled
subset the way both of these papers did, not assumed to transfer.

---

## 7. Statistical practice: paired comparisons and sample size

**Test:** for paired per-task binary outcomes (same task, two agent conditions), **McNemar's test** is
the right classical choice — it uses only the *discordant* pairs (task succeeded under condition A but
not B, or vice versa) and is exact/asymptotically-χ² under the null that the two discordant rates are
equal. A **bootstrap or permutation test on the paired difference-in-proportions** is a reasonable
nonparametric alternative that doesn't rely on the χ² approximation and handles extra structure (e.g.
multiple seeds per task, meaning outcomes aren't fully independent) more gracefully — recommend using
it *alongside* McNemar when n is small or seeds are stacked, not as a replacement in the large-n
regime.

**Sample size** (computed directly; standard McNemar power approximation, e.g. Connor 1987 — 95%
two-sided, detecting a 10-point paired success-rate difference):

| Discordant-pair rate (p₀₁+p₁₀) | N paired tasks @ 80% power | N @ 90% power |
|---|---|---|
| 0.15 | 115 | 153 |
| 0.20 | 155 | 206 |
| 0.25 | 194 | 259 |
| 0.30 | 233 | 311 |
| 0.40 | 312 | 416 |
| 0.50 | 390 | 521 |
| 0.60 | 469 | 626 |

For comparison, an **unpaired** two-proportion z-test detecting the same 10pp difference (e.g. 45% vs.
55%) needs roughly 290–390 tasks *per arm* (580–780 total) at 80% power — i.e., **the paired design the
foundations doc already commits to (§4/P4) typically needs roughly half or fewer total tasks** to
detect the same effect, which is the concrete quantitative justification for insisting on paired
per-task comparisons rather than aggregate deltas.

**Correction to the doc's "≥50 tasks/condition, ≥3 seeds" line (§4/P4):** 50 tasks is very likely
**underpowered specifically for a 10pp effect** — the table above says you need on the order of
150–300+ *paired* tasks (depending on how often the two conditions actually disagree on the same task,
which is not something we can know in advance and should be estimated from a pilot). Recommend sizing
the primary experiment closer to WorkArena's own per-site task volume (hundreds of instances are
available) rather than the 50-task figure, and treat 50 tasks as adequate only for a much larger
effect size (e.g. ≥20pp) or as a Phase-0 calibration/pilot run, which is in fact how the doc already
uses it in §5 Phase 0 — that specific use (AUROC calibration, not a paired significance test) is fine
at n≈50; it's only the *significance-testing* use that needs the larger n above.

---

## Corrections to docs/01-foundations.md

> **§3.2:** "**Harness:** BrowserGym / AgentLab — adopt rather than write our own runner. `[verify]`"

Confirmed real and actively maintained (Apache-2.0; PyPI 0.14.3, Jan 2026; ecosystem paper
[arXiv:2412.05467](https://arxiv.org/html/2412.05467v4)). Remove the `[verify]` tag. Add: it does *not*
give us per-step logprob/candidate-set logging for free (§3 of this doc) — that has to be built.

> **§3.5:** "Judges/reward models: AgentRewardBench — do automatic judges agree with humans? Reportedly
> less than one would like. `[verify]`"

Confirmed, with exact numbers now available (verified from the primary PDF, not a summary): official
rule-based evaluator precision 83.8% / recall 55.9% / F1 67.1%; best LLM judge tops out at 69.8%
precision; no judge exceeds 70% precision; human inter-annotator agreement 89.3%. See §6 above for the
full table and the direction of the two biases (rule-based under-credits, LLM judges over-credit).

> **§3.7:** "Success rate via programmatic validator — gold standard, but validators are brittle and
> some WebArena tasks are reported unsolvable or mis-specified; audited subsets exist. `[verify]`"

Confirmed and sharpened: 71/812 WebArena tasks (≈8.7%) had erroneous labels corrected per a manual
audit ([arXiv:2510.19949](https://arxiv.org/pdf/2510.19949) Appendix A.2, with a full table of
correction categories); OSWorld's audit found 300+ issues (majority of the 369-task set) fixed in
OSWorld-Verified. But "brittle" understates the direction of the effect: AgentRewardBench shows the
brittleness is **asymmetric and downward** — programmatic validators mostly produce false negatives
(under-crediting), the opposite failure mode from LLM judges (over-crediting). The doc should
distinguish these two, not lump them together as one "brittleness" risk.

> **§3.7:** "Variance — success in the 20–60% band at n≈50 carries roughly ±13pp CIs. Most reported
> deltas in this field are noise. `[verify the arithmetic and state the exact interval used]`"

Arithmetic confirmed correct at the band's worst point (p≈0.5, n=50: Wald and Wilson both give
≈13.4–13.9pp half-width; Wilson 95% CI for 25/50 is exactly [36.6%, 63.4%]). Correction: ±13pp is the
*maximum* over the 20–60% band, not a flat value across it — the band's edges (p=0.2 or 0.6) are
narrower, ~11pp. Full table in §5 above. Also: prefer the Wilson interval over the naive Wald formula
as house style, even though they coincide in this particular range.

> **§4/P4:** "**Stats:** ≥50 tasks/condition, ≥3 seeds, CIs, paired per-task comparisons rather than
> aggregate deltas."

The paired-comparison instinct is correct and is exactly what McNemar (or a paired bootstrap) is built
for. But 50 tasks/condition is very likely underpowered for a McNemar test aimed at a 10pp effect —
computed sample sizes run 115–470 paired tasks depending on the (unknown in advance) discordant-pair
rate, i.e. 3–9× the stated figure. Recommend keeping n≈50 only for the Phase-0 AUROC-calibration use
(where it's adequate) and sizing the Phase-2 significance-testing experiment to WorkArena's much larger
per-site task pool instead. See §7 above for the full table and the McNemar-vs-unpaired comparison.

> **§3.6:** "AgentDojo; WASP (web prompt injection); ST-WebAgentBench (policy compliance); BrowserART."

AgentDojo, WASP, and ST-WebAgentBench are all confirmed real with primary sources (§1.6 above).
**BrowserART could not be independently verified this session** — it appears only inside another
survey paper's list, and I did not reach its own paper. Mark it `[could not verify]` rather than
treating it as confirmed until it's checked directly.

---

## Design implications

1. **Primary benchmark: WorkArena (L1) + WorkArena++ (L2)** on the single self-hosted ServiceNow
   instance. It is the only candidate whose site count is literally 1, which is exactly what the
   amortization-across-repeated-tasks-on-one-site experiment (§4/P4's "success vs. number of tasks
   executed on that site" plot) needs. Apache-2.0, DOM/AXTree observation via BrowserGym, programmatic
   validators, thousands of task instances available. Use WebArena's shopping/admin/gitlab domains as
   a secondary generalization check on a different real site, and WebShop as a cheap early pilot for
   the graph-tool API before committing engineering time to the heavier ServiceNow instance.
2. **Harness: BrowserGym + AgentLab**, adopted rather than built. Budget separate work specifically for
   (a) a custom `action_mapping` exposing the graph-tool actions (`search`/`neighbors`/`path`/
   `landmarks`/`record`) and (b) per-step logprob/candidate-action-set logging, since neither of these
   is free — the extension point exists for (a), nothing confirmed exists for (b).
3. **Validator design:** since programmatic validators under-credit and LLM judges over-credit, and
   since a summarizer can silently fabricate numbers when reading even a real paper (this session's
   own near-miss), any scoring component we build should be (a) validated against a small
   human-labeled subset before being trusted for the headline metric, the way both AgentRewardBench
   and Online-Mind2Web's WebJudge did, and (b) reported alongside its own precision/recall against that
   subset, not presented as ground truth.
4. **Metric set to report per condition:** success rate with a Wilson (not Wald) 95% CI; steps/task;
   $/task; a checkpoint/key-node partial-credit score (TheAgentCompany- or WebCanvas-style) in addition
   to binary success, so a graph agent that gets most of the way through a macro before falling back
   gets partial credit rather than a zero; and the amortization curve (success and $/task vs. number of
   tasks already executed on the site) that §4/P4 already calls for.
5. **Sample size:** size the Phase-2 comparison to roughly 150–300+ paired tasks per site (not 50) if
   the target effect is ~10pp, using McNemar or a paired bootstrap on discordant pairs; reserve n≈50 for
   the Phase-0 AUROC calibration use, where it remains adequate. WorkArena's per-site task volume
   (19,912 L1 instances, 682 L2 tasks) comfortably supports this without needing a second site.

## Open questions

1. **VisualWebBench, ScreenSpot-v2's own paper, WASP's full author list, BrowserART, WebChoreArena's
   primary paper, OpenApps/TimeWarp** — all left as `[could not verify]` or partially verified this
   session due to the rate-limit cutoff; worth a follow-up pass before any of these five are cited as
   fact in a final write-up.
2. **WebArena's per-site task breakdown for the full 812-task set** (as opposed to the 165-task
   WebArena-Lite subset, which I do have) — needed to make the "secondary site" comparison in §2
   precise rather than approximate.
3. **Is there a published contamination study specifically for WebArena/WorkArena-family benchmarks?**
   Not found this session; worth a targeted search rather than treating contamination as a generic,
   citation-free worry.
4. **AndroidWorld and OSWorld-Verified current SOTA move fast** (this session found sources suggesting
   near-saturation claims for AndroidWorld by 2026) — whichever number ends up in a final paper should
   be re-checked against the live leaderboard at write time, not cited from this document's snapshot.
5. **Does WorkArena's validator design (100% precision in AgentRewardBench's Table 3, the one clean
   exception found) generalize as a template, or is it an artifact of ServiceNow's structured record
   model being unusually easy to check programmatically?** If the latter, that's a reason to expect our
   own graph-agent's validator to be *harder* to get right on less structured sites, and worth
   surfacing explicitly to whoever designs P1/P2's termination predicates.
