---
name: talk-distill
description: Meta-orchestrator for distilling a YouTube talk into study material. Use when the user gives a YouTube URL and wants any of — SRT captions, a clean speaker-labelled transcript, an executive summary, or a timestamp-indexed key-takeaways doc. Routes to talk-fetch / talk-transcribe / talk-summarize / talk-takeaways sub-skills based on what's needed.
version: 0.1.0
last_reviewed: 2026-05-26
---

# Talk Distill — Meta Skill

Coordinated set of skills for turning a YouTube talk into study artifacts:
raw SRT → light-edit speaker-labelled transcript → Casey-Muratori-style
executive summary + Yegor-Bugayenko-style timestamped key-takeaways index.

## The 4 sub-skills

| Skill | One-liner |
|---|---|
| `talk-fetch` | Probe + download the best subtitle track for a YouTube URL. Auto-skips human-authored vs. auto-captioned vs. translated decisions. Outputs `captions.SRT`. |
| `talk-transcribe` | Dedupe YouTube's rolling auto-captions, toggle speakers on `>>`, emit a paragraph-flowed `transcript.txt`. Wraps the project's `scripts/srt_to_transcript.py`. |
| `talk-summarize` | Read the transcript, produce Casey-style `executive_summary.md` (TL;DR + Salient Points + Outline). First-read entry point. |
| `talk-takeaways` | Read the transcript + SRT, produce Yegor-style `key_takeaways.md` (timestamped emoji bullets). Re-navigation entry point. |

## Typical sequence

For a brand-new talk:

1. `talk-fetch` — pull the SRT into `<topic>_talk/captions.SRT`.
2. `talk-transcribe` — produce `<topic>_talk/transcript.txt`.
3. `talk-summarize` — produce `<topic>_talk/executive_summary.md`.
4. `talk-takeaways` — produce `<topic>_talk/key_takeaways.md`.

Each step is independently invokable. If a user already has the SRT and
just wants takeaways, skip straight to `talk-takeaways`.

## When to invoke which sub-skill

| Situation | Load |
|---|---|
| User pastes a YouTube URL and says "distill this" / "summarize this" / "get the transcript" | `talk-distill` (this meta), then route by what's missing |
| User has an SRT already and wants a transcript | `talk-transcribe` |
| User has a transcript and wants the summary | `talk-summarize` |
| User wants a jumpable index, not a read-through summary | `talk-takeaways` |
| Just the captions, nothing more | `talk-fetch` |

## How Claude should use this meta-skill

When a YouTube URL appears in a request along with phrasing like "summarize,"
"distill," "get the transcript," "make study notes," etc., mentally invoke
this meta-skill, check what's already on disk in the target directory, and
run only the missing steps. Surface the chosen plan before acting:

- "I see no captions yet — fetching first, then transcribing."
- "Transcript exists; I'll just produce the summary."
- "Both summary and takeaways requested — I'll write them in parallel after the transcript."

If the talk's subdir doesn't exist yet, propose a name based on the video
title and uploader, scoped descriptively (e.g. `fulcro_statecharts_talk/`,
not `video_1/`).

## Conventions

- One subdir per talk under the project root; filenames in that subdir are
  fixed: `captions.SRT`, `transcript.txt`, `executive_summary.md`, `key_takeaways.md`.
- Casey-style + Yegor-style summaries coexist — they serve different
  purposes (first-read vs. re-navigation). Default is to produce both
  unless the user asks for only one.
- Speaker labels in the transcript are ~90–95% accurate. The pipeline is
  deliberately a rough first cut; manual spot-correction is expected for
  high-stakes citation use.

## Source repo

This skill is git-source-controlled in
[`avidrucker/talk-distill-skills`](https://github.com/avidrucker/talk-distill-skills).
SKILL.md files in `~/.claude/skills/talk-*` are symlinks to that repo —
edit in the repo, changes are live next session. Each skill has
independent semver (`VERSION` file + `CHANGELOG.md`).

## Deep reference

The design rationale, heuristic details, and cross-video validation results
live in [`workflow_notes.md`](../../workflow_notes.md) at the repo root.
That doc is the "research/" equivalent for this skill family.

Sister projects that established the layout conventions this family follows:

- [`warmed-skills`](https://github.com/avidrucker/warmed-skills) — Casey
  Muratori talks → skills (philosophy distillation flavor).
- [`yegor-pm-skills`](https://github.com/avidrucker/yegor-pm-skills) —
  Yegor Bugayenko's writings → skills (XDSD methodology flavor).
