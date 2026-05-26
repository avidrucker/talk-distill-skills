# Workflow Notes — YouTube Talk → Transcript → Summary Pipeline

> Running notes for the **`talk-distill-skills`** project: the pipeline that
> ingests a YouTube video, dedupes its auto-captions into a clean transcript,
> labels speakers, and produces both an `executive_summary.md` (TL;DR +
> Salient Points + Outline) and a `key_takeaways.md` (timestamped
> emoji-bullet index). The eventual goal is a Claude Code skill family
> (parent `talk-distill` orchestrator + `talk-fetch` / `talk-transcribe`
> / `talk-summarize` / `talk-takeaways` sub-skills).
>
> Keep this doc honest about what worked, what didn't, and what surprised
> us — that's what makes the future skill correct rather than aspirational.
>
> **Companion repo for examples / test corpus:** the actual talk artifacts
> produced by running this pipeline live in
> [`fulcro-statecharts-talks`](https://github.com/avidrucker/fulcro-statecharts-talks)
> (two Tony Kay talks captured so far: the basics walkthrough and the
> 3.5-hour Statecharts Marathon). When this doc says "video #1" or
> "video #2", that's where to look.

## Source-material conventions (from `Documents/Study/AI/`)

Two prior repos established the shape:

| Repo | Layout |
|---|---|
| `warmed-skills` (Casey Muratori, bad-code talk) | `bad_code_talk/{captions.SRT, transcript.txt, talk_summary.md}` |
| `yegor-pm-skills` (Yegor Bugayenko, XDSD talk) | `XDSD_YouTube_Talk/{XDSD_talk_yegor_2016.srt, *.txt, key_takeaways.md}` |

Both use a **`main` + `talks` branch split**: curated summary on `main`, bulky
`captions.SRT` + `transcript.txt` on `talks`. The reasoning: SRT and verbose
transcript are recoverable from YouTube via `yt-dlp` anyway, so a default
clone stays lean while the cite-and-quote material is one branch-switch away.

Two distinct summary shapes were already established in those repos:

- **`talk_summary.md`** (in `warmed-skills/bad_code_talk/`): TL;DR + Salient
  Points + Outline. First-read friendly, prose, structured.
- **`key_takeaways.md`** (in `yegor-pm-skills/XDSD_YouTube_Talk/`): timestamps
  + emoji bullets. Re-navigation friendly, scannable, links into the
  video's timeline.

(Those filenames are inherited from the source repos; we use them as the
canonical shapes for this family's two summary deliverables. The shapes
are NOT attributable to Casey Muratori or Yegor Bugayenko personally —
those were just the speakers of the talks each repo was summarising.)

The user picked **both** for this video, so we'll produce one of each
(under the warmed-skills file name `executive_summary.md` for the first
shape — we standardized on that name going forward).

## Decisions for *this* video (Tony Kay, statecharts)

| Decision | Value | Why |
|---|---|---|
| Repo layout | warmed-skills mirror (main + talks branches, eventually) | Matches established convention; future meta-skill expects this shape |
| Subdir | `fulcro_statecharts_talk/` | warmed-skills `bad_code_talk` style — descriptive, lowercase, scoped (Fulcro, not generic statecharts) |
| SRT filename | `captions.SRT` | Matches warmed-skills |
| Caption track | `en-orig` (English Original auto-captions) | The only kind available — this video has no human-authored subs |
| Transcript style | Light edit, near-literal, with speaker labels | The preview the user picked showed `Tony Kay: …` / `Host: …` — same shape as `yegor-pm-skills/XDSD_YouTube_Talk/XDSD_talk_yegor_2016.txt` |
| Meta-opening (~20s of "Start recording / Share screen / Bigger") | Replace with a single `[Preamble: tech check]` marker | Acknowledges structural opening without preserving the noise |
| Speaker names | `Tony Kay` + generic `Host` | Other speaker's name not knowable from captions alone |
| Summary deliverables | Both `executive_summary.md` (TL;DR + Salient + Outline shape) AND `key_takeaways.md` (timestamped emoji-bullet shape) | Reader gets first-read AND re-navigation entry points |

## Steps taken (with gotchas)

### 1. Confirmed yt-dlp could see the video and probed sub availability

```bash
yt-dlp --list-subs --skip-download <url>
yt-dlp --print "title" --print "uploader" --skip-download <url>
```

**Finding:** only auto-captions, no human-authored subs. Both `en` and
`en-orig` listed; for English-original audio they're typically identical.
Picked `en-orig`.

### 2. Hit a YouTube/yt-dlp version wall

The apt-installed `yt-dlp 2024.04.09` could list subtitle metadata but failed
to download them with "Did not get any data blocks" — YouTube's protections
have tightened in 2026.

**Fix landed in dotfiles** (not a project-local fudge): moved `yt-dlp` from
the apt section of `~/dotfiles/install.sh` into `install_cli_tools` as a
GitHub-release standalone (`~/.local/bin/yt-dlp`, idempotent install,
auto-removes the stale apt version to prevent PATH shadowing). The fresh
2026.03.17 build then fetched cleanly.

**Lesson for the eventual skill:** include a pre-flight check that warns
if `yt-dlp` is older than ~12 months and links to the upgrade path.

### 3. Fetched the SRT

```bash
yt-dlp --skip-download --write-auto-subs \
       --sub-langs en-orig --convert-subs srt \
       --output "fulcro_statecharts_talk/%(title)s.%(ext)s" <url>
```

yt-dlp writes VTT by default for YouTube captions and converts to SRT in a
post-processing pass (`--convert-subs srt`). Then we renamed
`Statecharts.en-orig.srt` → `captions.SRT` to match the warmed-skills
convention.

### 4. SRT → transcript: the YouTube rolling-caption problem

YouTube auto-captions are **rolling**. The naive expectation ("each block has
one or two lines that get concatenated") is wrong. What we actually see is
two alternating block shapes:

- **Content block** (seconds-long duration): `<previous_bottom_line>\n<new_line>`
- **Transitional block** (10-millisecond duration): just `<previous_bottom_line>` (repeated)

If you naively concatenate every line of every block, you get 2-5x
duplication. If you take only the *last* line of each block, you still get a
duplicate from every transitional block. The fix: **take the last non-empty
line of each block AND dedup successive equal yields**.

The conversion lives in [`scripts/srt_to_transcript.py`](scripts/srt_to_transcript.py).

### 5. Speaker labels — the `>>` ambiguity

YouTube auto-captions mark speaker changes with `>>` at line-start, but in
practice the markers are noisy:

1. After a long pause, YouTube emits `>>` even when the same speaker resumes
   (treats silence-then-speech as "new speaker").
2. The presenter's monologue often has stray `>>` after rhetorical questions
   ("Right?" / "Okay.") — YouTube thinks it heard the audience.
3. When the audience DOES interject, YouTube reliably emits `>>` for them.
   But when the presenter resumes, YouTube often fails to emit `>>` again —
   so a naive toggle leaves the rest of the talk mis-labeled.

The script applies three heuristics, layered:

1. **Preamble cutoff + speaker reset** (`--preamble-skip N`): skip the first
   N seconds of meeting tech-check; emit a single `[Preamble: tech check]`
   marker; reset speaker to the presenter on resume.
2. **Skip-first-marker after preamble**: the very first `>>` after preamble
   is treated as "presenter starts speaking after silence" and ignored.
3. **Presenter-dominant auto-revert**: after every non-presenter paragraph
   is flushed, the next non-`>>` paragraph defaults back to the presenter.
   This catches the "Tony says 'Right?', audience says 'yeah', Tony continues
   for 5 paragraphs" pattern.
4. **Length-threshold post-pass** (`--relabel-long-nonpresenter MIN_WORDS`):
   any `Host:` paragraph above MIN_WORDS gets relabeled as the presenter.
   In a teaching talk, audience interjections are nearly always short; long
   "Host" paragraphs are almost always presenter content mis-attributed by
   stray `>>` markers.

**Final stats for this video**: 500 paragraphs total — 373 Tony / 126 Host.
That ratio still over-counts Host slightly; the Q&A section is where the
length heuristic can't catch presenter mis-labels (Tony coaches in short
sentences and YouTube hallucinates interjections). The transcript content is
faithful; the labels are ~95% correct in the body, ~80% correct in the Q&A.

**One manual correction** was applied: line 17 ("All right. So as most of
you already kind of know, I" — Tony's actual content opener) was hand-flipped
from Host to Tony Kay.

## Open issues / future improvements for the skill

- **Pre-flight `yt-dlp` version check**. If the binary is more than ~12 months
  old, warn loudly. Optionally invoke `yt-dlp -U` if installed via the dotfiles
  pattern (`~/.local/bin/yt-dlp`, user-writable).
- **Sub-track selection logic**. For now this is hand-asked. The skill could:
  - Always prefer human-authored subs if present.
  - Among auto-captions, prefer `<lang>-orig` over plain `<lang>`.
  - If multiple languages are likely-relevant (multilingual talk), ask.
- **Speaker-name inference**. The video's description / metadata sometimes
  names participants. The skill could `yt-dlp --print description` and grep
  for name patterns.
- **Smarter speaker attribution**. Length-threshold is crude. An LLM-based
  pass over the transcript could correctly attribute every paragraph using
  context (Tony is the presenter, audience asks questions, etc.) — but that
  adds API cost and complexity. Weigh against the user's tolerance for
  remaining mis-labels.
- **Reusable convention for the talk subdir name**. Today the user chose
  `fulcro_statecharts_talk/` interactively. The skill could either always
  ask, or default to a derived name from the video title + uploader.
- **Both summary shapes auto-generated**. The `executive_summary.md`
  shape is a free-form Claude task. The `key_takeaways.md` shape requires
  choosing N timestamps, which means the LLM needs the timestamped
  transcript (not just the flattened text) — implying we should emit
  `transcript_timestamped.txt` as a third artifact, or include timestamps
  inline in `transcript.txt`.
- **Repo-init / branch split** is still TODO for this video.  Currently
  files are in a flat working directory; we have not done `git init` or
  set up the `main`/`talks` branch split. Defer this until we know how
  many videos / artifacts will live in this repo.

## Cross-video stress test — Video #2 (`fulcro_statecharts_marathon`)

Same speaker (Tony Kay), different shape: **3h 28m** vs. 76 min; explicitly an
"advanced topics" talk with a brief review at the start; recorded over the
same screen-share/Zoom format; auto-captions only (`en` + `en-orig` again).

### What worked unchanged

- **yt-dlp fetch**: same command line, no surprises.
- **Rolling-caption dedup** (last-line-per-block + successive-line dedup):
  scaled cleanly to 49,645 SRT lines → 4,942 unique deduped lines → 1,107 paragraphs.
- **Preamble cutoff at 27s**: happened to land at the right point AGAIN.
  Either Tony has a consistent ~27s tech-check habit, or this is luck.
  Worth probing more videos before locking in 27s as the skill default.
- **Presenter-dominant auto-revert**: kept Tony at ~78% of paragraphs on
  the marathon (matches the actual lecture-heavy distribution). The
  one-paragraph lag on stray `>>` is the same minor cosmetic issue as before.
- **Length-threshold post-pass (25 words)**: catches the longer mis-labels
  the same way it did on Video #1.

### What was *better* on the marathon

- **Speaker labels are noticeably cleaner overall.** The opening section
  ("All right, Luke. It is" → "Okay, so my intention here is to mainly talk
  about the more advanced…") came out *correctly attributed without manual
  fixes*. The talk has fewer of those short rhetorical "Right? / Okay." gaps
  that triggered spurious `>>` in Video #1.
- Even the substantive teaching body has clean labels — questions land on
  Host, answers land on Tony, without the constant Host-mis-label flicker
  Video #1 had in its 200-700 line range.

### What's still rough (same issues, same workarounds)

- Short two-or-three-word utterances (`Host: Yep.`, `Host: Okay.`,
  `Tony Kay: Yeah.`) mostly come out plausible-but-not-verifiable. They're
  too short for the length heuristic to help, and YouTube's `>>` placement is
  arbitrary on filler.
- A small number of mid-section paragraphs (~5-10 in the marathon) are
  labelled `Host:` when context shows they're Tony continuing. The pattern
  is identical to Video #1 — one paragraph mis-labelled, auto-revert catches
  the next.

### Cross-video conclusions (lock in for the eventual skill)

- **Defaults are sound.** `--preamble-skip 27`, `--paragraph-pause 4.0`,
  `--sentence-pause 2.0`, `--relabel-long-nonpresenter 25` produce usable
  output on both videos without per-video tuning.
- **Speaker labels: rough is good enough.** The remaining mis-labels are
  all in short-utterance territory where an LLM-pass *would* help but
  isn't worth the API call cost given the content is faithful regardless.
  When we eventually write the `talk-transcribe` sub-skill, document this
  honestly — speaker labels are 90–95% accurate; readers should verify when
  it matters.
- **Variations we still haven't stress-tested**:
  - Single-speaker (lecture with no Q&A) — would the `>>` heuristics
    over-fire?
  - Manually-authored subtitles (vs. auto-captions) — does the rolling-block
    pattern even apply?
  - Non-English audio — does `en-orig` still mean what we think it means?
  - Different uploader / talk format (conference talk, tutorial, podcast).
  - **Defer skill authoring** until at least one of these is also validated.
- **Memory caveat to apply on future videos**: even when the script's
  defaults work, *spot-check the opening section* before declaring the
  transcript "done". The 27s preamble cut is a heuristic that happens to
  fit Tony's habit; other speakers will need different values.

## Skill family — drafted at v0.1.1

Names locked 2026-05-25; v0.1.0 drafts written 2026-05-26; v0.1.1
clarification (dropping misleading "Casey-/Yegor-style" qualifiers from
descriptions) same day.

- Parent meta-skill: **`talk-distill`** (orchestrator; structurally the
  same shape as `yegor-pm` — parent + sub-skills routing).
- Sub-skills:
  - `talk-fetch` — yt-dlp wrapper, picks the right sub track, handles preflight checks.
  - `talk-transcribe` — SRT → speaker-labelled transcript with the dedup + speaker-toggle heuristics piloted here.
  - `talk-summarize` — transcript → `executive_summary.md` (TL;DR + Salient Points + Outline structure).
  - `talk-takeaways` — transcript (with timestamps from SRT cross-ref) → `key_takeaways.md` (timestamped emoji-bullet structure).

Skills are intentionally at v0.1.1, not v1.0. The defaults work on the
two Tony Kay statechart talks; they need stress-testing on at least one
video with a different shape (manual subs, non-English audio, or
single-speaker / no `>>`s) before declaring them stable.

## Repo layout — split into two

Done (2026-05-26). The original `statecharts-onboarding-video/` working
directory was split into two public repos in deliberately separate
namespaces on disk:

- **[`talk-distill-skills`](https://github.com/avidrucker/talk-distill-skills)**
  → `~/Documents/Study/AI/avi_drucker/talk-distill-skills/` (this repo).
  The `avi_drucker/` sub-namespace under `Study/AI/` is for skills
  authored by Avi himself, separate from skills distilled from someone
  else's work (`warmed-skills` ← Casey Muratori, `yegor-pm-skills` ←
  Yegor Bugayenko, both at `Study/AI/` top level).
  Single branch. Contents: `scripts/srt_to_transcript.py`,
  `workflow_notes.md`, and `skills/` + `research/` as they're authored.
- **[`fulcro-statecharts-talks`](https://github.com/avidrucker/fulcro-statecharts-talks)**
  → `~/Documents/Study/Fulcro/fulcro-statecharts-talks/`. Lives alongside
  other Fulcro learning material (`fulcro-book/`, `fulcro-solo-learn/`)
  rather than in `Study/AI/`, because the *content* is Fulcro learning;
  only the pipeline that produced it is AI-related.
  Two-branch split per the warmed-skills convention: `main` has just the
  curated `executive_summary.md` + `key_takeaways.md`; `talks` adds the
  bulky `captions.SRT` + `transcript.txt`.

## Memory captured during this session

- `feedback_dotfiles_central.md`: Tool-version changes go in `~/dotfiles`,
  user runs install.sh themselves. Established when the user redirected
  the yt-dlp upgrade away from a project-local `./bin/yt-dlp` proposal.
