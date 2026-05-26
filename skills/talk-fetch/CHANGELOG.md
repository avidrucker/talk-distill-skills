# Changelog — talk-fetch

## [0.1.0] — 2026-05-26

Initial draft. yt-dlp wrapper for fetching the best subtitle track from
a YouTube URL. Covers the preflight version check (the apt-shipped
yt-dlp ages out of YouTube compatibility roughly every six months), the
human-subs-over-auto-captions preference, the `<lang>-orig` preference
within auto-captions, and the canonical-filename rename to `captions.SRT`.
