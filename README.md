# Automaton Command Center

Local-first Vite + React foundation for Ammar's video production command center.

## Current foundation

- Dashboard overview for active projects, production state, attention queue, activity, and Google Drive connection state.
- Built-in interactions for project navigation, search, command-log handoff, notifications, and local connection feedback.
- UI language is intentionally restrained: dark graphite surfaces, Space Grotesk display type, DM Sans utility type, no invented stock imagery or fake analytics.
- Integration boundary documented in `docs/integration-contract.md` so the UI can later be connected to a local Electron/Node bridge without coupling the renderer to filesystem or OAuth credentials.

## Run

```bash
npm install
npm run dev
```

Then open the URL printed by Vite.

## Portable Hermes setup

Hermes Agent is the terminal AI assistant used to work on this project. Hermes is separate from the React application: the app is stored here, while Hermes has its own private configuration, provider credentials, sessions, and global skills.

This repository includes safe, project-local Hermes context:

- `AGENTS.md` — instructions Hermes should follow in this project.
- `.hermes/project-memory.md` — portable project facts and user preferences.
- `.hermes/skills/automaton-command-center/SKILL.md` — the reusable project skill.
- `docs/integration-contract.md` — future Drive, local-file, and video-job boundaries.
- `docs/hermes-portable-setup.md` — complete setup instructions for a brand-new Hermes installation.

The repository intentionally does not include API keys, OAuth tokens, `.env` files, Hermes session history, `state.db`, `auth.json`, gateway logs, or private memory databases.

### Quick setup on a new machine

Install and configure Hermes using the official instructions, then clone this project:

```bash
hermes setup
hermes doctor

git clone https://github.com/kyssta-exe/automaton.git
cd automaton
npm install
```

Install this project's skill into the active Hermes profile:

```bash
mkdir -p "$HOME/.hermes/skills/automaton-command-center"
cp .hermes/skills/automaton-command-center/SKILL.md "$HOME/.hermes/skills/automaton-command-center/SKILL.md"
hermes skills list
hermes -s automaton-command-center
```

Start Hermes from the repository directory so it can read `AGENTS.md` and `.hermes/project-memory.md`. For Windows PowerShell commands and the full explanation, read `docs/hermes-portable-setup.md`.

## Build verification

```bash
npm run build
```

## Direction

The next production slices should be implemented behind the bridge contract:

1. Google Drive OAuth + folder inventory adapter.
2. Local footage indexer with ffprobe metadata and thumbnail generation.
3. Video-use job runner that launches the existing local workflow and reports explicit states.
4. Project detail view with transcript, EDL, subtitle review, render history, and delivery actions.
5. Electron shell only after the browser version has a stable bridge API.
