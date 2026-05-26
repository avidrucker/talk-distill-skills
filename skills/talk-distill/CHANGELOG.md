# Changelog — talk-distill

## [0.1.1] — 2026-05-26

Clarification, no behavior change. Removed misleading "Casey-Muratori-
style" / "Yegor-Bugayenko-style" qualifiers from the file format
descriptions — those people didn't define the formats; they're the
*content* of sister repos (`warmed-skills`, `yegor-pm-skills`) that
happened to first use the outline/file-naming conventions this family
adopted. Formats are now described structurally ("`executive_summary.md`
— TL;DR + Salient Points + Outline" / "`key_takeaways.md` — timestamped
emoji-bullet index"), with the sister repos credited as the source of
the conventions rather than as eponymous styles.

## [0.1.0] — 2026-05-26

Initial draft. Meta-orchestrator for the talk-distill skill family.
Routes to `talk-fetch` / `talk-transcribe` / `talk-summarize` /
`talk-takeaways` sub-skills based on what artifacts the user needs.

Design rationale and cross-video validation results live in the repo's
`workflow_notes.md`. Skill family will iterate as the pipeline is run on
more talks (variations in caption authoring, language, single-speaker
format, etc. — see workflow_notes.md "Variations we still haven't
stress-tested").
