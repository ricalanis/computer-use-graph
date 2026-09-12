# computer-use-graph

Public, clean-room research project on web agents.

**Question:** does an autonomously explored, type-abstracted site graph beat token-matched flat
trajectory memory at equal amortized cost, on configuration-heavy sites? And can an uncertainty
signal calibrated against episode outcome decide when to trust it?

**Status (2026-09-12):** literature review and verification pass complete; design v0.2 written;
micro-validation run done (see below). No experiments on a real benchmark have run yet.

## What we've measured so far

A [micro-validation run](micro/README.md) on a synthetic config-admin site (25 pages, decoy
labels, 3-level nav) tested the harness mechanics before any real benchmark work: three memory
arms — none, flat transcript, site graph — built from the **same task-agnostic exploration**,
char-matched budgets, 24 tasks × 3 exploration seeds (216 paired episodes).

| arm | success | 95% CI |
|---|---|---|
| none | 59.7% | [48.2%, 70.3%] |
| flat | 70.8% | [59.5%, 80.1%] |
| graph | 73.6% | [62.4%, 82.4%] |

What it showed (details and caveats in `micro/README.md`):

- **The mechanism works end-to-end:** task-agnostic crawl → same-data graph/flat memories →
  controlled contrast → programmatic validators → paired McNemar + AUROC analysis.
- **Flat memory takes most of the win** (+11.1pp of the +14.0pp total) — reproducing in miniature
  the finding that drove the design: the primary contrast is graph vs flat, and it will be small.
- **The primary contrast is not yet distinguishable from noise** (+2.8pp, p=0.73 at n=72) — the
  power math from the methodology notes is confirmed empirically; the real experiment needs the
  full 362-task benchmark.
- **Verbalized confidence is uninformative** (AUROC 0.46–0.51 at every progress quartile) —
  consistent with the *Last Step Matters* finding; the action-entropy scorer is the next signal
  to instrument.

This is a smoke test of the machinery, not evidence for the hypothesis. The pre-registered
experiment sequence is in `docs/02-design-v0.2.md` §8.

## Start here

1. `knowledge/08-key-findings.md` — what we learned that changed the plan
2. `knowledge/02-action-space-ladder.md` — the computer-use substrate question
3. `docs/02-design-v0.2.md` — the current design and experiment sequence
4. `knowledge/09-decisions-log.md` — what's decided, proposed, and open
5. `micro/README.md` — the micro-validation run and its results

## Layout

```
README.md, CLAUDE.md (AGENTS.md → CLAUDE.md)   orientation for people and agents
docs/
  01-foundations.md        v0.1, frozen — taxonomy and action-space ladder as first written
  02-design-v0.2.md        current design
knowledge/                 maintained, topic-organized notes (index: 00-index.md)
  01 taxonomy · 02 action space · 03 benchmarks · 04 state & graphs · 05 memory & replay
  06 uncertainty · 07 methodology · 08 key findings · 09 decisions · 10 open questions · 11 glossary
micro/                     minimal validation experiment (synthetic site, results, analysis)
research/                  frozen evidence
  README.md                how it was produced; incidents affecting trust
  00-verification-log.md   root spot-checks and corrections
  00-worker-briefs.md      exact research prompts
  R0–R5                    one dossier per thread
bibliography/
  references.md            every cited source with verification status (generated)
  build_references.py      regenerates references.md from the dossiers
```

## Reproduce the micro run

Requires `oll` (Ollama Cloud CLI) on PATH. One arm, one exploration seed:

```bash
python3 micro/micro_exp.py --arm graph --seed 7 --out micro/results_graph_s7.json
```

Arms are `none`, `flat`, `graph`; seeds used in the run were 7, 11, 23. Aggregate and analyze:

```bash
python3 micro/analyze.py
```

Stdlib only, no other dependencies. Each full arm-seed run is ~24 episodes × ~7 LLM calls.

## Demo script (current state, ~10 minutes)

What follows is the script itself — narration to deliver, with links to each artifact and
commands as stage cues. Steps 5–6 can fall back to the committed results if the network is
unreliable; everything shown is in git.

