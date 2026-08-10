# Traps, and how to get out of them

Each of these cost real debugging time. They share a shape: something reports a
plausible value that is quietly wrong, and the render succeeds anyway.

## Contents

- [Rotated footage reports the wrong size](#rotated-footage-reports-the-wrong-size)
- [Stale segment caches pair captions with the wrong shot](#stale-segment-caches)
- [Loudness targets built for speech ruin ambience](#loudness-targets)
- [Speech you cannot fully patch out](#speech-you-cannot-patch-out)
- [Windows: ffmpeg filter paths with drive letters](#windows-ffmpeg-filter-paths)
- [Windows: fonts and npx](#windows-fonts-and-npx)
- [Per-segment auto-grading causes flicker](#per-segment-auto-grading)

---

## Rotated footage reports the wrong size

`ffprobe -show_entries stream=width,height` reports **coded** dimensions. Phone
and action-cam clips routinely carry a `rotation=-90` display matrix, so a file
reporting `3840x2160` actually displays as `2160x3840` — vertical.

ffmpeg auto-rotates on decode, so the filter graph sees the rotated frame. That
means the render *works*, it just produces something the wrong shape. Code that
reads stream width/height to decide "is this portrait?" concludes the opposite
of the truth and emits e.g. `scale=1920:-2` on a portrait source, giving a
1920x3413 file.

**Detect:** `scripts/probe.py` reports coded size, display size and rotation
side by side. Run it before deciding output dimensions.

**Fix:** scale by width and let height follow (`scale=<W>:-2`) after
auto-rotation. Never branch on coded dimensions.

**Smell:** an early contact sheet whose tiles are a different aspect than you
expected. Trust the tiles over the probe.

---

## Stale segment caches

Caching extracted segments makes revisions fast. Keying that cache by index
(`seg_00.mp4`) is a trap: insert a title card at position 0 and every index
shifts by one, so the cache serves each slot's previous occupant. Every caption
ends up over the wrong shot and **the render still succeeds**.

**Detect:** total duration drifts from the sum of the ranges. `selfeval.py`
checks this explicitly.

**Fix:** key on content — `seg_<source>_<start>-<end>.mp4`. Reordering then
still reuses correctly, and a changed range can never collide.

The same reasoning applies to any derived constant. Sum the ranges to find where
the footage ends rather than hardcoding it, or the audio tail-fade desyncs the
first time the edit changes length.

---

## Loudness targets

-14 LUFS is the streaming/social norm **for speech and music**. Quiet location
ambience is a different animal: wind-and-wildlife beds often measure near
-40 LUFS with a peak-to-loudness ratio above 30 dB, because wind buffets and
handling knocks sit far above the average level.

Normalising that to -14 needs ~+25 dB. The limiter then flattens everything:
dynamic range collapses (LRA 9.7 -> 4.0 in one real case) and the noise floor
rises into a constant roar.

**Target -18 LUFS with a ~90 Hz high-pass** for ambience beds. Watch the
reported LRA — under about 4 LU means you are over-compressing. If the source
is a clean loop with no transients, its true peak sits low and loudnorm can
reach target almost linearly, which sounds much better.

---

## Speech you cannot patch out

If location audio contains talking and the brief says no voice, the tempting fix
is to replace just the speech windows with nearby "clean" ambience. This tends to
fail: speech tails are longer than they look on a spectrogram, and a donor picked
just past the visible end still catches the last syllable. You patch, the client
still hears it, and you repeat.

**Replace the whole bed** with a loop of one verified-clean donor. Speech is then
gone by construction rather than by inspection.

**Verify a donor before trusting it** — render `showspectrumpic` over it and look
for voiced harmonic combs (evenly spaced horizontal bands, typically strongest
below ~3 kHz). Uniform broadband texture with no combs is clean.

```bash
ffmpeg -v error -ss 39 -t 12 -i src.mp4 -lavfi "showspectrumpic=s=1800x420:legend=1:stop=3000" spec.png
```

**Cost, and say it out loud:** a looped bed no longer syncs to picture, so lid
clunks and footsteps vanish. That is a real trade, and the client should hear it
from you rather than notice it themselves.

---

## Windows: ffmpeg filter paths

ffmpeg parses `:` as an option separator *inside filter arguments*. Any absolute
Windows path interpolated into a filter therefore breaks on the drive letter:

```
metadata=print:file=C:\Users\...\stats.txt      # C: is parsed as an option
```

**Fix:** run with `cwd` set to the target directory and pass a bare relative
filename. Escaping (`C\:/Users/...`) also works but is fragile across ffmpeg
versions and shells.

This bites any helper that writes filter output to a temp file — `signalstats`
metadata dumps are the common case.

---

## Windows: fonts and npx

**Fonts.** Tools written on macOS often hardcode `/System/Library/Fonts/...`,
falling back to a tiny bitmap font on Windows without erroring. Likewise
`FontName=Helvetica` in an ASS/libass `force_style` silently substitutes
something arbitrary. Set explicit font paths (`C:/Windows/Fonts/segoeuib.ttf`)
and check the rendered output rather than the exit code.

Rounded geometric faces (Poppins, Nunito) are not installed by default. Segoe UI
Bold/Semibold is the closest clean stand-in. Install the real face if brand
match matters.

**npx.** Three separate failures show up when a documented `npx <tool>` command
does not work:

1. The package has no binary — the CLI lives in a different package.
2. The package exposes several bins, so npx cannot choose. Use
   `npx --package=@scope/pkg <binname>`.
3. `spawn EINVAL` — Node on Windows refuses to launch a `.cmd` shim without
   `shell: true`. That is a bug in the tool, not your setup.

When all three block you, clone the tool's repo and wire it up manually.

---

## Per-segment auto-grading

Automatic per-clip grading analyses each segment and corrects it independently.
When every shot comes from one camera under one light, that *introduces*
inconsistency instead of removing it — neighbouring segments can get gamma 1.045
and none, a ~4.5% brightness step visible exactly at the cut.

**Apply one uniform grade** across all segments from a single shoot. Reach for
per-segment correction only when the sources genuinely differ (different
cameras, or light that changed during the day).
