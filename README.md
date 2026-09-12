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

## Scope rule

Clean-room and public. No employer-internal technology, data, benchmarks, or unreleased work informs
anything here. Every substantive claim carries a public citation. **✓** marks claims the root session
re-verified; everything else must be re-checked before external citation. Measured claims from our
own runs link to the raw result files that produced them.