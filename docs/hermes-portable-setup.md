# Portable Hermes project setup

The repository contains project-local Hermes context that can be reused on another machine without copying private Hermes state.

Included:

- `AGENTS.md` — project instructions loaded when an agent works in this repository.
- `.hermes/project-memory.md` — safe, portable project facts and preferences.
- `.hermes/skills/automaton-command-center/SKILL.md` — the project skill.

Not included intentionally:

- API keys, `.env` files, OAuth tokens, `auth.json`, credentials, session transcripts, `state.db`, gateway logs, cron jobs, or unrelated global skills.

## Use after cloning

From the repository directory, run Hermes there. The project instructions and memory file are available from the folder:

```bash
hermes
```

Load the project skill explicitly when needed:

```bash
hermes -s automaton-command-center
```

If this Hermes installation does not automatically discover project-local skills, install the included skill into the active Hermes home:

```bash
mkdir -p "$HOME/.hermes/skills/automaton-command-center"
cp .hermes/skills/automaton-command-center/SKILL.md "$HOME/.hermes/skills/automaton-command-center/SKILL.md"
hermes skills list
```

On Windows Git Bash, the same commands work. In PowerShell, use:

```powershell
New-Item -ItemType Directory -Force "$HOME\.hermes\skills\automaton-command-center"
Copy-Item ".hermes\skills\automaton-command-center\SKILL.md" "$HOME\.hermes\skills\automaton-command-center\SKILL.md"
hermes skills list
```

For a new machine, configure credentials separately with `hermes setup` or `hermes auth`. Never put those credentials in this repository.
