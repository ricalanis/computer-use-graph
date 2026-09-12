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

## Demo sequence (current state, ~10 minutes)

A live walkthrough of what exists right now, in order. Every step is runnable from a terminal or
shown from committed files — steps 5–6 can fall back to the committed results if the network is
unreliable.

1. **The bet (30s).** This README, top. The one-line question, and: "we built the smallest possible
   version of this experiment and ran it."
2. **The evidence base (1 min).** `knowledge/08-key-findings.md` — point at F1 (the closest paper
   already ran graph-vs-flat, so our novelty is autonomous exploration + cost accounting) and F2
   (flat memory takes ~2/3 of the win, so the real fight is graph vs flat).
3. **The site and the arms (2 min).** `micro/micro_exp.py` — scroll `PAGES` (25 pages, decoy
   labels), then `explore()` (the task-agnostic random walk that never sees task text — the
   anti-contamination firewall), then `graph_block` vs `flat_block`: same exploration data, two
   representations, char-matched budgets. Identical information; the only difference is structure.
4. **The actual memories (1 min).** Side by side:
   ```bash
   cat micro/memory_graph_s7.txt   # typed pages, affordance->destination edges
   cat micro/memory_flat_s7.txt    # recency-ordered transcript, same chars
   ```
   The whole hypothesis visible in two text files.
5. **Run one arm live (3 min).**
   ```bash
   python3 micro/micro_exp.py --arm graph --seed 7 --out /tmp/demo_graph.json
   ```
   ~24 episodes against Ollama in real time; every step is one LLM call, logged with confidence.
6. **The analysis (1 min).**
   ```bash
   python3 micro/analyze.py
   ```
   Walk the output top to bottom: the arm table (59.7% → 70.8% → 73.6%), the paired stats
   ("graph vs flat: +2.8pp, p=0.73 — not significant, and that's the expected result at n=72; the
   power tables in this repo predicted it"), then the AUROC block ("verbalized confidence is 0.49,
   i.e. useless — which is itself a finding; it matches the literature").
7. **The honest close (1 min).** `micro/README.md` → "Known limitations" (smoke test, one model,
   no distractor control), then the status line above: machinery validated, direction correct,
   noise exactly as predicted. Next spend: the entropy scorer and the real-benchmark pilot, both
   planned in `docs/02-design-v0.2.md`.

Arc: *a verified literature base, a working miniature of the exact experiment, results that
reproduce the literature's warnings, and a pre-registered plan for the real thing.*

## Scope rule

Clean-room and public. No employer-internal technology, data, benchmarks, or unreleased work informs
anything here. Every substantive claim carries a public citation. **✓** marks claims the root session
re-verified; everything else must be re-checked before external citation. Measured claims from our
own runs link to the raw result files that produced them.