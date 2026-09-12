# computer-use-graph

Public, clean-room research project on web agents.

**Question:** does an autonomously explored, type-abstracted site graph beat token-matched flat
trajectory memory at equal amortized cost, on configuration-heavy sites? And can an uncertainty
signal calibrated against episode outcome decide when to trust it?

**Status (2026-09-12):** the literature review and verification pass are complete, and design v0.2
is written. No experiments have run yet.

## Start here

1. `knowledge/08-key-findings.md` — what we learned that changed the plan
2. `knowledge/02-action-space-ladder.md` — the computer-use substrate question
3. `docs/02-design-v0.2.md` — the current design and experiment sequence
4. `knowledge/09-decisions-log.md` — what's decided, proposed, and open

## Layout

```
README.md, CLAUDE.md (AGENTS.md → CLAUDE.md)   orientation for people and agents
docs/
  01-foundations.md        v0.1, frozen — taxonomy and action-space ladder as first written
  02-design-v0.2.md        current design
knowledge/                 maintained, topic-organized notes (index: 00-index.md)
  01 taxonomy · 02 action space · 03 benchmarks · 04 state & graphs · 05 memory & replay
  06 uncertainty · 07 methodology · 08 key findings · 09 decisions · 10 open questions · 11 glossary
research/                  frozen evidence
  README.md                how it was produced; incidents affecting trust
  00-verification-log.md   root spot-checks and corrections
  00-worker-briefs.md      exact research prompts
  R0–R5                    one dossier per thread
bibliography/
  references.md            every cited source with verification status (generated)
  build_references.py      regenerates references.md from the dossiers
```

## Scope rule

Clean-room and public. No employer-internal technology, data, benchmarks, or unreleased work informs
anything here. Every substantive claim carries a public citation. **✓** marks claims the root session
re-verified; everything else must be re-checked before external citation.
