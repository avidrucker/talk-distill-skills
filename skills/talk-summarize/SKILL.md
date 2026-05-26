---
name: talk-summarize
description: Read a talk transcript and produce an executive_summary.md (TL;DR + Salient Points + Outline). Use when the user wants a first-read overview of a talk — prose, structured, and skimmable. No script involved; pure prompt-engineering for Claude.
version: 0.1.1
last_reviewed: 2026-05-26
---

# Talk Summarize — Sub Skill

Read `transcript.txt` for a talk and write `executive_summary.md` using
the **TL;DR + Salient Points + Outline** structure. This is the first-read
entry point — the doc someone opens when they want to know what the talk
is about *before* deciding to watch it.

(This format / file name was first used in
[`warmed-skills`](https://github.com/avidrucker/warmed-skills) for a
Casey Muratori talk; the structure is what's inherited, not anything
attributable to Casey.)

## When to invoke

- `talk-distill` runs this after `talk-transcribe`.
- User has a transcript and asks for "a summary" / "an executive summary" /
  "a brief on this talk" / "what's the gist" / etc.
- User asks for a "talk_summary.md" — same shape, different filename per
  the older warmed-skills convention. Honor whichever filename the user
  asks for.

## Required structure

The output is a single Markdown file with these sections in this order:

```markdown
# <Talk title> — <Speaker>

**Source:** <one-line framing: what kind of talk, where it was given/posted, runtime>

**Audience:** <who the talk was originally for; who else was on the recording if relevant>

---

## TL;DR

<one or two paragraphs. The whole talk distilled into something a reader
can absorb in 60 seconds. Be specific — name the core thesis, the
mechanism, the surprising bit. Avoid generic "the speaker discusses X"
filler. Compare:

  Weak: "The speaker discusses statecharts and their advantages."
  Strong: "Statecharts are hierarchical state machines you express as
   a nested map; the clever bit on the backend is putting the event
   queue AND the working-memory store in the same SQL database so the
   whole load → run → save → mark-delivered sequence commits as one
   ACID transaction.">

---

## Salient Points

### <Theme 1 — descriptive heading, not "Section 1">
<2-5 bullet points OR a paragraph or two. One concrete claim per bullet.
Quote the speaker briefly if it's a memorable phrasing.>

### <Theme 2>
<same shape>

[…7-15 thematic subsections total, depending on talk length…]

---

## Outline (rough timestamps)

1. **00:00–01:00** — <section topic>
2. **01:00–05:00** — <next topic>
[…flat numbered list mirroring the talk's actual flow…]
```

## Style rules

- **No emojis** in this format. Save those for `talk-takeaways`.
- **Prose over bullets** in TL;DR. Bullets are fine within Salient Points
  subsections.
- **Concrete > generic** everywhere. If a bullet could apply to any talk
  about any topic, rewrite it.
- **Quote sparingly**. Direct quotes are great when the speaker said
  something memorable; paraphrase when not.
- **No filler closers** like "In conclusion, the speaker emphasizes…".
  End the doc with the last Outline entry.

## How to read the transcript

The transcript is light-edit / near-literal — it preserves the speaker's
"uh"s and "kind of"s. **Don't quote those verbatim**; paraphrase to clean
prose. The speaker labels are ~90–95% accurate; lean on context (who's
explaining vs. asking) rather than blindly trusting the labels.

For long talks (>1 hour), it's often easier to read in stratified samples:
the first ~200 paragraphs in detail (this is where definitions land),
then sample at intervals through the middle, then the last ~100
paragraphs (where the speaker often summarizes their own thesis or
flags open questions).

## How to pick the Outline timestamps

The transcript itself doesn't carry inline timestamps (a known limitation
of the current pipeline). Two ways to assign Outline timestamps:

1. **Cross-reference the SRT.** For each paragraph at a topic boundary,
   find a distinctive phrase from the paragraph and `grep -n` it in
   `captions.SRT`. The block number above the matching line gives you the
   timestamp.
2. **Estimate.** Total runtime / total paragraph count × paragraph index
   gives a rough timestamp. Flag in TL;DR that timestamps are approximate
   if you go this route.

Method 1 is more work but produces jumpable timestamps that match the
video. Prefer it for talks worth re-watching; method 2 is fine for
once-over study material.

## Examples

Two reference summaries that this skill should produce something
comparable to — written by hand with the same structure before the skill
existed:

- [Fulcro statecharts (basics)](https://github.com/avidrucker/fulcro-statecharts-talks/blob/main/fulcro_statecharts_talk/executive_summary.md)
- [Fulcro statecharts (advanced marathon)](https://github.com/avidrucker/fulcro-statecharts-talks/blob/main/fulcro_statecharts_marathon/executive_summary.md)

Another example with the same structure, from the sister repo where
this file shape originated (filename there is `talk_summary.md`; the
content is the same TL;DR + Salient Points + Outline):

- [`bad_code_talk/talk_summary.md`](https://github.com/avidrucker/warmed-skills/blob/main/bad_code_talk/talk_summary.md)
  — Casey Muratori's "Where Does Bad Code Come From?"

## Output

- `${SUBDIR}/executive_summary.md`

## Caveats

- **Don't over-summarize.** A 3-hour talk can have a 1500-word summary; a
  20-minute talk should have something shorter. Length should track the
  amount of distinct content, not be a fixed cap.
- **Don't editorialize.** This is "what the speaker said," not "what I
  think about what the speaker said." Save commentary for a separate doc
  if the user wants it.
- **Test by reading aloud.** If a sentence sounds like LLM-prose
  ("delves into," "leverages," "robust framework for…"), rewrite it.
