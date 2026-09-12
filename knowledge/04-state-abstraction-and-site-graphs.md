# State abstraction and site graphs

Sources: R1, with root checks (✓). Covers prior art, "is this the same state?", hidden state,
exploration safety, and staleness.

## Prior art — what each system actually builds

| System | Node | Edge | Persisted cross-episode graph? | Result |
|---|---|---|---|---|
| **Environment Maps** ✓ (2603.23610) | Structured map built from 179 human recordings | — | **Yes**, per site | WebArena 14.2 → 23.3 (raw traces) → **28.2** (map) |
| NNetNav (2410.02907) | Flattened DOM/a11y within one episode | Prompted exploration policy, persona-seeded | No — explore → relabel → SFT data | Llama-3.1-8B 16.3% WebArena |
| Agent Workflow Memory (2409.07429) | — (flat NL workflows) | — | No (procedure memory) | +24.6% rel. Mind2Web, +51.1% rel. WebArena |
| Go-Explore (1901.10995) | Archive cell | Implicit | Yes, but **requires a resettable simulator** | Atari, not web |
| LASER (2309.08172) | **Hand-authored** abstract states | State-specific actions + backtrack | Per-domain, manual | WebShop |
| Explorer (2502.11357) | — | — | No; 94K independent trajectories at ~$0.28 each; halts on CAPTCHA/login/payment | Training data |
| Agent-E (2407.13032) | — | — | No; before/after DOM "change observation" | WebVoyager +10–30% |
| WILBUR (2404.05902) | — | — | No; live backtracking, learned demo ranker | 52.6% WebVoyager ✓ |
| ASI / SkillWeaver / AppAgentX | — (flat program/skill library) | — | Library, not graph | SkillWeaver +31.8% / +39.8% rel. |
| ExACT R-MCTS (2410.02052) | MCTS node (not deduplicated) | — | No | VWA +6–30% rel. |
| WebDreamer (2411.06559) | Simulated next-page description | — | No; simulate instead of execute | 4–5× cheaper than tree search |
| Koh et al. tree search (2407.01476) | Observation | Action; backtrack = **reset + replay** | No | WebArena 19.2%, VWA 26.4% |
| AriGraph (2407.04363) | Entity/relation triplets + episodic memory | Relations | Yes, but TextWorld, not web | — |
| Web Agents with World Models (2410.13232) | Predicts **transition-focused** abstraction of next observation | — | No | Evidence that full-page representations are too redundant |

**Recharacterization:** NNetNav is prior art for the *exploration policy*; AWM and skills are prior
art for *P2 (tools/options)*; none builds a site graph. **The two-layer type/instance graph with
affordance edges is not published anywhere found.** Every assumption under it has support
(clustering, wrapper induction, LASER's hand-built types, WMA's compression), but it's an untested
combination.

## "Same state?" — the web-testing literature already solved parts of this

- **Crawljax** (Mesbah et al., TWEB 2012) models an Ajax app as a state-flow graph. Node identity is a
  configurable **state abstraction function**. Its **oracle comparator pipeline** strips volatile
  substrings (timestamps, ads, tokens) before comparison, but the stripping rules are hand-tuned per site.
- **Named, swappable abstraction functions:** StrCmp, Gestalt, RTED, PDiff, WebEmbed, Judge
  (empirical study 2606.16650). Key finding: **fine-grained abstractions favor model-based/BFS
  exploration; compact ones favor RL.** Coverage correlates only weakly with failure-finding, so
  validate identity schemes on the downstream task, not coverage.
- **WebEmbed** (2306.07400): a Siamese transformer embedding; +56% average F1 on near-duplicate
  detection, +6–21% coverage.
- **Judge** (TOSEM): contrastive abstraction, reported most effective. Full text returned 403.
- **LLM semantic labels** as identity: no source uses them as a primary key. Use them for display only.
- **URL canonicalization:** treated as standard crawl practice, not a research contribution. URL-only
  identity structurally fails for SPAs.

## Hidden state (not in the URL)

- Modals, filters, cart, and auth are **not factored anywhere in the literature**. Systems fold them
  into DOM hashing and accept the fine-vs-coarse tradeoff.
- Infinite scroll has no dedicated treatment found. SPA routing's standing answer is to drive a real
  browser and treat DOM events as transitions.
- **Project design (D5):** keep hidden state out of node identity. Model it as an **episode context
  vector** `{auth, cart_nonempty, filters, modal_open}` that edges check as **preconditions**.
- Open risk: wizard steps, A/B buckets, and feature flags don't enumerate cleanly.

## Proposed node identity and edge schema (D5)

1. **Primary key** = (URL template, volatile-stripped DOM-skeleton hash of tag + role + structural path).
2. **Embedding** is used only to merge over-split nodes, with reviewed merges.
3. **Type layer** = clustering over instances. The LLM names types for display; a type holds the
   union of affordances.
4. Hidden state → episode context → edge preconditions.

```
edge = { source_type, source_instance, target_type, target_instance,
         affordance: {role, accessible_name, structural_path},     # never coordinates
         action: {type, params},
         preconditions: {auth, cart_nonempty, filters, modal_open},
         risk_tier: SAFE|LOW|HIGH, reversible,
         success_prob, observed_cost,
         termination_predicate,       # verifies the option; doubles as staleness probe
         last_verified, decay_policy }
```

## Exploration safety

- **Crawlers relied on "GET is safe" for 30 years. A click has no such contract**: Delete and Next are
  both `<button>`. An explicit risk gate is therefore necessary, not optional.
- **State of the art:**
  - **WebGuard** ✓ (2507.14293): 4,939 actions, 193 sites, SAFE/LOW/HIGH tiers. Frontier LLMs score
    <60% accuracy and <60% HIGH recall. Fine-tuned Qwen2.5-VL-7B: **80% accuracy, 76% HIGH recall**
    (up from 37% and 20%).
  - **InferAct:** preemptive critic, up to +20% Macro-F1.
  - **SeerGuard, CORA:** mobile; CORA gives conformal risk guarantees.
  - **Magentic-UI Action Guard:** heuristic + LLM judge routing to a human.
  - **Koh et al.** name the destructive-action classifier as unsolved future work.
  - **WebDreamer** avoids the problem by simulating.
- **Project design (D6):** a 76% recall classifier is a gate, not a safeguard. **HIGH-risk edges are
  excluded from exploration**; they run only when a task deliberately targets them, after a
  first-traversal confirmation.
- **Resets:** Go-Explore and tree search need them. WebArena provides them; the live web doesn't.

## Staleness

- **Wrapper maintenance** (schema-guided repair) is the most mature analogue.
- **Crawljax practice** is re-crawl and diff under the same abstraction function.
- **Change-detection tooling** (e.g. changedetection.io) schedules revisits by each page's observed
  change frequency.
- **Nothing agent-specific found** [unverified].
- **Design:** a failed termination predicate during normal use is the free staleness signal.
  Scheduled re-verification covers low-traffic types, at a rate set by observed drift.
