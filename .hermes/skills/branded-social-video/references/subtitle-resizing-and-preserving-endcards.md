# Subtitle resizing and final-screen preservation

Use this procedure when revising an existing branded vertical video at the user's request.

## Resizing

1. Read the active ASS style instead of assuming the current size. Calculate the requested relative change from that value and use one uniform size for all captions. For example, 66 px + 20% = approximately 79 px; 79 px + 10% = approximately 87 px.
2. Increase outline weight proportionally with the font size, and reduce side margins only as needed to preserve a safe usable width.
3. Treat every long caption as a candidate for manual wrapping. At larger sizes, a line that fit previously can clip horizontally even when ffmpeg/libass reports a successful render.
4. Keep no more than two lines per caption. Split at natural phrase boundaries; do not silently shrink only the problematic caption.
5. Render representative long lines and inspect actual frames. If clipping appears, revise the ASS `\\N` breaks and render again before delivery.

## Preserving an existing final screen

When the user asks to change subtitles but keep the final screen as-is:

1. Determine the footage/subtitle section boundary from the existing finished video's timeline and duration.
2. Regenerate subtitles from the untouched source footage only; never burn new subtitles over the already-finished video, which would duplicate the old captions.
3. Extract the existing final-screen segment from the prior finished video and append it after the newly subtitled footage. Preserve its visual content, duration, branding, product art, CTA, and website.
4. Inspect both a long subtitle frame and the last frame of the combined output.
5. Preserve the prior final file as a backup before replacing the main deliverable, and verify final dimensions, frame rate, duration, and audio/video streams with ffprobe.

## Reusable Windows edit-directory pattern

Keep all generated assets in `<source_dir>/edit/`, leaving the source `.mov` untouched. Use distinct names for the ASS file, subtitled intermediate, extracted final screen, concat list, verification frames, and revised final. A practical naming pattern is:

- `IMG_####_reference_style_<size>px.ass`
- `IMG_####_subtitled_<size>px.mp4`
- `IMG_####_finalscreen_unchanged.mp4`
- `IMG_####_concat_<size>px.txt`
- `IMG_####_final_<size>px.mp4`

The important verification is visual: successful encoding does not prove that enlarged captions fit the 1080×1920 frame.