# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a BibTeX bibliography repository for Ingmar Visser's academic publications in developmental psychology and infant cognition. The main file is `ingmar.bib`, managed with BibDesk on macOS.

## Files

- **ingmar.bib** — The single authoritative bibliography (124 entries as of April 2025)
- **archive/** — Historical source files (old ingmar.bib, ingmarInProgress.bib, works.bib) and merge_bib.py used to produce the current ingmar.bib

## Adding new publications

Edit `ingmar.bib` directly in BibDesk or as text. Follow the conventions below for citation keys, author format, and status notes.

## Citation Key Convention

Format: `firstauthorlastname + year + firstsubstantiveword` — all lowercase.

- **First author last name**: includes particles (`van`, `de`, `von`, etc.) concatenated — e.g. `van Renswoude` → `vanrenswoude`
- **First substantive word**: skips stop words and single-character tokens; strip LaTeX accents for key only
- **Collision suffix**: `b`, `c`, etc. appended to the second and subsequent duplicates (first keeps no suffix)
- Keys are regenerated on every merge run from current field values

Stop words (excluded from substantive word): a, an, the, of, in, on, and, for, to, with, from, by, at, as, is, are, was, were, be, been, it, its, this, that, these, those, or, but, not, into, than, do, does.

## Author Format Convention

`Last, First and Last, First and …` (BibTeX standard)

- Particles (`van`, `de`, `von`, `der`, `den`, `ter`, `te`, `le`, `la`, `du`, `des`, `op`) are kept with the last name: `van Renswoude, Daan`
- LaTeX accent commands in names must be preserved in output (e.g. `{\v S}lipogor`, `Kov{\'a}cs`)
- Use `{Hay Mar Myat Kyaw}` (double braces) for names where BibTeX would mis-parse word order

## Status Note Controlled Vocabulary

The `note` field for in-progress entries uses only these values (enforced by `normalize_status()` in merge_bib.py):

| Note value | Triggers |
|---|---|
| `in preparation` | "in preparation", "in prep" |
| `under review` | "submitted", "under review" |
| `in revision` | "in revision" |
| `IPA` | "in principle accept", "ipa" |
| `stage 1 registered report` | "stage 1" |
| `stage 2 registered report` | "stage 2" |
| `preprint` | "preprint" |
| `preregistration` | "preregistration", "pre-registration" |

When a published version is found: clear the status note. If the preprint had a DOI, add `preprint: https://doi.org/XXXX` to the note of the published entry.

## Deduplication and Merge Logic

1. ingmar.bib + ingmarInProgress.bib: key-based merge (richer field wins by string length; earlier date-added, later date-modified)
2. Within works.bib: group by normalized title, keep highest publication score; collect preprint DOIs from lower-ranked versions
3. works.bib vs combined: DOI exact match → title exact match → Jaccard similarity ≥ 0.72. If works.bib entry has higher publication score, update the existing entry (journal, volume, pages, doi, publisher); clear status note.
4. Year is only updated from works.bib if the existing entry had a status note (was in-progress).

## Fields Excluded from Output

`abstract`, `keywords`, `language`, `day`, `month`, `issn`, `bdsk-url-*`

## Output Sort Order

Year descending, then citation key ascending.

## Research Areas

Publications focus on: infant cognition, developmental psychology, ManyBabies multi-lab studies (MB2–MB5), hidden Markov models applied to psychology, eye-movement analysis, and Bayesian hierarchical modeling.
