# Contributing

Contributions are welcome: new agents, commands, rules, templates, lego bricks and fixes.

## Before you open a pull request
1. Run the integrity check and the tests (Python 3.9+, standard library only):
   ```
   python tools/validate_studio.py
   python tools/test_studio.py
   ```
2. If you changed a lego example manifest, regenerate its picture:
   `python tools/lego.py show lego/examples/<name>.lego.json --html lego/examples/<name>.html`
3. Keep the counts in `README.md`, `CLAUDE.md` and `docs/` in line with what you added.

## Adding things
- **Agent:** `.claude/agents/<name>.md`, and list it as a peer in the related agents. See `docs/agent-roster.md`.
- **Command:** `.claude/skills/<name>/SKILL.md`. See `docs/skill-catalog.md`.
- **Lego brick:** `lego/catalog/<id>.json`, using ports from `lego/ports.json`. See `docs/lego.md`.

## Ground rules
- Public or synthetic data only. Never commit restricted, confidential or personal data, or credentials.
- No invented numbers, parameters or citations in agents, templates or examples.
- Agents advise; the user decides. Keep that wording in new agents and commands.
