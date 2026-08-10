# Hermes local installation notes

For a local Windows source bundle, install the complete skill bundle under the active Hermes profile so `SKILL.md` stays alongside `helpers/`, `install.md`, and any vendored skills.

Recommended layout:

```text
%USERPROFILE%/.hermes/skills/video-use/
├── SKILL.md
├── helpers/
├── install.md
└── skills/
```

Copy the source bundle while excluding repository metadata and heavyweight development environments (`.git/`, `.venv/`, and generated `*.egg-info/`). Do not install only `SKILL.md`; the helper scripts are part of the skill contract.

Verify the installation with:

```bash
hermes skills list
python <skill-root>/helpers/timeline_view.py --help
python -m py_compile <skill-root>/helpers/*.py
```

`ffmpeg` and `ffprobe` are required for actual editing and inspection. ElevenLabs is optional until the user requests hosted transcription; do not start OAuth/API-key setup as part of a skill-only installation. If transcription is needed later, configure the chosen provider at that time.
