---
name: branded-social-video
description: Turn raw footage plus a list of talking points into a finished vertical branded video — cut, on-screen text cards, logo watermark, brand endcard and an audio bed. Use this whenever someone wants footage turned into a social/ad/instructional video (Reels, TikTok, Shorts, YouTube Shorts), wants tips or steps or product features shown as text over video, wants captions or titles burned into a clip, wants a branded intro or endcard added, or drops video files in a folder and asks for "an ad", "a tips video", "a promo" or "edit these together" — even if they never say the words vertical, 1080x1920, or branded.
---

# Branded social video

Raw clips plus a handful of talking points, out the other end a finished
vertical video: cut to the beats, text on screen, brand marks in place, audio
that does not embarrass you.

The scripts here do the mechanical parts. Your job is the judgement — which
frames earn screen time, which words land, and whether the result is actually
watchable.

## Campaign intake and brand routing

For the condensed Drive/brand intake checklist, read `references/brand-drive-workflow.md`.

When footage arrives through a Google Drive link, first use the Google Workspace skill to list the linked folder, identify the source videos, and download a working copy without modifying the originals. Keep all generated files under the footage folder's `edit/` directory (or a clearly named local working directory) and return the rendered deliverables; upload them back to Drive only when a destination is specified.

The user's default campaign has two brand outputs: one for **OzArmour** and one for **BeeKeepingGear**. Route clips, logo assets, copy, colors, and endcards to the correct brand rather than mixing them. Use `http://ozarmour.co/` and `https://www.beekeepinggear.com.au/` as the official reference sites, rechecking current product details and offers before making factual claims. If site content is unavailable, use only claims supported by the supplied footage or user-provided copy and flag anything requiring confirmation.

This workflow is used both for normal chat requests and for self-contained recurring jobs. ElevenLabs is intentionally deferred for now; do not make it a prerequisite for footage inventory, visual review, text overlays, or rendering. If subtitles require unavailable word-level transcription, state that dependency clearly rather than silently fabricating captions.

When a phone `.mov` contains an embedded rotation matrix, unsupported auxiliary audio, or metadata streams, inspect the stream map first. Render with explicit mapping (`-map 0:v:0 -map 0:a:0`) and preserve the intended display orientation. ffmpeg normally applies the embedded display matrix automatically; do not also add `transpose` unless autorotation is disabled, or the phone footage may be rotated twice. Verify normalized output dimensions before adding captions or an end card. See `references/phone-rotation-and-brand-only-endcards.md` for the tested pattern.

## Subtitle legibility and local-ASR fallback

For subtitle-only edits or campaigns where ElevenLabs is intentionally deferred, use the local ASR and verification procedure in `video-use/references/local-asr-subtitles.md` when available. Do not ship a successful encode without inspecting rendered frames. Match the standing reference at `D:/Video Editing/Store Video/edit/final-before-endcard.mp4`: ASS at 1080x1920, Arial regular 52px, uppercase white text, black outline 2px, shadow 1px, centered alignment, margins L/R 60 and bottom 300. Keep the style identical across every caption; use natural phrase grouping and consistent wrapping around 34 characters per line, with no more than two lines. A long caption must be split at a natural pause instead of growing taller or covering the speaker/product. Explicitly map `0:v:0` and the first usable audio stream for phone `.mov` files that contain extra metadata or unsupported audio streams.

When a product page is supplied for the end card, download the official product image, remove its background before use, and create a polished 1080x1920 product card using the supplied logo, accurate product title/pack size, a simple CTA, and the requested website address. Append a 4–5 second card after the subtitle render unless another duration is requested. Visually inspect the card and final last frame before delivery, and keep the downloaded source, transparent product cutout, card artwork, script, verification frame, and final output in edit directories without modifying source footage.


```bash
python scripts/probe.py <videos_dir>          # true orientation, fps, audio
python scripts/contact_sheet.py "<clip>" 0.5 50 2.5 sheet.png
```

Read the contact sheet. It tells you what you actually have, and one sheet
replaces a dozen blind seeks.

`probe.py` exists for a specific reason: `ffprobe` reports **coded**
dimensions, and rotated phone footage reports `3840x2160` while displaying as
`2160x3840` vertical. Everything downstream — output size, crop decisions —
depends on getting this right, and the render succeeds either way, so a wrong
answer here surfaces as a strangely-shaped deliverable rather than an error.

**Ask before assuming**, but only where the answer changes the work: delivery
format if the sources are landscape, whether location audio is wanted, whether
there is a brand reference to match. Take your best shot at the rest.

## The format

One project file drives everything. Copy `assets/project.example.json` next to
the footage as `project.json` and fill it in.

```
<videos_dir>/
├── <source clips, never modified>
├── logo.png
├── project.json          ← cuts, copy, brand, audio, all of it
└── edit/                 ← everything generated
    ├── cards/            ← one PNG per text card
    ├── clips/            ← per-segment extracts (cached)
    ├── scrim.png  watermark.png  endcard.png
    ├── base.mp4  composite.mp4
    ├── final.mp4         ← the deliverable
    └── verify/           ← self-eval sheets
```

