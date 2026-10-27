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
