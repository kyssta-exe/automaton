# Automaton Command Center — Hermes project context

This repository is the Automaton Command Center project. Before changing it, read:

- `.hermes/project-memory.md` for portable project facts and user preferences.
- `.hermes/skills/automaton-command-center/SKILL.md` for the project workflow and quality rules.
- `docs/integration-contract.md` before implementing Google Drive, local-file, or video-job integrations.

Use the project directory as the working directory. Keep the browser renderer honest: Google Drive, uploads, processing, and publishing are not live unless an actual bridge/provider is configured and verified.

For older or non-technical users, keep the interface direct and reassuring: large controls, plain wording, one obvious next step, high contrast, and clear feedback. Do not expose technical terms when ordinary language works.

Preserve original source files. Generated video work belongs in an `edit/` directory. Never commit credentials, OAuth tokens, API keys, session databases, or personal Hermes state.
