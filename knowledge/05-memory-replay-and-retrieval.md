# Memory, replay, and retrieval

Sources: R2 (including the flat-memory addendum), R5 §8, and root checks (✓).

## Does agent memory help? Yes — but check the baseline

| System | Stored | Benchmark | Result | **Beat what** |
|---|---|---|---|---|
| AWM | Induced NL workflows | Mind2Web, WebArena | +24.6% / +51.1% relative | No memory; vs Synapse +5.0 elem-acc / +4.0 step-SR (structured vs structured) |
| Synapse | State-abstracted exemplar trajectories | Mind2Web, MiniWoB++ | Ablation ladder +32/50/56% step-SR; 99.2% MiniWoB++ | Its own weaker rungs; no raw-trajectory rung |
| **WILBUR** ✓ | Ranked demos + synthesized advice | WebVoyager | Zero-shot 34.4 · +Backtrack 40.6 · **+flat demos 48.4** · +Synthesis 49.9 · full 52.6 | **Has a flat rung** |
| **ExpeL** | Insights and/or raw trajectories | ALFWorld, WebShop, HotpotQA | Flat retrieve-only ≥ insights on ALFWorld (55 vs 50) and WebShop (38 vs 37) | **Has a flat rung** |
| SkillWeaver | Self-discovered skill APIs | WebArena, live | +31.8% / +39.8% relative; transfer up to +54.3% | No skills; names flat demos as prior art but doesn't run them |
| WALT | Verified per-site tools | WebArena | +9 points over ASI | Skill baselines |
| PolySkill | Cross-site polymorphic skills | Web splits | +9.4% cross-task, +3.2% cross-domain over ASI | Skill baselines |
| **Environment Maps** ✓ | Map from human trajectories | WebArena (812) | 14.2 → **23.3 raw traces** → 28.2 map | **Has a flat arm** |
| Voyager | Code skill library | Minecraft | 3.3× more unique items | Ancestor, not web |
| Mem0 | Extracted memories | LoCoMo, LongMemEval | 92.5 / 94.4 | **Conversational QA, not GUI evidence** |

### Flat vs structured — the load-bearing result

Where a flat-memory baseline exists, **flat memory takes about two-thirds of the win**:

| Paper | Flat share of gain | Status |
|---|---|---|
| Environment Maps | 9.1 of 14.0pp (65%) | ✓ |
| WILBUR | 7.8 of 12.0pp over +Backtrack (65%) | ✓ |
| ExpeL | ≥100% on ALFWorld and WebShop | worker |

AWM, Synapse, and SkillWeaver never run a flat baseline, so their wins are untested against the
cheap alternative. **No paper runs flat-vs-structured on WebArena/Mind2Web with controlled budgets.**
That gap is this project's to fill.

Broader memory literature:
- **Infini Memory:** structural maintenance is worth +6.7pp on LongMemEval (76.0 vs 69.3).
- **RAGSearch:** GraphRAG +27.23 on multi-hop but only +0.47 on general QA; agentic dense RAG narrows
  the gap; Graph-R1 is 2.01 below flat Search-R1 on NQ.
- **Pattern:** structure wins on multi-hop, relational, and cross-reference tasks, and is marginal
  elsewhere. That is consistent with configuration-heavy sites benefiting most.

**Don't cite GraphRAG as "graphs beat flat."** Against references, its global search underperforms
plain RAG ✓: ROUGE-2 3.23 vs 6.32 on QMSum, 6.99 vs 10.08 on SQuALITY. LLM-judge position bias
produced "substantially different, and in some cases opposite, judgments" ✓.

## Macro / workflow replay

- **Repeatability is rare:** GPT-4 is consistent on only 4/61 WebArena templates (2510.23883).
- **Compounding:** 95% per step over 10 steps gives ~60% end-to-end.
- **RPA, 15 years of this:** UI changes are the primary cause of robot failures, and ~50% of developer
  time goes to fixes. UiPath's Healing Agent rebinds semantically on selector failure (reported
  60–70% maintenance reduction, vendor claim).
- **Convergent LLM-era architecture**, reinvented four times (2025–26):

  | System | Mechanism |
  |---|---|
  | Muscle-Mem | Replay on a recognized state; cache miss → agent |
  | PreAct | Cached sequences; divergence → reason for the diverging steps only |
  | Agentic Compilation | Compile to script; divergence → "lazy replanning" from the failed step |
  | SkillDroid | Weighted multi-attribute locator + per-step checker; "speculative replay" |

  The shared shape: cache → cheap per-step check → **resume from the failure point**. **All four gate
  on binary divergence; none uses a continuous uncertainty signal.**
- **Failure modes:** layout change, renamed elements, dynamic content changing what "next" means,
  compounding perception errors, and **false-positive step checks** (the replay "succeeds" against the
  wrong state). That last one is why the termination predicate must be independent of the replay engine.

## Graph tools — do LLMs traverse or flail?

- **GraphWalk** (2604.01610): without tools, models fixate on the first few relationships. With tools,
  80–100% on mazes. **Single-hop works; variable-hop path queries fail catastrophically.**
- **ToolMaze/AgentTether:** complex tool topologies trap agents in trial-and-error loops, and recovery
  drops ~37% under implicit semantic failures.
- **Consequence (D7):**
  - `search()` for entry points.
  - Single-hop `neighbors()`.
  - `path()` returns a **pre-computed** option or `None`, never a live multi-hop walk.

## Context budget

- **Lost in the Middle:** more than 30% degradation when the answer is mid-context.
- **Context Rot** (Chroma, 18 models):
  - Degradation grows with length, faster when the relevance is inferred rather than literal.
  - **A single distractor hurts.**
  - ~300-token focused prompts far outperform ~113k-token full prompts.
  - Coherent context can hurt more than shuffled context.
- **Anthropic guidance:** use the smallest high-signal set and just-in-time retrieval; a worked
  example uses a 3K-token budget for a tool-heavy agent.
- **No benchmark-derived optimum for tool-return size.** Make it an experimental variable and default
  to small k.

## Verifying macro execution

Three families, each validated individually, never combined for replay:

| Family | Tradeoff |
|---|---|
| Visual/screenshot judgment | Another LLM call and another judge to trust |
| **State-predicate assertion** (VeriSafe Agent) | Cheap and checkable, but you must know what to assert; this is the termination predicate |
| Independent verifier (VLAA-GUI completion gate) | Most robust, double cost |

"Where Did It Go Wrong?" compares runs at shared semantic states to localize divergence, which makes
a good audit-trail design.

## Tool API (D7)
```
search(goal_text, k=5) -> [NodeSummary]
neighbors(node_id) -> [Affordance]
path(from, to) -> Macro | None
execute_macro(macro) -> {status: success | diverged_at_step_i | failed, completed_steps, divergence_evidence}
landmarks() -> [NodeSummary]
record(observation, outcome) -> None
```
Returns are token-capped. `execute_macro` checks the termination predicate after every step and
resumes from step *i*. Its check is the one seam where a continuous signal could replace the binary one.
