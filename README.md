# talk-distill-skills

The pipeline and [Claude Code](https://claude.com/claude-code) skill
family for turning a YouTube talk into a clean speaker-labelled
transcript, an executive summary, and a timestamp-anchored key-takeaways
index — usable as personal study material.

This repo borrows its file/repo conventions from two sister repos:

- [`warmed-skills`](https://github.com/avidrucker/warmed-skills) — first
  repo I built with the `<talk>/captions.SRT` + `transcript.txt` +
  `talk_summary.md` layout. The `executive_summary.md` format (TL;DR +
  Salient Points + Outline) came from there.
- [`yegor-pm-skills`](https://github.com/avidrucker/yegor-pm-skills) —
  first repo I built with the parent meta-skill + sub-skills + per-skill
  `VERSION` / `CHANGELOG.md` layout. The `key_takeaways.md` format
  (timestamped emoji-bullet index) came from there.

Those repos distill someone else's published material. This one is
original tooling — the SRT-to-summary pipeline that turns the manual
ingestion process used in those repos into a reusable skill family.

## Why this exists

Each sister repo above hand-curated its SRT, transcript, and summary
files. That process was manual every time. This repo's goal is to
**automate the pipeline as a Claude Code skill family**, so the next
talk distillation is mostly a `/talk-distill <youtube-url>` away.

The talk artifacts produced by the pipeline so far live in
[`fulcro-statecharts-talks`](https://github.com/avidrucker/fulcro-statecharts-talks)
— two Tony Kay statechart talks distilled with this tooling. Treat that
repo as the test corpus / example outputs for what the skill family
should produce.

## Current state

- ✅ Working Python script: `scripts/srt_to_transcript.py`. Handles
  YouTube's rolling-caption format, speaker labeling via `>>` markers
  (with auto-revert and length-threshold heuristics), and configurable
  paragraph breaks. Stress-tested on two talks of very different length
  (76 min and 3h 28m) without per-video tuning.
- ✅ End-to-end workflow validated and documented in
  [`workflow_notes.md`](workflow_notes.md). Read that doc first if you want
  to understand the design choices, the heuristics, and the limitations.
- ✅ Skills drafted at v0.1.1 — see [`skills/`](skills/).

| Skill | Responsibility |
|---|---|
| `talk-distill` | Parent / meta-orchestrator. Routes to the four sub-skills based on which artifacts the user wants. |
| `talk-fetch` | `yt-dlp` wrapper. Probes available subtitle tracks, picks the right one (preferring human-authored over auto-captions, `<lang>-orig` over plain `<lang>`), fetches SRT. |
| `talk-transcribe` | SRT → speaker-labelled paragraph transcript. Wraps `scripts/srt_to_transcript.py`. |
| `talk-summarize` | Transcript → `executive_summary.md` (TL;DR + Salient Points + Outline). |
| `talk-takeaways` | Transcript (with timestamps) → `key_takeaways.md` (timestamped emoji-bullet index). |

Skills are v0.1.1 because they're written but not yet stress-tested on
a wide variety of talks (different speakers, manual vs. auto captions,
single-speaker vs. Q&A, non-English). The defaults are validated on the
two Tony Kay statechart talks; they'll need refinement as the family is
exercised on more material.

## Repo layout

```
talk-distill-skills/
├── README.md                          # this file
├── LICENSE                            # MIT
├── .gitignore
├── workflow_notes.md                  # design notes, heuristics, lessons learned
├── scripts/
│   └── srt_to_transcript.py           # the `talk-transcribe` implementation
└── skills/
    ├── talk-distill/{SKILL.md, VERSION, CHANGELOG.md}
    ├── talk-fetch/{...}
    ├── talk-transcribe/{...}
    ├── talk-summarize/{...}
    └── talk-takeaways/{...}
```

`scripts/` is **tracked** here, deviating from the convention in
`warmed-skills`/`yegor-pm-skills` of gitignoring it. The script isn't a
personal utility — it's the artifact this repo is built around.

## Using the script today

The script works standalone before any skill exists:

```bash
# 1. Fetch the SRT (yt-dlp >= 2025 strongly recommended; older builds
#    can list captions but fail to download them on current YouTube)
yt-dlp --skip-download --write-auto-subs --sub-langs en-orig \
       --convert-subs srt \
       --output "%(title)s.%(ext)s" \
       "https://www.youtube.com/watch?v=<VIDEO_ID>"

# 2. Convert to a speaker-labelled transcript
python3 scripts/srt_to_transcript.py captions.srt transcript.txt \
        --speakers "Tony Kay,Host" \
        --preamble-skip 27
```

Run with `--help` for the full flag set. Defaults work on Tony-Kay-style
Zoom-recorded team talks; other speakers may need a different
`--preamble-skip` (the script trims meeting tech-check chatter at the
start; this value happens to fit Tony's habit and is the most common
per-video tuning point).

## Convention notes

Skill-author-repo conventions (carried over from the sister repos
`warmed-skills` and `yegor-pm-skills`):

- Each skill ships `SKILL.md` + `VERSION` + `CHANGELOG.md`, independently
  semver-versioned. The `VERSION` file and the frontmatter `version:`
  field move together.
- Symlink installed skills into `~/.claude/skills/<slug>` so edits land
  live in the next session.
- `research/` directory holds deep-reference docs per skill, added when
  needed. For now, [`workflow_notes.md`](workflow_notes.md) at the repo
  root serves as the family's research doc.

## License

MIT — see [LICENSE](LICENSE).
