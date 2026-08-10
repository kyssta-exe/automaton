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
