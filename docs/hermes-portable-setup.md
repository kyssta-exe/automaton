# Hermes setup for Automaton Command Center

This guide is for a completely new machine with no Hermes setup yet.

## What this repository is

Automaton Command Center is a Vite + React + TypeScript browser application for managing a video-production workflow.

It is currently a frontend foundation. The screens and local browser behavior are real, but Google Drive, remote uploads, video processing, and job tracking are not live until a local bridge and provider credentials are configured.

The repository also includes portable Hermes project context:

- `AGENTS.md` — instructions for an agent working in this repository.
- `.hermes/project-memory.md` — safe project facts and preferences.
- `.hermes/skills/automaton-command-center/SKILL.md` — the reusable project skill.
- `docs/integration-contract.md` — the contract for future Drive, local-file, and video-job integrations.

## What Hermes is

Hermes Agent is the AI assistant that works from a terminal. It can read and edit the project, run commands, use skills, remember reusable project context, and help build the command center.

Hermes itself is separate from this React project:

- Hermes is the assistant and its local configuration.
- This repository is the application and its project documentation.
- The repository never needs to contain API keys, OAuth tokens, session databases, or Hermes gateway credentials.

## 1. Install Hermes

Use the official Hermes installation instructions for the operating system:

https://hermes-agent.nousresearch.com/docs/

After installation, confirm that the command works:

```bash
hermes --version
hermes doctor
```

On Windows, Hermes can be used from Windows Terminal, PowerShell, or Git Bash. If using Git Bash, use POSIX-style commands such as `mkdir`, `cp`, and `cd`.

## 2. Run the first-time setup

Start the setup wizard:

```bash
hermes setup
```

Configure at least:

1. An AI model/provider.
2. The terminal/workspace permissions Hermes should use.
3. Any toolsets needed for the work.

You can revisit setup later:

```bash
hermes setup
hermes model
hermes tools list
hermes config
```

For OAuth providers, use the Hermes credential manager instead of putting secrets in this repository:

```bash
hermes auth
hermes auth list
```

Keep API keys and OAuth credentials in Hermes' private configuration area. Never commit `.env`, `auth.json`, tokens, or provider keys.

## 3. Get the project

Clone the repository and enter it:

```bash
git clone https://github.com/kyssta-exe/automaton.git
cd automaton
```

Install the application dependencies:

```bash
npm install
```

Check the application:

```bash
npm run build
npm run lint
```

## 4. Install the project and video skills into Hermes

The repository includes the complete helper bundles for the three skills used in this workflow:

- `automaton-command-center` — dashboard and integration rules.
- `video-use` — editing, subtitles, rendering, and verification helpers.
- `branded-social-video` — OzArmour and BeeKeepingGear branded video production.

Copy the complete directories, not just `SKILL.md`, because `video-use` and `branded-social-video` use neighboring helper scripts and references:

```bash
mkdir -p "$HOME/.hermes/skills/automaton-command-center"
mkdir -p "$HOME/.hermes/skills/video-use"
mkdir -p "$HOME/.hermes/skills/branded-social-video"
cp -R .hermes/skills/automaton-command-center/. "$HOME/.hermes/skills/automaton-command-center/"
cp -R .hermes/skills/video-use/. "$HOME/.hermes/skills/video-use/"
cp -R .hermes/skills/branded-social-video/. "$HOME/.hermes/skills/branded-social-video/"
hermes skills list
```

### Video setup without ElevenLabs

ElevenLabs is intentionally not required for this project. Do not ask for an ElevenLabs key during setup and do not block video editing on it.

The bundled video setup is documented in `.hermes/skills/video-use/install.md`. Verify the local tools first:

```bash
ffmpeg -version
ffprobe -version
python .hermes/skills/video-use/helpers/timeline_view.py --help
python -m py_compile .hermes/skills/video-use/helpers/*.py
```

Install the core Python helpers when needed:

```bash
python -m pip install requests librosa matplotlib pillow numpy
```

For word-level subtitles without ElevenLabs, install the local fallback only when subtitle work is requested:

```bash
python -m pip install --user faster-whisper
```

