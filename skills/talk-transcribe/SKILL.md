---
name: talk-transcribe
description: Convert an SRT (typically YouTube auto-captions) into a clean speaker-labelled paragraph transcript. Use when the user has `captions.SRT` and wants `transcript.txt`. Wraps `scripts/srt_to_transcript.py`, which handles rolling-caption dedup, `>>` speaker-toggle, presenter-dominant auto-revert, and a length-threshold relabel post-pass.
version: 0.1.0
last_reviewed: 2026-05-26
---

# Talk Transcribe — Sub Skill

Turn an SRT into `transcript.txt`: paragraph-flowed, speaker-labelled,
preamble-trimmed, near-literal text suitable for reading and citing.

## When to invoke

- `talk-distill` runs this after `talk-fetch`.
- User has an SRT (from anywhere — YouTube, Vimeo, a `.srt` file on disk)
  and asks for "a transcript" / "a clean transcript" / "speaker-labelled
  text" / etc.

## What the script does (and why)

The script lives at `scripts/srt_to_transcript.py` in the source repo
([avidrucker/talk-distill-skills](https://github.com/avidrucker/talk-distill-skills)).
It applies four heuristics, layered:

1. **Rolling-caption dedup**. YouTube auto-captions interleave "content"
   blocks (long-duration: `prev_line\nnew_line`) with 10ms "transitional"
   blocks (just `prev_line` repeated). Taking the last non-empty line of
   each block AND deduping successive equal yields recovers the unique
   spoken stream.
2. **Preamble cutoff**. Skips the meeting tech-check chatter at the start
   ("can you hear me / share screen / bigger") and emits a single
   `[Preamble: tech check]` marker.
3. **Speaker toggle on `>>`** + **skip-first-marker** + **presenter-
   dominant auto-revert**. YouTube emits `>>` on speaker change but
   inconsistently: it fires `>>` on the audience interjection but often
   misses the presenter's resume. Auto-revert defaults the next paragraph
   back to the presenter unless a fresh `>>` says otherwise.
4. **Length-threshold relabel post-pass**. Any non-presenter paragraph
   above N words (default 25) is relabeled as the presenter — in a
   teaching talk, audience interjections are almost always short.

## Default invocation

```bash
python3 scripts/srt_to_transcript.py \
        "$SUBDIR/captions.SRT" \
        "$SUBDIR/transcript.txt" \
        --speakers "$PRESENTER,$OTHER" \
        --preamble-skip 27
```

The defaults shipped with the script work on Tony-Kay-style Zoom-recorded
team talks without further tuning. Other speakers / formats need at most
one knob tweaked: `--preamble-skip`. See "Tuning per video" below.

Full flag list (run `--help` for canonical):

| Flag | Default | When to tune |
|---|---|---|
| `--speakers "Name1,Name2"` | `"Tony Kay,Host"` | Set both names. The first is the presenter (toggle origin); the second is whoever interjects. Use a generic label like `Host` or `Q` if the second speaker's name is unknown. |
| `--preamble-skip 27.0` | 27.0 s | Probe the SRT first: how long is the tech-check chatter? Set to just after the last meta-utterance. |
| `--paragraph-pause 4.0` | 4.0 s | Lower for fast-paced talks; raise for slow speakers. Forces a paragraph break on any gap above this. |
| `--sentence-pause 2.0` | 2.0 s | Forces a paragraph break after `.?!` when the gap is at least this. |
| `--relabel-long-nonpresenter 25` | 25 words | Lower aggressively (e.g. 15) for talks with very short audience interjections. Set to `0` to disable entirely. |

## Tuning per video

Almost always the only thing worth tuning is `--preamble-skip`. To pick it:

```bash
# 1. Peek at the SRT around the first content block
head -200 "$SUBDIR/captions.SRT"

# 2. Find where the actual presentation starts (vs the "share screen /
#    can you hear me / bigger" chatter). Pick a number of seconds just
#    past the last meta-utterance.
# 3. Re-run with that value.
```

If the talk has no preamble at all (e.g. a pre-recorded conference
talk), pass `--preamble-skip 0`. The script will still emit the
`[Preamble: tech check]` marker for the very first paragraph, which
you can hand-remove.

## Output

- `${SUBDIR}/transcript.txt` — paragraph-flowed, `Presenter: …` /
  `Other: …` labels, single `[Preamble: tech check]` line at the top.

Stats printed to stderr: paragraph count, SRT block count, output path.

## Caveats — speaker label accuracy

**Speaker labels are ~90–95% accurate in the body, ~80% in the Q&A**. The
content (the words spoken) is faithful regardless. Sources of error:

- YouTube's `>>` placement is inconsistent: it fires on audience
  interjection but sometimes misses presenter resume. Auto-revert
  catches *most* of these; what slips through is a single mis-labeled
  paragraph at each transition the auto-revert can't catch.
- Short utterances (≤25 words) get the heuristic relabel benefit but
  the heuristic itself is conservative. A short Tony-says line followed
  by silence will sometimes label as Host.
- Spot-check the opening section (first ~20 paragraphs) by hand — that's
  where the meeting setup chatter has wonky toggles and the manual
  correction cost is lowest.

Tone-of-voice for any downstream skill (summary / takeaways): trust the
content, treat the speaker labels as suggestions.

## Deep reference

[`workflow_notes.md`](../../workflow_notes.md) §"SRT → transcript: the
YouTube rolling-caption problem" and §"Speaker labels — the `>>`
ambiguity" cover the heuristic design in depth, including failed
approaches we ruled out.
