# computer-use-graph — agent orientation

Public research project. **Question:** does an autonomously explored, type-abstracted site graph beat
token-matched flat trajectory memory at equal amortized cost, and can a calibrated uncertainty signal
decide when to trust it?

## Scope rule (non-negotiable)

Clean-room and public, per `../CLAUDE.md`. No employer-internal technology, data, benchmarks, or
unreleased work informs anything here, even when it would help. Derive ideas from public literature
or first principles, and don't mention that an internal alternative exists. No internal identifiers
in code, comments, commits, or docs.

## Current state (update when it changes)

- **Phase:** design v0.2 complete; no code yet.
- **Next:** Phase 0a kill tests (noisy-TV saturation; step vs episode AUROC), then Phase 0b pilot
  (~50 WebArena GitLab tasks, arm 1 vs arm 2).
- **Open operator decisions:** see `knowledge/09-decisions-log.md` (O1–O4). Primary benchmark is
  still open.

## Where things live

| Need | Go to |
|---|---|
| Orientation / what we know | `knowledge/00-index.md` → `knowledge/08-key-findings.md` |
| The current plan | `docs/02-design-v0.2.md` |
| Why a decision was made | `knowledge/09-decisions-log.md` |
| What's unresolved | `knowledge/10-open-questions.md` |
| Whether a citation is trustworthy | `bibliography/references.md` (status column), `research/00-verification-log.md` |
| Raw evidence | `research/R0`–`R5` |
| How the research was produced | `research/README.md`, `research/00-worker-briefs.md` |

## Conventions

- **Provenance marks.** **✓** = root-verified (re-fetched or recomputed). Unmarked = worker-retrieved
  only. `[unverified]` = not confirmed. Keep marks when moving facts between files.
- **Never fabricate citations.** Cite only retrieved sources. Before citing anything externally that
  isn't ✓, re-fetch it and log the check in `research/00-verification-log.md`.
- **Don't trust summarizer numbers.** A page summarizer has fabricated table values in this project.
  Read the table or quote the sentence.
- **Frozen files.** Don't edit `docs/01-foundations.md` or `research/R*.md`; dossiers quote v0.1 line by
  line. Record corrections in the verification log and knowledge notes.
- **Design changes** go into a new versioned doc (`docs/03-…`) plus a decisions-log entry. Don't
  silently rewrite v0.2 once work starts against it.
- **Knowledge notes are the maintained layer.** When a finding changes, update the relevant
  `knowledge/` note and, if it's load-bearing, `08-key-findings.md`.
- **Bibliography is generated.** Edit `bibliography/build_references.py` (titles, verified set,
  notes), then run `python3 bibliography/build_references.py`. Never hand-edit `references.md`.
- **Experiments** (when they exist): pre-register before running, pin container digests and run
  dates, and log cost per arm as a first-class column (`knowledge/07-experimental-methodology.md`).
