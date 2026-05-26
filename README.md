# talk-distill-skills

The pipeline (and eventual [Claude Code](https://claude.com/claude-code)
skill family) for turning a YouTube talk into a clean speaker-labelled
transcript, an executive summary, and a timestamp-anchored key-takeaways
index — usable as personal study material.

Sister project to [`warmed-skills`](https://github.com/avidrucker/warmed-skills)
and [`yegor-pm-skills`](https://github.com/avidrucker/yegor-pm-skills):
same general shape (research + skills), different focus (workflow tooling
rather than philosophy distillation).

## Why this exists

Casey Muratori's WARMED talk and Yegor Bugayenko's XDSD talk each got
hand-curated SRT → transcript → summary treatment in those sister repos.
That process was manual every time. This repo's goal is to **automate the
SRT-to-summary pipeline as a reusable Claude Code skill**, so the next
talk distillation is mostly a `/talk-distill <youtube-url>` away.

The actual talk artifacts produced by the pipeline so far live in
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
- ⏳ Skills not yet authored. The plan is a meta-skill `talk-distill` that
  orchestrates four sub-skills:

| Skill (planned) | Responsibility |
|---|---|
| `talk-fetch` | `yt-dlp` wrapper. Probes available subtitle tracks, picks the right one (preferring human-authored over auto-captions, `<lang>-orig` over plain `<lang>`), fetches SRT. |
| `talk-transcribe` | SRT → speaker-labelled paragraph transcript. The current `srt_to_transcript.py` is the candidate implementation. |
| `talk-summarize` | Transcript → Casey-style `executive_summary.md` (TL;DR + Salient Points + Outline). |
| `talk-takeaways` | Transcript (with timestamps) → Yegor-style `key_takeaways.md` (timestamped navigation index). |
| `talk-distill` | Parent / meta-orchestrator that runs the four above in sequence on a single YouTube URL. |

Deferring skill authoring until the pipeline has been run on a wider
variety of talks (different speakers, manual vs. auto captions,
single-speaker vs. Q&A, non-English) so the abstractions are validated
rather than over-fit to two Tony Kay talks.

## Repo layout

```
talk-distill-skills/
├── README.md                          # this file
├── LICENSE                            # MIT
├── .gitignore
├── workflow_notes.md                  # design notes, heuristics, lessons learned
├── scripts/
│   └── srt_to_transcript.py           # the candidate `talk-transcribe` implementation
└── skills/                            # (will appear when skills are authored)
    └── talk-<slug>/{SKILL.md, VERSION, CHANGELOG.md}
```

`scripts/` is **tracked** here, deviating from the
warmed-skills/yegor-pm-skills convention of gitignoring it. The script
isn't a personal utility — it's the artifact this repo is built around.

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

This repo follows the established skill-author-repo shape from
[`warmed-skills`](https://github.com/avidrucker/warmed-skills) and
[`yegor-pm-skills`](https://github.com/avidrucker/yegor-pm-skills):

- Skills (when authored) ship `SKILL.md` + `VERSION` + `CHANGELOG.md` per
  skill, independently semver-versioned.
- Symlink installed skills into `~/.claude/skills/<slug>` so edits land
  live in the next session.
- `research/` directory holds deep-reference docs per skill (added
  when skills are authored).

## License

MIT — see [LICENSE](LICENSE).