If local ASR is unavailable, report that limitation instead of fabricating subtitles. Do not run a paid transcription test during setup.

Ask Hermes to rescan skills, or start a new session:

```bash
hermes skills list
hermes -s video-use -s branded-social-video -s automaton-command-center
```

If the skills do not appear immediately, start a new Hermes session or use `/reload-skills` inside the session.

### Windows PowerShell version

```powershell
New-Item -ItemType Directory -Force "$HOME\.hermes\skills\automaton-command-center"
New-Item -ItemType Directory -Force "$HOME\.hermes\skills\video-use"
New-Item -ItemType Directory -Force "$HOME\.hermes\skills\branded-social-video"
Copy-Item ".hermes\skills\automaton-command-center\*" "$HOME\.hermes\skills\automaton-command-center" -Recurse -Force
Copy-Item ".hermes\skills\video-use\*" "$HOME\.hermes\skills\video-use" -Recurse -Force
Copy-Item ".hermes\skills\branded-social-video\*" "$HOME\.hermes\skills\branded-social-video" -Recurse -Force
hermes skills list
```

## 5. Start Hermes in the project

Always start Hermes from the repository directory so it can see `AGENTS.md`, the project memory, source code, and integration contract:

```bash
cd path/to/automaton
hermes -s automaton-command-center
```

The first message can be:

```text
Read AGENTS.md, .hermes/project-memory.md, .hermes/skills/automaton-command-center/SKILL.md, README.md, and docs/integration-contract.md before working. Explain what is currently live, what is local-only, and what still needs a bridge or credentials. Do not change files yet.
```

This gives a new Hermes installation the project context without importing private session history.

## 6. How the portable memory works

`.hermes/project-memory.md` is a checked-in, project-specific memory file. It contains only durable facts that are useful to any Hermes installation working on this repository:

- what the application is;
- the older-user accessibility requirements;
- truthful integration boundaries;
- video and subtitle defaults;
- brand reference websites;
- source-file safety rules.

`AGENTS.md` tells the agent to read that file. This is intentionally different from copying the entire private Hermes home directory.

Do not copy these private files into GitHub:

- `~/.hermes/.env`
- `~/.hermes/auth.json`
- `~/.hermes/state.db`
- `~/.hermes/sessions/`
- `~/.hermes/logs/`
- `~/.hermes/cron/`
- unrelated personal skills or memory databases

If you want Hermes to remember a new project fact permanently, update `.hermes/project-memory.md` through a reviewed repository change rather than copying private databases between machines.

## 7. Run the application

Start the development server:

```bash
npm run dev
```

For a production-style local check:

```bash
npm run build
npm run preview -- --host 127.0.0.1 --port 4173
```

Open the URL Vite prints. The app should show the main actions, My videos, Videos in progress, Google Drive, Help, and Settings.

## 8. Important current limitations

The following are intentionally not claimed as live yet:

- Google Drive account connection and folder listing.
- Uploading video files to a remote service.
- Actual transcription and video rendering through the command center.
- Real-time processing lifecycle updates.
- Publishing or delivery automation.

The interface should clearly label these states. A saved local plan means it is saved in browser storage on that computer; it is not an uploaded project or processing job.

## 9. Safe development rules

- Keep original footage untouched.
- Put generated video artifacts in an `edit/` directory.
- Keep provider credentials out of React code and out of Git.
- Read `docs/integration-contract.md` before adding integrations.
- Do not call Google Drive or provider APIs directly from React components.
- Run `npm run build` and `npm run lint` before pushing changes.
- Test the production preview, not only the hot-reload development server.
- Do not say an integration is connected unless a real status check confirms it.
- Do not publish, delete, or finalize anything without user approval.

## Quick start summary

```bash
# Install and configure Hermes separately using the official docs
hermes setup
hermes doctor

# Get the application
git clone https://github.com/kyssta-exe/automaton.git
cd automaton
npm install

# Install this project's Hermes skill
mkdir -p "$HOME/.hermes/skills/automaton-command-center"
cp .hermes/skills/automaton-command-center/SKILL.md "$HOME/.hermes/skills/automaton-command-center/SKILL.md"

# Work with project context loaded
hermes -s automaton-command-center
```
