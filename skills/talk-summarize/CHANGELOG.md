# Changelog — talk-summarize

## [0.1.1] — 2026-05-26

Clarification, no behavior change. Removed misleading "Casey-Muratori-
style" qualifier from the format description — Casey didn't define the
TL;DR + Salient Points + Outline structure; it was just the structure
used in `warmed-skills/bad_code_talk/talk_summary.md`, which happened to
be summarizing a Casey talk. Format is now described structurally
(`executive_summary.md` — TL;DR + Salient Points + Outline), with
`warmed-skills` credited as the source of the file shape rather than as
an eponymous style.

## [0.1.0] — 2026-05-26

Initial draft. No script — pure prompt for Claude. Locks in the
TL;DR + Salient Points + Outline structure inherited from the
`talk_summary.md` shape in `warmed-skills`. Style rules emphasize
concrete-over-generic, prose-over-bullets in TL;DR, no LLM-isms, and
accurate representation over editorial commentary.

The two reference examples linked from SKILL.md (the two Fulcro
statecharts talks at avidrucker/fulcro-statecharts-talks) ARE the style
guide — they were written by hand before the skill existed.
