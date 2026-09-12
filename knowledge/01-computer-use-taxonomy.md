# Computer-use taxonomy

Computer use is not one problem. Three orthogonal design axes, five sub-problems that get
conflated, and five task archetypes on which any given technique pays off very differently.
Sources: `docs/01-foundations.md` §1; refinements from R0, R4.

## Axis A — observation (what the model sees)

| Mode | Strength | Weakness |
|---|---|---|
| **Pixels** (screenshot only) | Works on anything rendered: canvas apps, PDF viewers, remote desktops, native apps | Expensive per step; needs visual grounding, which is weak (see note 02) |
| **Text structure** (DOM / accessibility tree) | Cheap, precise, enumerable | Brittle on custom widgets; needs pruning (lossy). The a11y tree can list off-screen or unreachable elements (Playwright issue #39955). |
| **Hybrid / set-of-marks** | Screenshot with numbered overlays on interactable elements; model reasons visually, acts on an index | Resolves to element-targeted execution underneath (WebVoyager) |
| **Programmatic** (API / SDK / MCP) | Fastest, most reliable where available | Arguably not computer use; needs an integration per app |

*Correction carried from R0:* v0.1's "raw trees are frequently 100k+ tokens" has no source. WebArena
says only that the a11y tree is "more compact than the DOM." **Measure it** for the chosen sites.

## Axis B — action space
See [note 02](02-action-space-ladder.md). Families: low-level pixel/keyboard · element-targeted ·
code-as-action · macro/replay. The graph idea is a macro-family technique.

## Axis C — control loop

- **ReAct-style single agent** (observe → think → act). The baseline everyone reports.
- **Planner/executor split**, sometimes with a dedicated grounder. Agent-E adds explicit before/after
  DOM "change observation."
- **Reflection / retry** (Reflexion lineage).
- **Search over states:**
  - Real-environment tree search needs resets. Koh et al. reset and replay to backtrack: WebArena
    19.2%, VisualWebArena 26.4%.
  - Reflective MCTS: ExACT.
  - Simulated search with an LLM as world model: WebDreamer, 4–5× more efficient than tree search at
    comparable performance, explicitly because the web is "rife with irreversible actions."
- **Memory-augmented:** workflows (AWM), demonstrations (WILBUR), skills (ASI, SkillWeaver, WALT,
  PolySkill), maps (Environment Maps ✓). See note 05.
- **Trained:** SFT on synthetic trajectories (NNetNav, Explorer, Synatra) or RL with execution
  rewards (WebRL lineage).

## Five sub-problems hiding inside all of it

1. **Grounding.** Mapping "the blue Submit button" to coordinates or an element. Often the largest
   error source for pixel agents (note 02 has the numbers).
2. **State estimation.** What page am I on, did the last action work, modal or navigation?
   Under-modeled; Agent-E's change observation is one of few explicit treatments.
3. **Verification.** Did the task complete, *including side effects*? Programmatic validators
   under-credit and LLM judges over-credit (note 03).
4. **Memory / transfer.** Across steps, episodes, and sites. Multi-site transfer is essentially
   unsolved: 0/48 in Environment Maps ✓.
5. **Safety.** Prompt injection (WASP, AgentDojo), policy compliance (ST-WebAgentBench), and
   irreversible actions (WebGuard ✓). Note 04 covers exploration safety.

## Task archetypes

| Archetype | Shape | Graph fit |
|---|---|---|
| Read-only information seeking | Navigation- and exploration-heavy, cheap to retry | Friendly |
| Transactional (form fill, purchase, CRUD) | Short navigation, high precision, irreversible | May not amortize |
| Long-horizon multi-app | Email → sheet → internal tool | Hard; per-site maps don't transfer (0/48 ✓) |
| **Authoring / configuration** (settings, admin, deep menus) | Deep affordance trees | **Most graph-shaped.** Empirically where structure beat flat memory: GitLab +11.1pp, CMS +7.1pp ✓ |
| Repeat / routine | Same template, N times | Where amortization should dominate. WorkArena L1 is this regime. |
