# Phone rotation, stream mapping, and brand-only end cards

## Why this matters

Phone `.mov` files may report coded dimensions that differ from the displayed orientation because rotation is stored in a display matrix. They may also contain an unsupported auxiliary audio stream (for example, APAC/spatial metadata) and several data streams. A successful encode can still be wrong if the wrong stream is selected or rotation is ignored.

## Reproducible workflow

1. Probe every stream and inspect `Display Matrix`/rotation metadata.
2. Explicitly map the video stream and the first usable AAC audio stream; do not rely on automatic stream selection.
3. Render to a normalized output (commonly 1080x1920 vertical for social) and verify dimensions after encoding.
4. Run local word-level ASR on the normalized/source clip, correcting only obvious recognition errors while retaining the spoken meaning.
5. Burn captions last using the established ASS style and inspect a mid-clip frame.
6. If a clip contains many products and no single product should be promoted, use a brand-only end card: supplied logo, brand identity, simple CTA, and website address; do not invent a product image or product-specific claim.
7. Append a 4–5 second card, extract the last frame, and inspect the final card as well as a subtitle frame.

## Known-good mapping pattern

```bash
ffmpeg -i input.mov \
  -map 0:<video-stream-index> -map 0:<first-usable-aac-index> \
  -vf "subtitles=normalized.ass" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 output.mp4
```

The exact stream indices must come from `ffprobe`; never copy these indices blindly between files.

## Verification checklist

- [ ] Original `.mov` was not modified.
- [ ] Output displays upright and has the intended social dimensions.
- [ ] Unsupported auxiliary audio/data streams are absent from the output.
- [ ] Captions are readable, lower-positioned, and not covering the principal subject.
- [ ] Brand-only card contains no unsupported product claim.
- [ ] Website spelling is exact: `beekeepinggear.com.au`.
- [ ] Final duration includes the complete end card.
- [ ] Mid-clip subtitle frame and final card frame were visually inspected.
