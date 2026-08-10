---
name: automaton-command-center
description: Build and maintain the Automaton Command Center as a truthful, local-first, older-user-friendly video workflow dashboard.
version: 1.0.0
metadata:
  hermes:
    tags: [automaton, command-center, local-first, video, older-users, vite, react]
---

# Automaton Command Center

Use this skill when working in the Automaton Command Center repository.

## Product rule

Build a useful browser application first, with clear seams for a future local bridge. The renderer must not directly handle Google credentials, filesystem access, child processes, ffmpeg, transcription, uploads, or rendering. Keep those behind typed adapters or a preload-exposed bridge.

## Honesty rule

Google Drive, uploading, video processing, rendering, publishing, and remote job tracking are not live just because a screen exists. If an integration is unavailable, say so in simple language. Local browser state can be described as “saved on this computer,” never as uploaded, synced, or processing remotely.

## Older-user accessibility

- Make the home page answer “What would you like to do?”
- Put the most common actions in large, obvious cards.
- Use familiar words and one clear next step.
- Use large text, high contrast, generous spacing, large click targets, visible focus states, and clear feedback.
- Avoid technical words such as API, OAuth, bridge, pipeline, queue, renderer, and job runner in the user interface.
- Provide an easy local-file path when online storage is not connected.
- Never silently reject a file or user action; explain what happened and what to do next.
- Keep originals safe and require approval before publishing, deleting, or finalizing.

## Video workflow

The command center orchestrates the existing video workflow; it does not replace the editor. The workflow is:

1. Inspect source footage.
2. Cache word-level transcripts where available.
3. Propose and confirm an editing strategy.
4. Produce the EDL and assets.
5. Render with subtitles last.
6. Verify cuts, overlays, captions, orientation, and the final card visually.
7. Expose truthful progress and artifacts to the dashboard.

Generated work belongs in an `edit/` directory. Source files stay untouched.

## Branded defaults

The standing branded workflow can produce OzArmour and BeeKeepingGear outputs. Use the official websites as references and re-check current claims before publishing. Do not invent product claims, prices, offers, or specifications.

Default vertical social output is 1080x1920. Use ASS subtitles with Arial regular, uppercase white, centered, maximum two lines. Baseline size is 52px; for older-viewer deliverables use 87px with a stronger outline and deliberate natural wrapping. Make end-card text large enough to read and inspect rendered frames for clipping.

## Architecture

Prefer Vite + React + TypeScript. Keep `src/lib/automaton-bridge.ts` as the integration boundary. Read `docs/integration-contract.md` before adding provider or job integrations. Future expensive actions should return job IDs and explicit states such as `queued`, `transcribing`, `review`, `rendering`, `verifying`, `complete`, and `failed`.

## Verification

Before handoff:

- Run `npm run build`.
- Run `npm run lint`.
- Test the production preview, not only hot reload.
- Check desktop and narrow layouts for clipping and overflow.
- Test navigation, the primary action, file attachment, invalid-file feedback, local-plan persistence, Google Drive status, and the processing empty state.
- State clearly what is implemented, what is local-only, and what still needs a bridge or credentials.
