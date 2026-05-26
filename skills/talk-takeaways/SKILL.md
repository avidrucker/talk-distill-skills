---
name: talk-takeaways
description: Read a talk transcript (ideally plus the SRT for accurate timestamps) and produce a key_takeaways.md — a flat list of timestamp-anchored emoji-prefixed bullets for jumping back into the video. Use when the user wants a navigation index, not a read-through summary.
version: 0.1.1
last_reviewed: 2026-05-26
---

# Talk Takeaways — Sub Skill

Read `transcript.txt` (and `captions.SRT` for precise timestamps) and
write `key_takeaways.md`. This is the **re-navigation** entry point — the
doc someone opens when they've watched the talk and want to find a
specific moment, or when they want to skim the structure before deciding
which sections to watch.

(This format / file name was first used in
[`yegor-pm-skills`](https://github.com/avidrucker/yegor-pm-skills) for a
Yegor Bugayenko talk; the structure is what's inherited, not anything
attributable to Yegor.)

## When to invoke

- `talk-distill` runs this after `talk-transcribe` (often in parallel
  with `talk-summarize`).
- User asks for "key takeaways" / "a timestamp index" / "jump points" /
  "the highlights with timestamps" / etc.

## Required structure

```markdown
# Key Takeaways — <Talk title> (<Speaker>)

**Video:** <one-line context>
**Link:** https://www.youtube.com/watch?v=<id>
**Duration:** <h:mm:ss>

## Key takeaways for quick navigation

> Timestamps are approximate (deduced from the SRT). Append `&t=XXmYYs`
> to the YouTube link to jump.

- **00:00** <emoji> Preamble — <whatever the meta-setup is>. Skip to ~01:00 for content.
- **01:00** <emoji> <One-line gist of the next topic>
- **05:00** <emoji> <Next topic>
[…20-50 bullets total, depending on talk length…]
```

## Bullet style

Each bullet has three parts:

1. **Timestamp** in `**HH:MM**` or `**MM:SS**` format, depending on talk
   length. Use bold so it stands out.
2. **Emoji glyph** that hints at the topic category (no strict mapping —
   pick what feels right). Common patterns:
   - 🎯 for "key insight" / "thesis statement"
   - 🧠 for definitions / mental models
   - 🛠️ for tools / mechanisms / how-it-works
   - 🏗️ for architecture / design decisions
   - 💬 for Q&A / audience interaction
   - ❓ for open questions / future work
   - ⚠️ for caveats / warnings / common mistakes
   - 📚 for historical context / references to other work
   - 🔌 for "this connects to / is built on…"
   - 📐 for formal/spec content
   - 🐛 for war stories / things that went wrong
   - 🎬 for "this is where the demo / live coding happens"
   - 🏁 for closing / wrap-up
3. **One-line gist**. Specific. Should make sense without surrounding
   context. Compare:

       Weak: "Discussion of state machines."
       Strong: "Hierarchical states + parallel regions: how Tony's
        traffic-light example has 4 parallel branches alive at once."

## Picking bullets

Aim for **one bullet per major topic shift**, not per paragraph. The
transcript will have hundreds of paragraphs; a good takeaways doc has
20-50 bullets.

Topic shifts to bullet-mark:

- Speaker introduces a new section ("Okay, so now I want to talk about X").
- A demo / code-walkthrough begins.
- A war story is told.
- A Q&A exchange surfaces a non-obvious point.
- The speaker flags a "this is the BIG idea" moment.
- The talk closes / Q&A begins.

Skip:

- Filler ("uh, yeah, where was I").
- Pure tech-check chatter.
- Restatements of previously-covered material.

## How to assign timestamps

Two ways, in order of preference:

1. **From the SRT directly.** For each bullet, find a distinctive
   sentence from the corresponding transcript paragraph and `grep -n` it
   in `captions.SRT`. The timecode line just above the matching content
   line gives you the precise timestamp.

   ```bash
   grep -n "as most of you already kind of know" captions.SRT
   # then read the block above the matching line to get the timecode
   ```

2. **Approximate from paragraph index.** If only the transcript is
   available: `(paragraph_index / total_paragraphs) * total_duration`
   gives a rough timestamp. Round to a sensible 5-minute granularity
   to make it clear it's approximate.

The current `srt_to_transcript.py` script does NOT preserve inline
timestamps in `transcript.txt`. A future version of `talk-transcribe`
might emit a `transcript_timestamped.txt` to make this easier. Until
then, the SRT-grep approach is the precision route.

## Output

- `${SUBDIR}/key_takeaways.md`

## Examples

Two reference takeaways docs that this skill should produce something
comparable to — written by hand with the same structure before the
skill existed:

- [Fulcro statecharts (basics)](https://github.com/avidrucker/fulcro-statecharts-talks/blob/main/fulcro_statecharts_talk/key_takeaways.md)
  — ~25 bullets covering 76 min of content.
- [Fulcro statecharts (advanced marathon)](https://github.com/avidrucker/fulcro-statecharts-talks/blob/main/fulcro_statecharts_marathon/key_takeaways.md)
  — ~50 bullets covering 3 h 28 min.

The sister repo where this file shape originated (different emoji
choices, same structure):

- [`XDSD_YouTube_Talk/key_takeaways.md`](https://github.com/avidrucker/yegor-pm-skills/blob/talks/XDSD_YouTube_Talk/key_takeaways.md)
  — Yegor Bugayenko's XDSD talk.

## Caveats

- **Timestamps are jumpable, not exact.** Even from the SRT, the block
  boundary may be a few seconds off from where the topic actually starts.
  Good enough for navigation; not for legal citation.
- **Emoji is decoration.** Don't agonize. If unsure, pick one that's
  *roughly* topical and move on. The information is in the text, not
  the glyph.
- **The bullet count is a quality indicator.** Fewer than ~15 bullets
  for a 1-hour talk usually means under-segmentation (you're collapsing
  topics). More than ~80 means over-segmentation (you're per-paragraph
  bulleting). Re-balance.