Never write into the source folder beyond `edit/` and `project.json`. People
re-shoot; their originals must stay pristine.

## Building it

```bash
python scripts/build_assets.py project.json    # scrim, cards, watermark, endcard
python scripts/render.py      project.json     # cut → concat → composite
python scripts/audio_bed.py   project.json     # audio → final.mp4
python scripts/selfeval.py    project.json     # check before delivering
```

Re-running is cheap: segments are cached by content, so changing copy or the
scrim re-composites without re-cutting.

### Why the pipeline is shaped this way

Per-segment extract → lossless concat → single composite pass. It is tempting
to do everything in one filtergraph, but then adding an overlay re-encodes the
picture twice. Cutting first and copying the concat keeps one encode.

Text is composited **last**, over the scrim and watermark. Anything drawn after
your captions will eventually cover them.

Each segment gets 30ms audio fades at both edges. Hard joins pop, and a pop is
the kind of thing nobody notices in review and everyone notices on real
speakers.

### Default audio policy

When source audio contains people talking, use `ambience_loop`, not `keep`.
Scan the source tracks with speech detection or ASR, choose an 8–12 second
speech-free stretch containing the natural location sound (bees, hive hum,
wind or room tone), and set it as the donor. Loop it with equal-power
crossfades, normalize gently, and fade it before the end card. Never use a
donor section that contains a voice just because it is loud or atmospheric.

## The look

### Default house style

Use this as the default branded treatment unless the client supplies a
different reference:

- Render vertical 1080x1920 at the source frame rate.
- Open with a full-screen cream brand card using the supplied logo and a short
  all-caps topic title, built like the ending card rather than over footage.
- Place the supplied logo in a small rounded light pill at the top-right during
  footage, then end on the full logo plus website.
- Render every tip as one complete all-caps text block. Use one font family,
  one weight, one size and one spacing pattern for every tip. Do not split into
  headline/support layers and do not add a divider, underline, emoji or tick
  mark unless the client explicitly asks for it.
- Keep the text centered in the lower-middle, above the social-control zone,
  over a dark gradient scrim and restrained halo. Keep faces, hands, bees,
  entrances, smokers, boxes and labels unobstructed.
- If an em dash makes the all-caps block look awkward, replace the dash with a
  clean sentence break while preserving every word.

Text sits **directly on the footage — no box**. Legibility comes from two cheap
things stacked: a gradient scrim darkening the lower third, and a blurred dark
halo behind the glyphs. Both are in `build_assets.py`.

This matters more than it sounds. A solid or frosted panel is the obvious way to
make text readable, and it is what everyone reaches for first — but it covers
whatever you are selling. The scrim-plus-halo combination survives bright sky
and dark subjects while leaving the product visible.

Each card carries one complete all-caps text block:

```
BOLD UPPERCASE HEADLINE          the instruction, 2-5 words
    ▬▬▬                          short accent rule in the brand colour
Complete all-caps text block.     the complete instruction, naturally wrapped
```

Centred, lower-middle of frame, **bottom-anchored** so the support line lands on
the same baseline whether the headline wraps to one line or two. Fixed size and
position across every card — text that shifts between cards reads as sloppy
even when viewers cannot say why. Use one headline size and one support size for
all instruction cards; keep the same font family, weight, line spacing and
headline/support gap on every card. Do not add a divider, underline or per-card
size adjustment. If the copy wraps, preserve the fixed sizes and use natural
line breaks rather than shrinking a single card.

For the default simple uniform card, do not split the copy into a headline and
support line at all. Render the complete sentence as one all-caps text block in
one font size and one weight, with natural wrapping only. The project config
uses `single_style_cards: true`, `uppercase_headlines: true`, and `card_size`
for this treatment.

Adapt all of it. If the client has a reference ad, study it and match its
structure — that is worth more than anything specified here. Different accent,
different placement, uppercase or not: fine. What should survive is *uniform
placement*, *uniform card typography*, and *contrast that does not depend on the
panel*.

For older-viewer deliverables, treat the reference subtitle size as a starting point, not a ceiling. The user's current preferred older-viewer subtitle size is 87px ASS (Arial regular), with a proportionally stronger outline and reduced side margins as needed. Increase the ASS font size uniformly, manually insert deliberate two-line breaks at natural phrase boundaries, and inspect rendered frames from long and short captions. Never solve clipping by silently shrinking only the problem caption; keep a uniform readable style and re-wrap the text instead. When the user asks to enlarge text after a render, regenerate the actual video immediately; updating a preference or memory alone is insufficient.