---

**[1 — The bet · 30s · this README, top]**

> "This repo asks one question: does an agent that explores a website on its own and builds a
> graph of it beat an agent that just rereads its transcripts — when both get the same memory
> budget and the exploration cost is counted. We haven't run the real experiment yet. What we
> have is the verified evidence base, and a working miniature of the exact experiment, with
> results. This is that miniature."

**[2 — Why the fight is graph vs flat · 1 min · [key findings](knowledge/08-key-findings.md)]**

> "Twenty findings changed our plan. Two matter for this demo.
> [F1](knowledge/08-key-findings.md): the closest paper already ran graph-versus-nothing on
> WebArena — so that's not a contribution anymore. Our novelty is autonomous exploration and
> honest cost accounting.
> [F2](knowledge/08-key-findings.md): wherever a flat baseline existed, flat memory took about
> two-thirds of the win. So the real fight is graph versus flat — and it will be small. The
> miniature was built to test the machinery for exactly that fight."

**[3 — The experiment, in code · 2 min · [micro_exp.py](micro/micro_exp.py)]**

> "A synthetic admin panel: 25 pages, three levels of navigation, and decoy labels —
> 'Email digest' next to 'Email notifications', 'Install analytics' next to 'Install beta
> analytics'. The agent gets no hints about which is real.
> This function — `explore` — is a random walk. It never sees task text. That's the
> anti-contamination firewall: every evaluation task is held out by construction.
> Then the same exploration log becomes two memories: `graph_block` — typed pages with
> affordance-to-destination edges — and `flat_block` — a recency-ordered transcript. Same data,
> same character budget. Identical information. The only difference is structure."

**[4 — The two memories, side by side · 1 min · stage cue]**

```bash
cat micro/memory_graph_s7.txt
cat micro/memory_flat_s7.txt
```

> "On the left, the graph: every page type, every button, where it leads. On the right, the
> transcript: the same knowledge, buried in narrative order. Same characters. This is the whole
> hypothesis, visible in two text files."

**[5 — One arm, live · 3 min · stage cue]**

```bash
python3 micro/micro_exp.py --arm graph --seed 7 --out /tmp/demo_graph.json
```

> "This is the agent operating the panel right now — every step is one model call, and every
> step logs the action, the destination, and the agent's own confidence. Twenty-four tasks,
> three memory arms, three exploration seeds — two hundred sixteen paired episodes in the full
> run; this is one arm of it."

**[6 — The results · 1 min · stage cue]**

```bash
python3 micro/analyze.py
```

> "No memory: 59.7%. Flat transcript: 70.8%. Graph: 73.6%. The ordering is the hypothesis's
> direction — but look at the paired statistics: graph versus flat is +2.8 points, p = 0.73.
> Not significant. And that is the expected result: our own power tables said 72 pairs can't
> resolve a small effect — the real run needs the full 362-task benchmark.
> One more thing: verbalized confidence — the agent saying 'I'm 90% sure' — has an AUROC of
> 0.49 against failure. Coin flip. Useless. That's not a bug; it's a published finding we
> reproduced, and it's why the next thing we build is an entropy scorer instead."

**[7 — The honest close · 1 min · [micro/README.md](micro/README.md)]**

> "The limitations are in the repo, not hidden: smoke test, one model, no distractor control
> yet. What's validated is the machinery — task-agnostic exploration, matched budgets, paired
> statistics, honest power math — and the direction. The plan for the real experiment is
> pre-registered in [the design doc](docs/02-design-v0.2.md): the entropy scorer, the pilot on
> real WebArena, then the eight-arm comparison. The miniature says the machinery is ready.
> The next dollar spent goes to the real thing."

---

*Arc: a verified literature base → a working miniature of the exact experiment → results that
reproduce the literature's warnings → a pre-registered plan for the real thing.*

## Scope rule

Clean-room and public. No employer-internal technology, data, benchmarks, or unreleased work informs
anything here. Every substantive claim carries a public citation. **✓** marks claims the root session
re-verified; everything else must be re-checked before external citation. Measured claims from our
own runs link to the raw result files that produced them.