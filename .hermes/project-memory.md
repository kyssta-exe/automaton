# Portable project memory

This file is intentionally limited to project context. It is safe to keep in the repository. It is not a copy of Hermes session history, credentials, OAuth tokens, or the user's private global memory database.

## Project

- Project name: Automaton Command Center.
- Stack: Vite + React + TypeScript.
- Purpose: a calm, local-first command center for video production workflows.
- Renderer/provider boundary: React presents state and actions; filesystem, OAuth, ffmpeg, transcription, rendering, uploads, and job providers belong behind a future local bridge.
- Current browser app is a frontend foundation. Google Drive and real video processing must not be presented as live until configured and verified.
- Original files must remain untouched. Generated artifacts should go under the source footage folder's `edit/` directory when practical.

## User experience

- The main audience includes older adults and people who know little about computers.
- The interface should be straight to the point, easy to navigate, calm, forgiving, and reassuring.
- Prefer plain labels such as “Make a new video,” “My videos,” “Videos in progress,” “Google Drive,” and “Help.”
- Use large readable text, high contrast, generous spacing, large click targets, visible focus states, and clear error messages.
- The home screen should answer: “What would you like to do?”
- Do not make users understand APIs, OAuth, bridges, pipelines, queues, renderers, or job runners.
- Never claim that a file was uploaded, synced, processed, published, deleted, or finished unless the real service confirms it.
- Nothing should be published, deleted, or finalized without user approval.

## Video defaults

- Default social format: 1080x1920 vertical.
- Subtitle baseline: ASS, Arial regular, uppercase white, centered, maximum two lines, 52px by default.
- For older-viewer branded videos: 87px subtitles with stronger outline and deliberate natural wrapping. Make end-card logo support text, product/title text, CTA, website, and descriptive copy substantially larger too.
- Product cards remain 1080x1920 and usually last about 4–5 seconds.
- Always inspect rendered frames and verify that no text is clipped.

## Brands

- OzArmour: https://ozarmour.co/
- BeeKeepingGear: https://www.beekeepinggear.com.au/
- Re-check live brand sites before relying on current product details, offers, prices, or claims.
- Brand assets are normally stored under the user's Hermes assets directory; do not commit private asset folders or credentials to this repository.

## Current integration boundary

- Google Drive page: show truthful connected/not-connected state and a local-file fallback.
- Videos in progress page: show real lifecycle states only when jobs are connected; otherwise use an honest empty state.
- Saved local plans may be stored as browser metadata, but they are not remote projects or processing jobs.
- Future job states may include: queued, transcribing, review, rendering, verifying, complete, and failed.