End-card typography must be treated as part of the same readability pass, not left at the old small size. Enlarge product/title text, pack size, supporting copy, CTA, and website together while preserving the logo, product image, card layout, and safe margins. For an existing card without a rebuild script, use the original rendered card as the base, cover old text with pixel-matched background sampled from the card (not an approximate color fill), redraw the larger text, and visually inspect the final card. Avoid rectangular masks that extend beyond rounded CTA buttons; mask only inside the button shape or redraw the button cleanly.

two-line captions plus the final end-card frame. Never solve clipping by
silently shrinking only the problem caption; keep a uniform readable style and
re-wrap the text instead. Preserve the previous deliverable as a clearly named
backup and promote the new render to the main filename only after visual checks
pass. If the user asks to keep an existing final screen unchanged, regenerate
subtitles from the untouched source footage, extract and append the existing
final-screen segment from the prior finished render, and verify the final frame;
do not burn new subtitles over an already-subtitled finished video.

See `references/subtitle-resizing-and-preserving-endcards.md` for the repeatable
resizing, manual-wrap, backup, and final-screen preservation workflow.

If a line forces the block taller than its neighbours, cut words. One
overlong caption dragging every other card out of alignment is a copy problem,
not a layout problem.

For BeeKeepingGear content specifically, when the subject is the pink women's
range or the user requests a pink-special treatment, use a pink end card rather
than the neutral cream default. Keep the logo intact, use a high-contrast dark
ink and a saturated pink CTA/accent, and enlarge the website, CTA, and support
copy together so the card is readable by the same older audience as the
footage captions.

## Choosing cuts

Match each shot to the line it carries. If the copy says "light your smoker
first", find the frames where that actually happens — literal matches land far
better than generic footage, and viewers notice the mismatch even when they are
not looking for it.

Confirm boundaries before rendering:

```bash
python scripts/contact_sheet.py "<clip>" --bounds 18.0,24.5 1.6,8.8 bounds.png
```

Check nothing lands mid-gesture or on a camera whip. 5–7 seconds per card is a
reasonable default — long enough to read at 1x, short enough to keep moving —
but let the footage argue.

Open on your strongest frames. Order cards to match the client's list unless
there is a reason not to; the sequence usually carries meaning.

## Grading

One uniform grade across every segment from a single shoot. Automatic
per-segment correction sounds better and is worse: neighbouring shots get
different gamma and you see a brightness step exactly at the cut. Reach for
per-clip correction only when sources genuinely differ.

`eq=contrast=1.03:gamma=1.03:saturation=1.04` is a safe lift for well-exposed
daylight. Look at a frame before and after rather than trusting the numbers.

## Audio

Two modes in `project.json`:

- **`keep`** — location audio as cut. Right when the sound belongs to the
  picture and contains nothing unwanted.
- **`ambience_loop`** — replace the whole bed with a clean donor stretch,
  looped. Right when there is talking to remove.

If there is speech to strip, replace the whole bed rather than patching windows.
Speech tails run longer than they look, so a donor picked just past the visible
end catches the last syllable, the client still hears it, and you go round
again. Verify a donor is clean by rendering a spectrogram and checking for
voiced harmonic combs — evenly spaced horizontal bands below ~3 kHz:

```bash
ffmpeg -v error -ss 39 -t 12 -i "<clip>" -lavfi "showspectrumpic=s=1800x420:legend=1:stop=3000" spec.png
```

A looped bed no longer syncs to picture, so knocks and footsteps disappear.
That is a real trade — say so rather than letting them find it.

**Do not normalise ambience to -14 LUFS.** That target assumes speech or music.
Quiet nature beds sit near -40 LUFS with enormous peak-to-loudness ratios, so
-14 means +25 dB of gain, a crushed dynamic range and a wall of wind noise.
-18 with a high-pass at 90 Hz is the better landing spot.

## Before you deliver

```bash
python scripts/selfeval.py project.json
```

Then **look at both sheets it writes**. It checks cut boundaries for audio pops
and visual jumps, samples every card at full opacity, and compares duration
against the project — a mismatch there usually means a stale segment cache
paired captions with the wrong shots.

Running the script is not the check. Reading its output is.

State honestly what you changed and what it cost. If you trimmed copy to fit,
or a looped bed lost the sync sound, say so — those are the client's calls to
reverse, and they can only reverse what they know about.

## When something behaves strangely

Read `references/troubleshooting.md`. It covers rotated footage, stale caches,
loudness targets, unremovable speech, Windows font and ffmpeg filter-path
issues, and grading flicker — each of which fails *silently*, producing a
successful render that is quietly wrong.

The common thread: when a render succeeds but looks or sounds off, suspect a
value that was reported plausibly and was wrong, not a crash you missed.

## Dependencies

- `ffmpeg` and `ffprobe` on PATH (any modern build)
- Python with `pillow` and `numpy`
- Fonts: set explicit paths in `project.json`. macOS-style paths fail silently
  on Windows, falling back to a bitmap font that looks broken but does not error.
