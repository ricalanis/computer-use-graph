# The action-space ladder

"Do agents use mouse and keyboard, actions, or curl?" All of them. They are rungs of one ladder,
and real systems select rungs per call. Sources: `docs/01-foundations.md` §2 and R0.

## The rungs

| # | Layer | Agent emits | Executed by |
|---|---|---|---|
| 0 | OS input events | `click(842,316)`, `type`, `key` | xdotool / pyautogui / CGEvent — the real cursor moves |
| 1 | Browser input events | Coordinates via CDP `Input.dispatchMouseEvent` | Chrome, tab-scoped, no real cursor |
| 2 | Element-targeted | `click(id=42)`, `click("button:has-text('Submit')")` | Playwright/Selenium: actionability checks → synthesized trusted events |
| 3 | DOM/JS manipulation | `el.click()`, `el.value = "x"` | The page's own JS engine |
| 4 | Accessibility actions | `AXPress(node)` | Platform a11y API (AX, UIA, AccessibilityService) |
| 5 | Semantic / macro | `add_to_cart(sku)` | Script expanding into layer-2 steps |
| 6 | Private network API ("curl") | `POST /api/cart` with page cookies/CSRF | HTTP client |
| 7 | Public API / MCP | `create_issue(...)` | Documented endpoint |

**Governing tradeoff.** Down the ladder buys generality and costs reliability and speed. Up the
ladder buys reliability and speed and costs generality, because every rung above 0 needs an
app-specific **binding** (selector, node id, endpoint) that can go stale. **Grounding doesn't
disappear as you climb; it changes shape:** which pixel → which selector → which endpoint.
The tradeoff is monotone *in expectation on standards-compliant apps*. On poorly instrumented
UIs, layer 4 can be less reliable than layer 2 (R0).

## What real stacks actually do (R0)

| Stack | Agent-facing action | Underneath | Rung(s) |
|---|---|---|---|
| Anthropic computer-use tool (reference impl.) | Pixel `left_click`, `type`, `key`, `scroll` | Xvfb + `xdotool` | 0 |
| OpenAI CUA / Operator | `{"type":"click","x":..,"y":..}` | Playwright mouse (browser) / PyAutoGUI (desktop); also model-written code path | 1 / 0 |
| **BrowserGym** ✓ | `ACTION_SUBSETS`: `bid` = click/fill/select_option/hover/press/drag_and_drop/upload_file…; `coord` = mouse_*/keyboard_* | Playwright for both | **2 and 1, a config switch** |
| browser-use | `click(index)`; coordinate click toggle; `evaluate(code)` | Direct CDP client (`cdp-use`), not Playwright on current main | 2, 1, 3 |
| WebArena native | `click [id]`, `type [id] [text]`, tabs, `goto` | Playwright | 2 (1 alternative) |
| OSWorld | `pyautogui` code or `computer_13` enumerated actions | pyautogui on a VM | 0 (both) |
| AndroidWorld | tap/swipe by coordinate *or* element | AccessibilityService / touch injection | 4 and 0/1 |
| Set-of-marks (WebVoyager) | Mark number on screenshot | Mark → DOM element → driver click | Perception trick over 2 |
| Playwright-MCP | `browser_click({ref:"e5"})` from a11y snapshot | Playwright locator | 2 (a11y-derived refs) |

**Rung is predominantly a harness configuration, not a property of the stack.**

## Three distinctions that resolve most of the confusion

1. **The agent's action space ≠ the executor's.** `click(id=42)` still ends as a mouse event. The
   question is where the line falls between what the model decides and what the harness resolves.
   A high line means a per-site harness, and amortizing that cost is what the graph is for.
2. **Reads and writes belong on different rungs.** Reading the page's own XHR/fetch responses
   (layer 6, read-only) is clean and safe. Writing at layers 3/6 bypasses client validation and
   state machines. **Default: navigate and write at 2, read at 6.** *No published agent harness was
   found describing XHR-response reading as an observation channel* [unverified as prior art].
   Treat it as an undocumented technique and declare it in the method.
3. **What layer 3 actually breaks.**
   - `el.click()` produces `isTrusted: false` events (MDN).
   - Setting `.value` directly bypasses React controlled-input tracking (react#10135).
   - It does *not* bypass CSRF: the page's own submit still carries its token. CSRF cost belongs to
     layer 6.
   - Whether bot detection checks `isTrusted` is [unverified], and moot on self-hosted benchmarks.

## Grounding evidence (why pixel agents are a different experiment)

- **ScreenSpot:** GPT-4V 16.2% average, web icons under 9%. CogAgent 47.4%. SeeClick 53.4%.
- **ScreenSpot-Pro** (professional high-res apps): best prior 18.9%; cascaded visual search 48.1%.
  Current SOTA is still under 60%.
- **OSWorld:** human 72.36% vs best model 12.24%, attributed mainly to grounding and operational
  knowledge. End-to-end, not a controlled action-space ablation.
- A clean same-model element-vs-coordinate ablation was [unverified]. BrowserGym's `bid`/`coord`
  switch ✓ makes that ablation cheap to run ourselves.

## Code-as-action

CodeAct reports up to +20% absolute success and 30% fewer turns, **on API/tool-use benchmarks, not
GUI**. No GUI replication was found, so it's plausible by analogy, not measured. Costs: harder
per-step verification and a sandboxed runtime. Recorded as a road not taken.

## Options / semi-MDP framing

Sutton, Precup & Singh (1999): an option is (initiation set, policy, termination condition). That
is exactly what a graph edge should be. **No GUI/web paper uses this vocabulary.** Workflow-guided
exploration, AWM, and NNetNav do options-like things under other names. Present it as a deliberate
formal import, not as field-standard framing.

Execution model:
```
task goal
  └─ graph lookup → option (layer 5)             ← research object
       └─ element-targeted steps (layer 2)       ← agent action space
            └─ trusted input events (layer 1)    ← harness
```
Try the option, check its termination predicate, and on failure resume per-step reasoning *from
the failure point*.

## Project decision (see decisions D2, D3)

- **Agent action space:** layer 2 over an **actionability-filtered** a11y-tree candidate set.
- **Executor:** Playwright via BrowserGym.
- **Reads:** layer 6 allowed and declared.
- **Writes:** no layer-6 writes.
- **Edges:** layer-5 options.

**Why layer 2:** categorical entropy needs an enumerable candidate set. Coordinates would need
discretizing, and entropy would then be a grid-size artifact.

**What will NOT transfer to pixel agents:**
1. The entropy signal itself.
2. Edge-durability and decay numbers.
3. Cost-per-step ratios. v0.1's "~50×" is unsourced; measure it.
4. Anything about grounding uncertainty.

Scope every claim to DOM-accessible web apps.
