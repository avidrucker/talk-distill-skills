# Changelog — talk-transcribe

## [0.1.0] — 2026-05-26

Initial draft. Wraps `scripts/srt_to_transcript.py`. Validated end-to-end
on two Tony Kay statechart talks of very different length (76 min and
3h 28m) — defaults work on both without per-video tuning. Documents
the four-heuristic layered approach (rolling-caption dedup, preamble
cutoff, presenter-dominant `>>` toggle with auto-revert, length-
threshold relabel) and the known speaker-label accuracy limits
(~90–95% body / ~80% Q&A).
