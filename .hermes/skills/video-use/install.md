# video-use local setup for Automaton Command Center

This is the first-time setup for the bundled `video-use` skill. It is intentionally configured for the current workflow: ElevenLabs is optional and must not block setup or normal video editing.

## What gets installed

- `video-use` with its helper scripts and verification tools.
- `branded-social-video` with brand routing, cards, end-card, audio, and render scripts.
- `ffmpeg` and `ffprobe` for inspection and rendering.
- Python dependencies for the helper scripts.
- Optional local ASR only when subtitles are needed.

Do not ask for, create, or require an ElevenLabs API key during this setup.

## Verify the bundled skills

From the Automaton repository:

```bash
python .hermes/skills/video-use/helpers/timeline_view.py --help
python -m py_compile .hermes/skills/video-use/helpers/*.py
python -m py_compile .hermes/skills/branded-social-video/scripts/*.py
ffmpeg -version
ffprobe -version
```

If `ffmpeg` or `ffprobe` is missing, install it using the operating system's package manager or the official FFmpeg build for that system. Do not claim video editing is ready until both commands work.

## Install Python dependencies

Use a project or user Python environment. The bundled `video-use/pyproject.toml` lists the core dependencies:

```bash
python -m pip install requests librosa matplotlib pillow numpy
```

For a lightweight Windows setup, install only the dependencies needed for the first task and add more if a helper reports one missing. Keep generated environments out of Git.

## Local subtitle fallback

When word-level subtitles are needed and ElevenLabs is not configured, use the local fallback:

```bash
python -m pip install --user faster-whisper
```

Prefer `base.en` for English social clips when quality matters; use `tiny.en` for a quick first pass. Cache transcripts under the footage folder's `edit/` directory. Do not transcribe during installation unless the user supplies footage and asks for a real test.

If local ASR is unavailable, say that subtitle generation needs a transcription dependency. Never fabricate captions.

## Register both skills with Hermes

Hermes needs the complete skill directories, not only the `SKILL.md` files, because the helper scripts and references sit beside them.

```bash
mkdir -p "$HOME/.hermes/skills/video-use"
mkdir -p "$HOME/.hermes/skills/branded-social-video"
cp -R .hermes/skills/video-use/. "$HOME/.hermes/skills/video-use/"
cp -R .hermes/skills/branded-social-video/. "$HOME/.hermes/skills/branded-social-video/"
hermes skills list
```

Start a new Hermes session or run `/reload-skills`, then load both skills for video work:

```bash
hermes -s video-use -s branded-social-video -s automaton-command-center
```

### Windows PowerShell

```powershell
New-Item -ItemType Directory -Force "$HOME\.hermes\skills\video-use"
New-Item -ItemType Directory -Force "$HOME\.hermes\skills\branded-social-video"
Copy-Item ".hermes\skills\video-use\*" "$HOME\.hermes\skills\video-use" -Recurse -Force
Copy-Item ".hermes\skills\branded-social-video\*" "$HOME\.hermes\skills\branded-social-video" -Recurse -Force
hermes skills list
```

## Daily video workflow

1. Start Hermes from the footage folder or the Automaton repository.
2. Read the source files and inspect actual frames before editing.
3. Keep source footage untouched.
4. Put all generated outputs in `<videos_dir>/edit/`.
5. For Drive footage, list and download a working copy; do not alter originals.
6. Route OzArmour and BeeKeepingGear footage, logos, claims, and end cards separately.
7. Re-check official brand sites before current product claims or offers.
8. Propose the editing strategy in plain English and confirm it before cutting.
9. Render subtitles last, with 1080x1920 output for vertical social videos by default.
10. Use the user's readable subtitle defaults: Arial regular, uppercase white, centered, maximum two lines; 52px baseline and 87px for older-viewer work.
11. Make end-card text large and inspect long captions and the final frame for clipping.
12. Self-evaluate the rendered video before delivery.

The authoritative detailed rules are in `video-use/SKILL.md` and `branded-social-video/SKILL.md`.
