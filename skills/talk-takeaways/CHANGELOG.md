# Changelog — talk-takeaways

## [0.1.0] — 2026-05-26

Initial draft. No script — pure prompt for Claude. Locks in the Yegor-
Bugayenko style (flat list of timestamp-anchored emoji-prefixed bullets)
inherited from yegor-pm-skills' `key_takeaways.md`. Documents an emoji
palette as suggestion rather than enforced mapping, the SRT-grep
technique for precise timestamps, and a target bullet count (~20-50
depending on talk length).

Known limitation acknowledged: the current `srt_to_transcript.py`
doesn't preserve inline timestamps, so SRT-grep is the precision route.
A future `talk-transcribe` version may emit a `transcript_timestamped.txt`
intermediate to make this easier.
