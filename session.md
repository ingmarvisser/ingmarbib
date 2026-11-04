# Session memory — ingmarbib

This file is the project's working memory. The SessionStart hook loads it as
context at the start of each session and surfaces the latest `Next:` line; the
Stop hook appends a dated Done/Next bullet to the Activity log below.

## Current focus
Develop an update skill that processes new entries from `new/` into `ingmar.bib`
and moves processed files to `archive/`. Also: review categories and notes fields
for comprehensiveness.

Next: review categories and notes fields for completeness across existing entries.

## Activity log
- 2026-10-27 — Done: Scaffolded the project (added `session.md` + `project-overview.md`); hooks now active. Next: develop the `new/` → `ingmar.bib` update skill.
- 2026-10-27 — Done: Applied new-project skill to ingmarbib; confirmed deliverables (update skill, notes/categories review). Next: develop the update skill for the `new/` folder and apply it to its current contents.
- 2026-10-27 — Done: Wrote `/update-bib` skill (`.claude/skills/update-bib/skill.md`); parsed all 13 emails in `new/`; proposed 6 updates/new entries + 1 skip + 1 ask (missing title). Next: get Ingmar's approval on the 8 proposals, then apply approved changes to `ingmar.bib` and archive processed emails.
- 2026-10-27 — Done: Parsed 8 new files in `new/`; updated proposals — IJdo author list confirmed (docx), Pfadt title changed + preprint DOI found, Thiele et al. title now known. Full updated 8-item proposal presented; 2 questions open (IJdo journal history, Thiele author order). Next: get approval and apply all changes to `ingmar.bib`.
- 2026-10-27 — Done: Applied all 7 changes to `ingmar.bib` (2 updates + 5 new entries; 126 total); archived all 22 files from `new/` to `archive/processed/`; `/update-bib` skill marked done. Next: review categories and notes fields for completeness.
- 2026-10-27 — Done: Confirmed all changes; `new/` empty; offered git commit. Next: commit ingmar.bib changes, then review categories/notes fields.
- 2026-10-27 — Done: Committed ingmar.bib (121→126 entries), project-overview.md, session.md (9c3c9f7). Next: review categories and notes fields across existing entries for completeness.
- 2026-10-27 — Done: Started chief skill; found `Things: TODO` in project-overview.md — no Things project linked yet. Asked Ingmar whether bibliography maintenance is tracked in Things. Next: link a Things project (or skip) and proceed to categories/notes review.
- 2026-10-27 — Done: Audited all 126 entries; found 20+ issues: 5 missing status notes, 1 note typo, 1 probable duplicate (sarafoglou 2024/2025), 4 entry-type mismatches, 8 missing DOIs, 3 author-format errors; asked 3 clarifying questions. Next: get answers, apply fixes, then clarify what "categories" means.
- 2026-10-27 — Done: Applied 8 straightforward fixes (333460f): note typo, 3 author formats, 3 entry types, 1 premature journal field. Next: await answers on schaaf2023context/exner statuses, sarafoglou duplicate, and "categories" definition; then add missing DOIs.
- 2026-10-27 — Done: Added status-unknown notes to 4 entries; removed sarafoglou2024bayesian duplicate (125 entries, 337edd1). Explained that "categories" likely means thematic grouping (not yet in bib); awaiting direction. Next: confirm categories scheme; add 8 missing DOIs.
- 2026-11-04 — Done: Designed two-field scheme: `status` (pipeline stage) + `document` (current document type). Flagged IPA ambiguity; proposed checking cv_pubs.tex before implementing. Next: get approval on scheme + IPA placement, check LaTeX template, then migrate note field and update CLAUDE.md.
- 2026-11-04 — Done: Implemented status/document field scheme (e10d047): migrated 31 bib entries, updated cv_pubs.tex routing, updated CLAUDE.md. `document` is multi-valued (semicolons); CV display of document deferred. Next: add 8 missing DOIs on published articles.
- 2026-11-04 — Done: Added 8 missing DOIs (beeb549): kucharsky2021wald, hofman2015balance, hosenfeld2015major, vanschijndel2015preschoolers, andersen2014cognitive, raijmakers2014costs, vanbers2014preschoolers, visser2022mixture. Categories/notes review complete. Next: thematic CV sections (not started), vanbers2014distinctive cleanup (journal field holds "Manuscript submitted for publication" — decade-old entry).
- 2026-11-04 — Done: Rebuilt cv_pubs.pdf from latest ingmar.bib. Fixed three issues: updated biber (lipo bug), added ingmar-dm.dbx data model for status/document fields, patched apa.bbx to remove unsupported usenarrator option (biblatex-apa 9.20 vs biblatex 3.22a mismatch). WIP section now populated. Next: note that apa.bbx patch will be overwritten by next tlmgr update of biblatex-apa.
- 2026-11-04 — Done: Located MB3 entry (visser2026manybabies, @misc, status=under review, preprint DOI 10.31234/osf.io/ghrdt_v2). Asked for publication details (journal, volume, pages, DOI) to complete the update. Next: apply publication details once provided, change entry type to @article, remove status field, move preprint DOI to document field.
