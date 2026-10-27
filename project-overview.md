# Project overview — ingmarbib

## Goal
Maintain a single authoritative BibTeX bibliography of Ingmar Visser's publications (`ingmar.bib`); keep entries up to date as papers are submitted, revised, or published.

## Scope / key questions
- All publications correctly entered, with consistent citation keys, author format, and status notes.
- New entries processed from the `new/` staging folder into `ingmar.bib` and archived.
- CV PDF (`cv_pubs.pdf`) builds cleanly from the bib.
- Notes and categories fields comprehensive and consistent across entries.

## Deliverables
<!-- The concrete outputs; a chief of staff reports progress per item. -->
- [ ] `ingmar.bib` — in progress (actively maintained; 124 entries as of April 2025)
- [ ] `cv_pubs.pdf` — in progress (built from bib via LaTeX/Makefile)
- [x] Update skill — done (`/update-bib` skill at `.claude/skills/update-bib/skill.md`)
- [ ] Categories and notes review — not started (audit existing entries for completeness)

## Key people
- Ingmar Visser — sole maintainer

## Files / index
- `session.md` — working memory (current focus + rolling Activity log)
- Things: TODO
- `ingmar.bib` — the authoritative bibliography
- `cv_pubs.tex` / `cv_pubs.pdf` — CV built from the bib
- `Makefile` — build rules for the CV PDF
- `new/` — staging folder for new entries (processed, then moved to `archive/`)
- `archive/` — historical source files and merge script (`merge_bib.py`)
- `CLAUDE.md` — citation key conventions, author format, status vocabulary, merge logic

## Status
Scaffolded 2026-10-27.

## Notes
- Confidentiality: no personal/participant/editorial data in AI tools —
  anonymize first. Own work (manuscripts, grants) is fine.
