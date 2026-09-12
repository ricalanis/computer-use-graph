# R0 — Substrate / Action-Space Layers

**Worker:** R0. **Scope:** verify, correct, and deepen §1.2 and §2 of `docs/01-foundations.md` (the
action-space ladder). Method note: this pass used WebSearch until the session's search budget was
exhausted mid-task, after which verification continued via WebFetch, `curl` against arXiv's API,
Semantic Scholar's API, and raw GitHub source. Every claim below is either sourced with a URL that
was actually retrieved, or marked `[could not verify]` with what was searched. No citation is
invented.

---

## 1. Comparison table — agent-emitted action → harness translation → underlying mechanism

The single biggest correction this table forces on §2's framing: **most real systems are not "on
one rung."** The ladder is real, but production harnesses expose *several rungs as a configuration
choice* and often mix rungs within one session. Evidence for that claim is in the table itself
(BrowserGym, browser-use, AndroidWorld all do this explicitly).

| Agent / Stack | Agent-emitted action (example) | Harness translation | Underlying event mechanism | Ladder rung(s) | Source |
|---|---|---|---|---|---|
| **Anthropic computer-use tool** | `left_click({coordinate:[x,y]})`, `type`, `key`, `scroll` — 17 sub-actions, all in full-screenshot pixel space | App-supplied "action handler" translates tool calls into environment actions; Anthropic's own docs deliberately abstract this so any environment can be plugged in | Reference implementation (`anthropic-quickstarts`/`claude-quickstarts` computer-use-demo) runs a virtual X11 display (Xvfb) + Mutter/Tint2 desktop and shells out to `xdotool` to move/click the mouse | **0** (reference impl); docs leave 0/1 open depending on integrator | [Computer use tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool); [computer.py using xdotool](https://github.com/anthropics/claude-quickstarts/blob/main/computer-use-demo/computer_use_demo/tools/computer.py) |
| **OpenAI computer-use-preview / Operator (CUA)** | `{"type":"click","x":405,"y":157}`, `type`, `scroll`, `keypress`, `wait`, `screenshot` | "Your action handler translates these requests into browser or operating system input." Sample app uses **Playwright** for the browser case and **PyAutoGUI** for desktop | Playwright's low-level mouse API (coordinate dispatch, not element-targeted) or PyAutoGUI's OS-level synthetic input | **1** (browser sample) / **0** (desktop sample). OpenAI also documents a "code execution" path where the model itself writes Playwright/PyAutoGUI code (code-as-action wrapping rung 0/1) | [OpenAI computer-use guide](https://developers.openai.com/api/docs/guides/tools-computer-use); [Computer-Using Agent announcement](https://openai.com/index/computer-using-agent/) |
| **BrowserGym / AgentLab (ServiceNow)** | Configurable per experiment. `"bid"` subset: `click('a51')`, `fill('b12','text')`, `select_option`, `hover`, `drag_and_drop`. `"coord"` subset: `mouse_click(x,y)`, `keyboard_type`. `"nav"` subset: `goto(url)`, `go_back` | The `bid` (browsergym-id) subset resolves an accessibility-tree-derived id to a live element and calls Playwright locator methods; the `coord` subset dispatches raw mouse/keyboard ops | Playwright (`page: playwright.sync_api.Page` is a global in the action-execution module) for both subsets — the difference is *what the agent references*, not the executor | **2** (`bid` subset) and **1** (`coord` subset), selectable via `ACTION_SUBSETS` — this is the clearest direct evidence that "rung" is a harness config knob, not an intrinsic property of a stack | [BrowserGym repo](https://github.com/ServiceNow/BrowserGym); source: `action/highlevel.py` and `action/functions.py` (`ACTION_SUBSETS = {"bid": [...], "coord": [...], "nav": [...]}`, fetched from `raw.githubusercontent.com/ServiceNow/BrowserGym/master/browsergym/core/src/browsergym/core/action/{highlevel,functions}.py`); [BrowserGym Ecosystem paper](https://huggingface.co/papers/2412.05467) |
| **browser-use** | `click(index=42)` (element index from a DOM/AX snapshot) by default; `click_by_coordinate` when `set_coordinate_clicking(True)`; `evaluate(code)` for raw JS | `_click_by_index` looks up the node in a selector map built from the page's DOM/AX snapshot, then dispatches a `ClickElementEvent` through the library's own event bus | Current main branch depends on **`cdp-use`** (a direct Chrome DevTools Protocol client), **not Playwright** — this contradicts most blog-level descriptions of browser-use as "Playwright-based," which describe older versions | **2** (index click), **1** (coordinate click), **3** (raw `evaluate`) — all three exposed as first-class actions in one library | [browser-use repo](https://github.com/browser-use/browser-use); source: `tools/service.py` (`_click_by_index`, `_click_by_coordinate`, `set_coordinate_clicking`, `evaluate`) and `pyproject.toml` (`"cdp-use==1.4.5"`), fetched from `raw.githubusercontent.com/browser-use/browser-use/main/...` |
| **Playwright/Selenium-driven agents generically** | `page.click(selector)` | Playwright performs **actionability checks** before acting: element is *visible* (non-empty box, not `visibility:hidden`), *stable* (same bounding box for 2 animation frames), *receives events* (is the actual hit-target, not occluded), *enabled* — then dispatches | CDP `Input.dispatch*Event` — produces `isTrusted: true` events indistinguishable from a real user at the DOM level | **2** | [Playwright actionability docs](https://playwright.dev/docs/actionability) |
| **WebArena native action space** | `click [1582]` (accessibility-tree element id), plus coordinate variant, `type [id] [text] [enter_flag]`, `press`, `scroll`, tab ops (`tab_focus`, `new_tab`, `tab_close`), URL ops (`goto`, `go_back`, `go_forward`) | The paper's own harness resolves the id against the accessibility tree and issues the corresponding Playwright/Selenium call; raw HTML/DOM is available as an alternate, "less compact" observation but WebArena doesn't publish token-count numbers for either | Playwright | **2** (id-based) primary; **1** (coordinate) as an alternative | [WebArena paper, arXiv](https://arxiv.org/html/2307.13854v4); [WebArena repo](https://github.com/web-arena-x/webarena) |
| **OSWorld** | Two configurable action spaces: `"pyautogui"` — the agent emits literal Python using `pyautogui.click(x,y)` etc.; `"computer_13"` — a fixed enumerated set of pixel/coordinate actions designed by the authors | Executed directly as Python/pyautogui calls against a real VM desktop | pyautogui → OS-level synthetic input (X11/Windows/macOS input injection) | **0** for both subsets — even the "structured" `computer_13` space is still coordinate-based, it is *not* element-targeted | [OSWorld paper, arXiv](https://arxiv.org/abs/2404.07972); [OSWorld repo](https://github.com/xlang-ai/OSWorld) |
| **AndroidWorld** | JSON actions: `tap`, `swipe`, `type`, `navigate_home`/`navigate_back`, all referencing either screen coordinates *or* a UI element description | Description mentions **both** coordinate gestures and elements derived from the **Android accessibility tree** (each element has text/position/status derived from `AccessibilityNodeInfo`-equivalent metadata); dispatched as synthetic touch/gesture events | Android's `AccessibilityService` gesture-dispatch API and/or direct touch injection | **4** (a11y-node reference) and **0/1** (raw coordinate tap) simultaneously available | [AndroidWorld paper, arXiv](https://arxiv.org/html/2405.14573v4); [android_world repo](https://github.com/google-research/android_world) |
| **Set-of-Marks web agents (WebVoyager)** | The model emits a **mark number** overlaid on a screenshot (e.g. "click [7]") | A JS tool ("GPT-4V-ACT," explicitly credited as inspired by Set-of-Mark prompting) segments the rendered page, overlays numbered boxes on interactive DOM elements, and maps the chosen mark back to its underlying DOM element for execution | The resolved DOM element is then clicked via the browser driver (Selenium/Playwright) | Agent-facing action space is visually-indexed but **resolves to layer 2** — SoM is a perception/indexing trick layered on top of an element-targeted executor, not a new execution rung | [Set-of-Mark Prompting paper, arXiv](https://arxiv.org/abs/2310.11441); [WebVoyager paper, arXiv](https://arxiv.org/pdf/2401.13919) |
| **MCP / Playwright-MCP (Microsoft)** | `browser_snapshot` returns an accessibility-tree snapshot with per-node `ref` ids (`ref="e5"`); `browser_click({element: "Submit button", ref: "e5"})` | Explicitly documented: "Playwright MCP uses Playwright's accessibility tree, not pixel-based input... requires no vision models, operating purely on structured data" | Playwright locator resolved from the ref → real dispatched input events, same actionability checks as any Playwright script | **2**, with the *element-identification* channel itself borrowed from the a11y tree (a taste of **4** for perception, **2** for execution) | [Playwright MCP intro](https://playwright.dev/mcp/introduction); [microsoft/playwright-mcp repo](https://github.com/microsoft/playwright-mcp) |

**Cross-cutting observation not in the current §2 table:** three of the ten systems surveyed
(BrowserGym, browser-use, AndroidWorld) expose *multiple rungs as a runtime switch inside the same
codebase*, and OpenAI's own guide documents a fourth mode (model-authored Playwright/PyAutoGUI code)
that wraps rung 0/1 inside rung "code-as-action." §2's table implies one rung per system; the
correction is that **rung is predominantly a per-call or per-experiment configuration decision, not
a fixed property of the stack** — which is good news for §2.4's own decision (layer 2 is readily
selectable in the tooling this project would likely adopt, e.g. BrowserGym) but bad news for citing
any one system as "the" example of a rung.

---

## 2. Reliability/cost gap: coordinate (pixel) vs element-level actions

**Grounding accuracy (ScreenSpot family):**

| Model | ScreenSpot avg. accuracy | Notes |
|---|---|---|
| GPT-4V (general VLM, zero-shot) | **16.2%** (mobile text 22.6% / icon 24.5%; desktop text 20.2% / icon 11.8%; web text 9.2% / icon 8.8%) | Web-icon grounding is the hardest single category, under 9% |
| CogAgent | **47.4%** | Purpose-built GUI grounding model |
| SeeClick (fine-tuned specialist) | **53.4%** | Mobile 78.0%/52.0% (text/icon), desktop 72.2%/30.0%, web 55.7%/32.5% |

Source: [SeeClick paper, arXiv 2401.10935](https://arxiv.org/pdf/2401.10935) (which introduces
ScreenSpot). This is a direct, citable measurement of the "grounding does not disappear, it changes
shape" claim in §2.1: a general-purpose model asked to point at *pixels* fails 5-6 out of 6 times
on icons.

**ScreenSpot-Pro (high-resolution professional software):** best existing grounding model achieves
only **18.9%**; the paper's own proposed cascaded visual-search method reaches **48.1%** without
additional training. Source: [ScreenSpot-Pro paper, arXiv 2504.07981](https://arxiv.org/abs/2504.07981).
This is important evidence for §2.4's stated reason for deferring layer 0 ("grounding error there is
large enough to swamp the graph signal") — the failure rate *gets worse*, not better, as resolution
and UI density increase, which is directionally exactly the professional-SaaS-admin case §1.5 calls
"transactional."

**End-to-end pixel/OS-level task success vs. humans:** OSWorld reports human performance at
**72.36%** of tasks vs. the best evaluated model at **12.24%**, attributing the gap "primarily" to
GUI grounding and operational knowledge. Source: [OSWorld paper, arXiv 2404.07972](https://arxiv.org/abs/2404.07972).
This is an end-to-end number (not an isolated action-space ablation — OSWorld does not publish a
controlled a11y-tree-only vs. pixel-only ablation table in what was retrievable this session), so
treat it as circumstantial support, not a clean causal isolation of the action-space variable.

**Element-level vs. pixel-level agent success, direct comparison:** [could not verify] a clean,
single-paper, same-model ablation of "element-id action space" vs. "coordinate action space" with a
success-rate delta on the same benchmark. What is available (NNetNav, arXiv 2409.19669-family;
fetched via arXiv API, abstract only) reports an a11y-tree-based fine-tuned Llama-3.1-8B reaching
**16%+ success on WebArena**, "outperforming zero-shot GPT-4" — but the exact action-space modality
of that GPT-4 baseline was not independently confirmed this session, so this is suggestive, not
proof, of the isolated action-space effect. Flag as a specific, well-scoped follow-up for R4/R5
(who own benchmark ablation tables) rather than claim it here.

**Tokens/latency per step:** [could not verify] a specific number. WebArena's own paper states only
qualitatively that the accessibility tree is "more compact than the DOM representation," with no
token counts given (confirmed by direct read of [arXiv 2307.13854v4](https://arxiv.org/html/2307.13854v4)).
The foundations doc's claim that "raw trees are frequently 100k+ tokens" (§1.2) is plausible from
general practitioner experience but **is not sourced by the paper it would most likely draw from**,
and no other source for that specific figure was found this session — flagged under corrections
below.

---

## 3. The trusted-events problem

**`Event.isTrusted` is the actual, documented mechanism, and it is binary, not fuzzy.** Per MDN:

> "The `isTrusted` read-only property of the `Event` interface is a boolean value that is `true`
> when the event was generated by the user agent (including via user actions and programmatic
> methods such as `HTMLElement.focus()`), and `false` when the event was dispatched via
> `EventTarget.dispatchEvent()`. The `click` event fired through `HTMLElement.click()` sets the
> `isTrusted` property to `false`."

Source: [MDN, Event.isTrusted](https://developer.mozilla.org/en-US/docs/Web/API/Event/isTrusted).

This confirms precisely the §2 table's layer-3 row: calling `el.click()` in JS is **not** merely a
"different way to click" — it produces an event object that is programmatically distinguishable
from a real click at the platform level, before any application code even runs.

**Why Playwright doesn't just call `.click()`:** Playwright's actionability model (visible, stable,
receives-events, enabled — [playwright.dev/docs/actionability](https://playwright.dev/docs/actionability))
exists specifically so that, once checks pass, Playwright dispatches through CDP's input pipeline
rather than the page's JS — producing `isTrusted: true` events that any listener, native form
validation, or anti-automation check sees as indistinguishable from a real user. The docs page
itself documents the checks but (as fetched) does not spell out the trusted-event rationale in those
exact words; that inference is drawn from the isTrusted mechanism above plus the checks' evident
purpose (replicating what a human could actually do — e.g. "receives events" exists precisely to
stop a script from clicking through an overlay a real cursor could not reach).

**React controlled-input value tracking:** this is a real, long-documented gotcha — confirmed to
exist via React's own issue tracker, [facebook/react#10135, "dispatchEvent is ignored on
input/textarea elements"](https://github.com/facebook/react/issues/10135) — but this session's
WebFetch could only retrieve the issue's title/metadata, not the full comment thread, so the exact
technical wording of React's explanation (the native-setter/value-tracker workaround) is **not
independently quoted here**; treat the mechanism description as well-known engineering folklore
confirmed to be a real, tracked React issue, not as a verbatim-sourced quote.

**Bot detection checking `isTrusted` or synthetic-event fingerprints:** [could not verify]. This
session's WebSearch budget was exhausted before a targeted search against Cloudflare/PerimeterX/
DataDome/Akamai documentation could be run, and an arXiv abstract search for `"trusted events" AND
"bot detection"` returned zero results. This is a real, frequently-discussed-in-practice technique,
but it is **not confirmed by any source retrieved this session** — do not cite it as established
without a follow-up pass.

**CSRF — important precision the foundations doc should sharpen, not necessarily an error:**
§2.2's point 3 attributes CSRF-token rotation cost specifically to **layer 6** (private-API
forging), which is the correct rung to blame. It would be a mistake to read that as implying
layer-3 DOM manipulation (`el.value = x`, `el.click()`) bypasses CSRF — it does not, and does not
need to: a layer-3 write still triggers the page's own real form-submission or `fetch()` call,
which carries whatever CSRF token the page's own JS already embedded (e.g., a hidden input or a
cookie the app reads at submit time). What layer 3 actually breaks is (a) the React/controlled-
component value-tracking problem above, and (b) the `isTrusted` gate on any listener that checks
it — not the CSRF flow itself. This is a clarification of the doc's already-correct rung
attribution, not a contradiction of it.

---

## 4. Code-as-action

**CodeAct** (Wang et al., ["Executable Code Actions Elicit Better LLM Agents," arXiv
2402.01030](https://arxiv.org/abs/2402.01030), ICML 2024; [repo](https://github.com/xingyaoww/code-act)):
reports **up to 20% higher absolute success rate** over JSON/text-action baselines on
M³ToolEval (82 human-curated multi-turn tasks) and **up to 30% fewer actions/turns**.

**Important scope caveat, directly relevant to §1.2's claim:** CodeAct's evaluation domains are
general **API/tool-use agents** (API-Bank, M³ToolEval) — general-purpose Python execution against
APIs and tools, not browser/GUI action spaces. §1.2 asserts code-as-action as a family on the GUI
action-space ladder ("emit a Playwright/Python snippet per step") and claims an "efficiency win
(loops, batching)" — that claim is a reasonable **extrapolation** from CodeAct's general result, but
**no GUI/browser-specific paper reproducing CodeAct's ablation was found this session**. The
concrete evidence that GUI harnesses *do* expose a code-as-action affordance is browser-use's
`evaluate(code)` action (raw JS per step, confirmed above) and OpenAI's documented "model writes
Playwright/PyAutoGUI code" integration path — but neither of those sources reports a controlled
efficiency/success-rate comparison against discrete-action baselines specifically for GUI tasks.
**Treat "code-as-action wins for GUI agents" as plausible-by-analogy, not measured.**

Caveats CodeAct's own framing implies (and that generalize straightforwardly to GUI code-as-action):
harder to verify per-step (a multi-line snippet can partially succeed, partially fail, or have side
effects before erroring), and executing model-generated code requires a sandboxed runtime — the
CodeAct reference implementation runs in per-session Docker containers (confirmed from the repo's
own README description of its chat-UI demo architecture,
[xingyaoww/code-act](https://github.com/xingyaoww/code-act)), which is itself a real infrastructure
cost the discrete-action alternative doesn't pay.

---

## 5. The options/semi-MDP framing

**Canonical citation, confirmed:** Sutton, R. S., Precup, D., & Singh, S. (1999). "Between MDPs and
Semi-MDPs: A Framework for Temporal Abstraction in Reinforcement Learning." *Artificial
Intelligence*, DOI [10.1016/S0004-3702(99)00052-1](https://doi.org/10.1016/S0004-3702(99)00052-1).
Confirmed via the Semantic Scholar API (paper id `0e7638dc16a5e5e9e46c91272bfb9c3dd242ef6d`; DBLP key
`journals/ai/SuttonPS99`), which returned exactly this title/author/venue/year tuple. §2.3's citation
is correct.

**Is the options/semi-MDP framing applied, explicitly, to GUI or web agents anywhere published?**
Searched (via arXiv's API, after the WebSearch budget was exhausted): `"options framework" AND
"agent"`, `"hierarchical reinforcement learning" AND "web agent"`, `"options" AND "web navigation"`,
`"macro actions" AND "GUI"`, `"subgoal" AND "browser agent"`. Result: **no hit that is both (a) an
options/semi-MDP or HRL paper and (b) about GUI or web agents.** The `"options framework" AND
"agent"` search returned exclusively pure-RL papers (option-critic variants, safe option-critic,
multi-agent options for robotics/traffic) — none GUI-adjacent.

What *does* exist, doing conceptually options-like things without the formalism:
- Liu et al., ["Reinforcement Learning on Web Interfaces Using Workflow-Guided Exploration," arXiv
  1802.08802](https://arxiv.org/abs/1802.08802) (2018) — induces "workflows" from demonstrations
  that constrain the allowable action sequence at each step (a policy operating under an
  initiation/termination-like constraint), evaluated on the World of Bits/MiniWoB lineage. The
  abstract text retrieved does not use "option" or "semi-MDP" terminology.
- ["Agent Workflow Memory," arXiv 2409.07429](https://arxiv.org/abs/2409.07429) — the exact paper
  §1.3 of the foundations doc already names as the nearest neighbor to this project. Same
  observation: workflow/macro framing, no options-formalism language in the abstract.
- ["NNetNav," arXiv](https://arxiv.org/abs/2410.02907) (title confirmed: "NNetNav: Unsupervised
  Learning of Browser Agents Through Environment Interaction in the Wild") — exploits "the
  hierarchical structure of language instructions" to decompose complex instructions into
  sub-tasks; again hierarchical in spirit, not couched in options/semi-MDP terms.

**Assessment: (c), essentially absent as an explicit formalism**, with the practice (workflow
induction, skill/macro libraries, hierarchical instruction decomposition) common. §2.3's move —
explicitly importing the Sutton-Precup-Singh options/semi-MDP vocabulary (initiation set, policy,
termination condition) to describe a graph edge — is a **legitimate but non-standard theoretical
framing for this specific subfield**. It is not naive (the formalism fits cleanly: a macro *is*
initiation-set + policy + termination-predicate, and the doc's own "termination predicate" language
in §2.5/P1 already borrows the right piece), but the doc should not present it as "the" standard
citation practitioners use — the field's own papers describing the same mechanism reach for
"workflow," "skill," or "macro," not "option." This is worth being explicit about since a reviewer
who works in HRL would immediately ask "why isn't this cited as options" of the *existing* web-agent
literature, and the honest answer is that literature mostly doesn't.

---

## 6. Read-at-layer-6/write-at-layer-2 hybrid

**Does anyone publish intercepting the page's own XHR/fetch responses as an agent observation
channel?** Searched arXiv abstracts for `"network requests" AND "web agent" AND "observation"` and
`"API responses" AND "web agent"` — **zero results either way.** This is a real, mechanically
supported capability of the tooling this project would use (Playwright's `page.on("response")` and
the CDP `Network` domain are documented, general-purpose framework features — not fetched fresh this
session but well-established and uncontroversial), but **no published agent-harness paper using it
as a described observation-construction technique was found.** §2.2's point 2 and §2.4's "reads may
use layer 6" decision are therefore **not corroborated by prior published work** — they describe a
mechanically sound, low-risk technique that appears to be either genuinely novel in this context or
simply undocumented as a distinct design choice in papers (as opposed to being buried, unremarked,
in some harness's implementation). Flag as `[could not verify — likely an underexplored but
mechanically uncontroversial technique]`, not as validated prior art.

**Ethics/ToS discussion of request forging by agents:** the safety-benchmark papers the foundations
doc already names were checked directly:
- [ST-WebAgentBench, arXiv](https://arxiv.org/abs/2410.06703) (confirmed abstract: 222 tasks scored
  on six safety/trustworthiness dimensions, introduces "Completion Under Policy" metric) — focused
  on policy compliance (consent, robustness), not specifically on request forging or ToS.
- [WASP, arXiv](https://arxiv.org/abs/2504.18575) (confirmed abstract: end-to-end prompt-injection
  benchmark for web agents) — focused on injection attacks, not request-forging ethics.

Neither directly addresses "is an agent making API calls a site didn't intend for programmatic
callers a ToS or ethical problem." **No paper making that argument explicitly was found this
session** ([could not verify]; the WebSearch budget ran out before a broader, non-arXiv-restricted
search of legal/ethics-of-scraping literature could be attempted, which is where such a discussion
would more likely live than in an ML safety benchmark paper). §2.2's point 3 on this topic should be
read as the authors' own reasoned position, not as summarizing an established literature consensus.

---

## 7. Verdict on §2.4: is layer-2/Playwright/a11y-tree the right substrate for an uncertainty
   experiment?

**The case for (layer 2 is close to correct):**
- The table evidence above shows layer 2 is where the *field's actual infrastructure* already
  lives: WebArena's native action space is id-based (layer 2 primary), BrowserGym's `bid` subset is
  layer 2 on top of Playwright, and Playwright-MCP is a pure layer-2/a11y hybrid. Adopting layer 2
  means adopting, not reinventing, the field's harness — directly consistent with §3.2's own
  recommendation to "adopt rather than write our own runner."
- §2.5's P3 argument (enumerable candidate set → well-defined categorical entropy) is *the*
  strongest argument in the whole document and it is not weakened by anything found this session:
  ScreenSpot's own numbers (§2 above) show that pixel-coordinate grounding is not merely "harder,"
  it fails in a way (9-25% accuracy for a general VLM) that would make any per-step distribution
  over "the next pixel" dominated by grounding noise rather than genuine task-level uncertainty.
  Layer 0's uncertainty signal would be contaminated by a *different, better-studied* problem
  (grounding) that the field already has its own benchmarks for (ScreenSpot family) — conflating
  the two would make P3's central claim (surprisal-as-control-signal) uninterpretable.
- Playwright's actionability semantics (confirmed above) give layer 2 a genuine reliability
  advantage that is not just theoretical: real trusted events, real hit-testing, and — critically —
  synchronization with whatever the *page itself* considers "ready," rather than a fixed sleep or a
  coordinate that may now point at the wrong thing after a re-render.

**The case against / what should worry the authors:**
- Playwright-MCP's own bug tracker shows layer-2/a11y observation is not free of the exact failure
  mode §2.1 warns about for every rung above 0: "[Bug]: Accessibility tree snapshot includes
  off-screen/non-viewport elements causing AI agents to generate invalid test cases on unreachable
  UI elements" ([microsoft/playwright#39955](https://github.com/microsoft/playwright/issues/39955)).
  This is a live, acknowledged defect class: the a11y tree can describe elements that are not
  actually actionable (off-screen, in a closed accordion, behind a modal), which is precisely the
  "which selector, and is it still valid" grounding problem §2.1 says layer 2 has — the doc is right
  that this problem doesn't disappear, and this GitHub issue is a concrete, dated instance of it
  actually happening to agents built on exactly the substrate §2.4 chooses.
- AndroidWorld and browser-use both demonstrate that real production systems hedge by keeping a
  coordinate/pixel fallback *alongside* the element-targeted primary action space (browser-use's
  `set_coordinate_clicking` toggle; AndroidWorld's dual tap/element actions). That the field's own
  tools keep the fallback is mild evidence that pure layer-2 is not obviously sufficient even for
  DOM-accessible apps — canvas-rendered widgets, custom drag-handles, and non-standard controls
  inside otherwise-normal web apps regularly have degenerate or misleading a11y representations,
  which is exactly the "custom widgets" caveat §1.1 already flags for the observation axis but which
  §2.4 doesn't re-flag for the *action* axis.
- The CodeAct evidence (§4 above) is a reminder that a fourth option — code-as-action *over* layer-2
  primitives (a Playwright script rather than one Playwright call per turn) — has the closest
  measured analogue to an efficiency win in the whole literature (up to 30% fewer turns, in a
  non-GUI domain) and was set aside by §2.4 without being tested against. That's a defensible choice
  for a first experiment (verification is harder for multi-step code, as discussed in §4), but it
  should be named as a road not taken, not omitted.

**What would NOT transfer from this project's results to a pixel-level agent, named specifically:**
1. **The entropy/perplexity control signal itself (P3).** A clean categorical distribution over an
   enumerated candidate set (layer 2) has no analogue at layer 0 without discretizing continuous
   coordinates into a grid — the foundations doc already says this (§2.5), and nothing found this
   session weakens it. Any AUROC number for "surprisal predicts step failure" measured at layer 2 is
   *not* a claim about pixel agents; a grid-size choice would need to be re-litigated from scratch.
2. **Edge durability numbers (P1).** §2.5 already states coordinate edges die on layout shift while
   selector edges die on CSS refactor — these are different failure distributions with different
   time constants. A crossover point (§P4's "amortization curve") measured against layer-2 edge
   decay will not predict the crossover point for layer-0 edges, which likely decay faster (any
   visual re-layout invalidates a coordinate; many CSS refactors do not change a stable
   `role+text` locator).
3. **Cost-per-step ratios.** The ~50× figure in §2.5/P4 could not be sourced this session (flagged
   below); whatever the real ratio is between a screenshot-plus-vision-model step and an a11y-tree
   text step, it is a property of *current model pricing and image-tokenization*, not a property of
   the task — it will not transfer across model generations, let alone across the pixel/element
   boundary, and should be re-measured for whatever specific models the actual experiment uses
   rather than assumed from this document.
4. **ScreenSpot-style grounding-failure modes.** The specific things that break at layer 0 (icons
   without text labels, high-density professional UIs per ScreenSpot-Pro) are a *different* error
   surface than anything a layer-2, a11y-tree-driven agent will ever encounter, because a11y-tree
   candidate enumeration sidesteps pixel localization entirely. A layer-2 result saying "the graph
   reduces uncertainty" says nothing about whether a graph would help or hurt *grounding* uncertainty
   at layer 0 — that is a separate hypothesis this project's design cannot test.

**Net verdict:** §2.4's choice is defensible and, on the evidence gathered, probably the right
first move — but the document should state more plainly that this is a choice made *because* the
project's specific measurement (categorical entropy) requires it, not because layer 2 is
unambiguously "the" right substrate for computer-use in general. The scope-limiting sentence already
in §2.4 ("results will be a claim about DOM-accessible web apps, not about computer use in general")
is correct and should be read as load-bearing, not boilerplate.

---

## Corrections to docs/01-foundations.md

- **§1.2:** *"raw trees are frequently 100k+ tokens, so pruning is mandatory."* This specific figure
  could not be traced to a source. WebArena's own paper (the most likely origin for such a claim)
  states only qualitatively that the accessibility tree is "more compact than the DOM representation"
  with no token counts given ([arXiv 2307.13854v4](https://arxiv.org/html/2307.13854v4), read
  directly). Keep the qualitative point (raw DOM/HTML is large and needs pruning); mark the specific
  number `[unverified]` until a source is found, or replace it with a measured number from this
  project's own pilot runs.

- **§2 (the ladder table) and its framing generally imply one rung per system.** Correction: at
  least three widely-used systems (BrowserGym, browser-use, AndroidWorld) expose **multiple rungs as
  a runtime switch within one codebase**, and OpenAI documents a fourth mode (model-authored
  Playwright/PyAutoGUI code) layered over rung 0/1. See the cross-cutting note after the §1 table.
  This doesn't invalidate the ladder — it strengthens §2.2's point 1 ("the agent's action space ≠
  the executor's action space... the harness decides") but the doc should say explicitly that most
  real systems occupy a *span* of rungs, selected per call, not a point.

- **§2 table, layer 4 (accessibility actions) implicitly ranked "above" layer 2/3 on the reliability
  axis of the monotone tradeoff.** Correction: accessibility-tree-based targeting is not uniformly
  more reliable than DOM/CSS/text-based targeting. A live, dated example: Playwright's own bug
  tracker records "[Bug]: Accessibility tree snapshot includes off-screen/non-viewport elements
  causing AI agents to generate invalid test cases on unreachable UI elements"
  ([microsoft/playwright#39955](https://github.com/microsoft/playwright/issues/39955)). Whether a11y
  metadata is trustworthy depends entirely on whether the app author implemented it correctly
  (ARIA roles, labels) — many production apps (especially canvas-rendered or heavily custom-widget
  UIs) have sparse or misleading a11y trees. The ladder's "monotone" framing (§2.1) should note this
  is monotone *in expectation, for well-behaved standards-compliant apps*, not as a hard guarantee —
  layer 4 can be *less* reliable than layer 2 on a poorly-instrumented app.

- **§1.2's claim that code-as-action is "an efficiency win (loops, batching)" for GUI agents
  specifically.** Correction/caveat: the strongest quantitative evidence for this (CodeAct, up to
  20% success-rate gain and 30% fewer turns, [arXiv 2402.01030](https://arxiv.org/abs/2402.01030))
  comes from general API/tool-use agents (API-Bank, M³ToolEval), not GUI/browser tasks. No
  GUI-specific ablation reproducing this result was found. The claim should be flagged as an
  extrapolation, which §5 of this project's own experimental design should be aware of before citing
  CodeAct as if it were GUI-domain evidence.

- **§2.5/P4's "cost-per-step varies by roughly 50× across the ladder"** — this specific multiplier
  could not be sourced this session (marked `[verify the arithmetic]` in the original doc, correctly
  anticipating this). No paper found gives a directly comparable cost-per-step number across rungs.
  Recommend either sourcing it before it's used in the paper, or explicitly labeling it an
  order-of-magnitude illustrative estimate, not a cited figure.

- **§2.2 point 3 (CSRF)** is directionally correct but worth one precision pass: CSRF-token cost is
  correctly attributed to layer 6, and the doc should avoid ever implying (it does not currently,
  but a careless reading might) that layer-3 DOM/JS manipulation bypasses CSRF — it doesn't; what
  layer 3 actually breaks is React-style controlled-input value tracking and any `isTrusted`-gated
  listener, confirmed via [MDN's `Event.isTrusted`](https://developer.mozilla.org/en-US/docs/Web/API/Event/isTrusted).
  This is a clarification, not a contradiction, of what's already written.

- **§2.3's options/semi-MDP framing is correctly cited but should not be presented as standard
  practice in the GUI/web-agent subfield.** See §5 above: searched broadly, found no GUI/web paper
  using the Sutton-Precup-Singh vocabulary explicitly, despite several papers (workflow-guided
  exploration, Agent Workflow Memory, NNetNav) doing conceptually similar things under different
  names. Recommend the paper state this framing as a deliberate, useful theoretical import, not as
  "the" standard framework already used in this literature.

---

## Design implications

1. **Adopt BrowserGym/AgentLab, and specifically its `bid` action subset, rather than writing a
   custom Playwright wrapper.** It already implements exactly the layer-2, id-referenced action set
   §2.4 specifies, is the harness §3.2 already recommends, and its `ACTION_SUBSETS` mechanism gives
   a *free* ablation path: swapping to the `coord` subset on the same codebase is the cheapest
   possible way to run a controlled layer-1-vs-layer-2 comparison later, using the project's own
   infrastructure rather than reconstructing one from a different paper's numbers.

2. **Budget a pilot measurement for the two numbers this session could not source:** (a) actual
   token counts for pruned a11y-tree observations on the specific WebArena site(s) chosen for Phase
   1/2, and (b) actual cost/latency per step for the specific actor + scorer models chosen. Both
   numbers are load-bearing for P4's amortization argument and neither has a citable source at the
   specificity this project needs — they should be measured, not assumed from the ~50× figure in the
   current draft.

3. **Treat the a11y-tree observation as noisy, not ground truth, and build the irreversibility/
   candidate-enumeration pipeline defensively.** Given the confirmed Playwright issue about
   off-screen elements appearing in snapshots, the pruned-tree → candidate-set step that feeds P3's
   categorical entropy calculation should filter for genuine actionability (visible + receives-events,
   per Playwright's own actionability model) before computing entropy over candidates, or the entropy
   signal will be partly measuring "how many phantom off-screen elements did the tree include" rather
   than genuine task uncertainty.

4. **When writing up P3/P4 results, explicitly scope every efficiency and reliability claim to
   layer 2 / DOM-accessible web apps**, per the transfer analysis in §7 above (numbered items 1-4).
   A reviewer familiar with ScreenSpot or OSWorld will immediately ask whether the graph-uncertainty
   result would hold for a pixel agent; the honest, sourced answer is "untested, and the categorical-
   entropy method as designed cannot be directly ported without redesigning the uncertainty signal
   for continuous coordinates."

5. **Do not cite CodeAct as GUI-domain evidence for the code-as-action family (§1.2) without either
   (a) finding a GUI-specific replication, or (b) explicitly labeling it cross-domain evidence.** If
   the eventual paper wants a genuine code-as-action condition, browser-use's `evaluate(code)` action
   and OpenAI's "model writes Playwright code" pattern are the two concrete existing implementations
   to build on or benchmark against, rather than re-deriving one from scratch.

6. **Correct the options/semi-MDP framing's rhetorical positioning before submission**, per the
   correction above — cite it as a novel, well-motivated formal import rather than implying the
   field already frames macro-actions this way; the actual related work (workflow-guided
   exploration, Agent Workflow Memory, NNetNav) should be cited as the closest prior art *without*
   the options vocabulary, since that's how those papers actually describe themselves.

---

## Open questions

1. **Is there in fact any published agent harness that reads the page's own XHR/fetch responses as
   its observation channel (§2.2 point 2 / §2.4's "reads may use layer 6")?** Not found this session,
   but the search was constrained by an exhausted WebSearch budget partway through — a dedicated,
   non-arXiv-restricted follow-up search (developer blogs, harness READMEs, Playwright/Puppeteer
   community projects, not just academic papers) might surface prior art academic search missed.
2. **What is the real, current cost-per-step ratio between a screenshot-driven step and a pruned-
   a11y-tree-driven step, for the specific models this project will actually use?** No general
   citable figure exists; this needs to be measured directly rather than argued from a documented
   number, since token/latency economics shift with every model release.
3. **Do bot-detection systems in practice check `isTrusted` or other synthetic-event signals, and
   does that matter for a research harness running against a self-hosted WebArena-style
   environment (where there is no adversarial bot detection to defeat)?** Genuinely unresolved by
   this pass, and possibly moot for the self-hosted, causal-claim environment §3.2 restricts the
   project to — but relevant the moment §3.3's live-web generalization appendix is attempted.
4. **Is a controlled, same-codebase layer-2-vs-layer-1 (BrowserGym `bid` vs `coord`) ablation of
   P3's entropy signal itself worth running as an explicit Phase 0 sub-experiment**, given that the
   infrastructure to do so already exists in the adopted harness? This wasn't asked for in the
   original research questions but falls directly out of finding that BrowserGym exposes both
   subsets natively.
5. **Would a fine-grained accessibility-actionability filter (dropping off-screen/hidden nodes
   before entropy computation) change the calibration story in P3's "Experiment zero" (does
   surprisal predict step failure, AUROC)?** This project's own irreversibility-classifier and
   candidate-enumeration pipeline hasn't been built yet, so this is untestable until then, but it is
   a concrete, falsifiable question the pipeline design should be built to answer, not just guard
   against.
