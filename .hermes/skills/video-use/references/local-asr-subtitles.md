# Local ASR subtitle fallback and render verification

Use this fallback when the user explicitly defers ElevenLabs or no hosted word-level ASR is configured.

## Transcription

1. Install the local fallback in the active Python environment:

```bash
python -m pip install --user faster-whisper
```

2. Prefer `base.en` for short English social clips when quality matters; use `tiny.en` only for a quick first pass. Run CPU int8 with word timestamps and VAD filtering. Cache the resulting word-level JSON under `<videos_dir>/edit/`.
3. Treat obvious brand/product homophones as editorial review items, not automatic truth. For example, an ASR result of `jazz` may be `jars` when the footage and brand context support that correction. Preserve the spoken meaning; do not invent claims.
4. If the shell's `python` launcher is a broken trampoline on Windows, resolve and invoke a real Python executable directly (for example, `py -3` or the installed Python `python.exe`) rather than recording the launcher failure as a tool limitation. Confirm the interpreter with `py -3 --version` and test the ASR import before starting a long transcription.

## SRT construction

- Build captions from word timestamps, but keep each event to a short phrase or two short lines.
- Avoid large sentence-long blocks: long captions rise into faces and product demonstrations when bottom-aligned.
- Use natural pause boundaries and leave a small gap or exact handoff between events; do not create overlapping SRT events.
- Keep the subtitle filter last in the video filter chain.
- Use a high-contrast white bold font with black outline/shadow and a conservative bottom margin; adapt font size after looking at an actual rendered frame.

## Render and verify

For phone `.mov` files with extra/unsupported audio metadata streams, explicitly map the main video and first usable audio stream:

```bash
-map 0:v:0 -map 0:a:0
```

Render with ffmpeg to `<videos_dir>/edit/<name>_subtitled.mp4`, preserving the source's displayed orientation and using H.264/AAC for broad compatibility. Verify with `ffprobe` that the output has the expected vertical dimensions, duration, video stream, and audio stream.

Always extract at least one subtitle frame from the rendered output and inspect it visually. If a caption covers the speaker's face or is too tall, shorten the caption chunks and re-render before delivering. Keep the original source untouched.
