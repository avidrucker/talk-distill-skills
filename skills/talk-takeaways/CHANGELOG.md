# Changelog — talk-takeaways

## [0.1.1] — 2026-05-26

Clarification, no behavior change. Removed misleading "Yegor-Bugayenko-
style" qualifier from the format description — Yegor didn't define the
timestamped emoji-bullet structure; it was just the structure used in
`yegor-pm-skills/XDSD_YouTube_Talk/key_takeaways.md`, which happened to
be indexing a Yegor talk. Format is now described structurally
(`key_takeaways.md` — flat list of timestamp-anchored emoji-prefixed
bullets), with `yegor-pm-skills` credited as the source of the file
shape rather than as an eponymous style.

## [0.1.0] — 2026-05-26

Initial draft. No script — pure prompt for Claude. Locks in the
flat timestamp-anchored emoji-prefixed bullet structure, inherited from
the `key_takeaways.md` shape in `yegor-pm-skills`. Documents an emoji
palette as suggestion rather than enforced mapping, the SRT-grep
technique for precise timestamps, and a target bullet count (~20-50
depending on talk length).

Known limitation acknowledged: the current `srt_to_transcript.py`
doesn't preserve inline timestamps, so SRT-grep is the precision route.
A future `talk-transcribe` version may emit a `transcript_timestamped.txt`
intermediate to make this easier.
