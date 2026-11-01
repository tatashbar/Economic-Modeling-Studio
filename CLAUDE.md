# Economic Modeling Studio — Claude Code

The project instructions are shared by all coding agents and live in AGENTS.md:

@AGENTS.md

## Claude Code specifics
- This session has **119 specialized agents** (`.claude/agents/`) and **85 slash commands** (`.claude/skills/`). Run agents as subagents with the Task tool, in parallel where steps are independent.
- Start here: `/start` or `/help`. Roster: @docs/agent-roster.md · Commands: @docs/skill-catalog.md
- How agents work together: @.claude/docs/coordination-rules.md · Collaboration protocol: @.claude/docs/collaboration-protocol.md
- Hooks in `.claude/settings.json` print the session context at start, block destructive commands, guard restricted data, secrets and raw data, check required document sections, and keep an agent audit log.
- After editing `.claude/skills/` or `.claude/rules/`, run `python tools/sync_agents.py` so the copies for other agents stay in sync.
