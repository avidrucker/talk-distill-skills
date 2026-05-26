#!/usr/bin/env python3
"""Convert a YouTube auto-caption SRT into a light-edit, speaker-labelled transcript.

YouTube auto-captions arrive as a "rolling" stream: each subtitle block repeats
the previous block's last line and appends one new line. Concatenating naively
produces 2-5x duplication. The dedup here is simple and robust: take only the
last non-empty line of each block. `>>` line-start markers are YouTube's
speaker-change signal; we toggle between two configured speaker names.

Usage:
    srt_to_transcript.py <input.srt> <output.txt> \
        [--speakers "Tony Kay,Host"] \
        [--preamble-skip 20] \
        [--paragraph-pause 4.0] \
        [--sentence-pause 2.0]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def parse_srt(path: Path):
    """Yield (start_seconds, text_line) tuples for the unique new line of each
    SRT block, robust against YouTube's rolling-caption format.

    YouTube auto-captions interleave two block shapes:
      - Long "content" blocks carrying "<previous_bottom_line>\\n<new_line>".
      - 10ms "transitional" blocks repeating just <previous_bottom_line>.
    Taking the last non-empty line of each block surfaces every new utterance
    once, but the transitional blocks then emit a duplicate of what the prior
    content block already emitted. We therefore also dedup successive equal
    emissions before yielding.
    """
    content = path.read_text(encoding="utf-8")
    blocks = re.split(r"\n\s*\n", content.strip())
    prev_line = None
    for block in blocks:
        lines = block.split("\n")
        tc_idx = None
        for i, line in enumerate(lines):
            if "-->" in line:
                tc_idx = i
                break
        if tc_idx is None:
            continue
        start_ts = lines[tc_idx].split("-->")[0].strip()
        try:
            h, m, rest = start_ts.split(":")
            s, ms = rest.split(",")
            start_sec = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        except (ValueError, IndexError):
            continue
        last_nonempty = ""
        for cl in reversed(lines[tc_idx + 1 :]):
            stripped = cl.strip()
            if stripped:
                last_nonempty = stripped
                break
        if not last_nonempty or last_nonempty == prev_line:
            continue
        prev_line = last_nonempty
        yield start_sec, last_nonempty


def stream_to_paragraphs(
    blocks,
    speakers=("Tony Kay", "Host"),
    preamble_skip_seconds=20.0,
    paragraph_pause=4.0,
    sentence_pause=2.0,
    presenter_dominant=True,
):
    """Group deduped lines into (speaker, paragraph_text) tuples.

    Heuristics:
      - Toggle speakers on `>>` line-start (YouTube's speaker-change marker).
      - Skip everything before preamble_skip_seconds; emit one `_meta` row in its place.
      - Within one speaker's turn, start a new paragraph on a >paragraph_pause gap,
        or on a >sentence_pause gap following sentence-ending punctuation.
      - **Presenter-dominant auto-revert** (default on): after every non-presenter
        paragraph is flushed, the next paragraph defaults back to the presenter
        (speakers[0]) unless that paragraph carries its own `>>` marker. YouTube
        often fails to emit `>>` when the presenter resumes after an interjection,
        which would otherwise label the rest of the talk under the wrong speaker.
        Disable with presenter_dominant=False if you have multi-paragraph
        audience turns that aren't separated by their own `>>` markers.
    """
    speaker_idx = 0
    words = []
    last_ts = 0.0
    preamble_emitted = False
    # The first `>>` right after the preamble is usually YouTube marking
    # "speech resuming after a silent gap" (presenter starting), not a real
    # alternation between speakers — so we eat it without toggling.
    skip_first_marker = False
    revert_pending = False
    out = []

    def flush():
        nonlocal words, revert_pending
        if words:
            out.append((speakers[speaker_idx], " ".join(words)))
            words = []
            # If the speaker we just flushed isn't the presenter, queue an
            # auto-revert for the next paragraph (presenter-dominant model).
            if presenter_dominant and speaker_idx != 0:
                revert_pending = True

    for ts, line in blocks:
        if not preamble_emitted:
            if ts < preamble_skip_seconds:
                last_ts = ts
                continue
            out.append(("_meta", "[Preamble: tech check]"))
            preamble_emitted = True
            # The chitchat before the preamble cutoff is often mis-toggled
            # because both speakers exchange short polite words. Reset to the
            # first configured speaker (the presenter) when real content begins.
            speaker_idx = 0
            skip_first_marker = True
            last_ts = ts

        if line.startswith(">>"):
            flush()
            revert_pending = False  # explicit >> overrides any pending revert
            if skip_first_marker:
                skip_first_marker = False
            else:
                speaker_idx = 1 - speaker_idx
            line = line[2:].strip()
        elif revert_pending:
            # No explicit speaker marker on this paragraph; presenter-dominant
            # heuristic says we're back to speakers[0] (the presenter).
            speaker_idx = 0
            revert_pending = False

        gap = ts - last_ts
        if words and gap > paragraph_pause:
            flush()
        elif (
            words
            and gap > sentence_pause
            and words[-1].rstrip().endswith((".", "?", "!"))
        ):
            flush()

        if line:
            words.append(line)
        last_ts = ts

    flush()
    return out


def relabel_long_nonpresenter_paragraphs(paragraphs, speakers, min_words=25):
    """Post-pass: relabel non-presenter paragraphs above `min_words` as the
    presenter (speakers[0]). YouTube auto-captions sprinkle stray `>>` markers
    inside the presenter's monologue (often after rhetorical "Right?" / "Okay.");
    each one mis-labels exactly one paragraph as the non-presenter before the
    auto-revert heuristic catches the next. Audience interjections in teaching
    talks are nearly always short, so a length-threshold cleanup recovers most
    of the false positives without re-labeling legitimate audience turns.
    Pass min_words=0 (or None) to disable.
    """
    if not min_words:
        return paragraphs
    presenter = speakers[0]
    out = []
    for speaker, text in paragraphs:
        if speaker not in ("_meta", presenter) and len(text.split()) >= min_words:
            out.append((presenter, text))
        else:
            out.append((speaker, text))
    return out


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--speakers", default="Tony Kay,Host",
                   help='Comma-separated speaker names, in toggle order. Default: "Tony Kay,Host".')
    p.add_argument("--preamble-skip", type=float, default=20.0,
                   help="Seconds of opening to skip (replaced with a [Preamble: tech check] marker). Default: 20.")
    p.add_argument("--paragraph-pause", type=float, default=4.0,
                   help="Gap (seconds) within one speaker's turn that forces a paragraph break. Default: 4.")
    p.add_argument("--sentence-pause", type=float, default=2.0,
                   help="Gap (seconds) after a sentence-ending punctuation that forces a paragraph break. Default: 2.")
    p.add_argument("--relabel-long-nonpresenter", type=int, default=25, metavar="MIN_WORDS",
                   help="Post-pass: relabel non-presenter paragraphs with >=MIN_WORDS words as the presenter (recovers from spurious >> markers in monologue). Pass 0 to disable. Default: 25.")
    args = p.parse_args(argv)

    speakers = tuple(s.strip() for s in args.speakers.split(","))
    if len(speakers) < 2:
        print("--speakers needs at least two comma-separated names", file=sys.stderr)
        return 2

    blocks = list(parse_srt(args.input))
    paragraphs = stream_to_paragraphs(
        blocks,
        speakers=speakers,
        preamble_skip_seconds=args.preamble_skip,
        paragraph_pause=args.paragraph_pause,
        sentence_pause=args.sentence_pause,
    )
    paragraphs = relabel_long_nonpresenter_paragraphs(
        paragraphs, speakers, min_words=args.relabel_long_nonpresenter
    )
    with args.output.open("w", encoding="utf-8") as f:
        for speaker, text in paragraphs:
            if speaker == "_meta":
                f.write(f"{text}\n\n")
            else:
                f.write(f"{speaker}: {text}\n\n")
    print(f"wrote {len(paragraphs)} paragraphs from {len(blocks)} SRT blocks -> {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
