# Collaboration Protocol

Applies to every agent and skill. The user makes the decisions; the studio provides expertise, structure and challenge.

## Question-first workflow
1. **Ask clarifying questions** — the decision to inform, audience, horizon, country, data availability, constraints, deadline, acceptable uncertainty.
2. **Present 2-4 options** with trade-offs (transparency, data needs, build and validation effort, run time, communicability). Always include a simple benchmark. Give a recommendation, and defer the decision to the user.
3. **Draft incrementally** — create a skeleton first, then one section at a time. Update `production/session-state/active.md` after each approved section.
4. **Get approval before writing** — show the draft, ask "May I write this to `<path>`?". No `Write`/`Edit` until the user says yes.
   - *Orchestrated-run exception:* a skill that names the destination path for a new artifact under `production/`, `docs/`, `forecasts/`, `validation/` or `models/<name>/` may have its subagents write there without a separate prompt. Never for edits to existing models, data or config.

## Structured decisions
Write the full analysis first, then end with a short options list: a 1-5 word label per option, one sentence each, "(Recommended)" on your pick, at most four independent questions.

## Insufficient-input rule
If an input needed for a section does not exist, the answer is **`NOT ASSESSED — NO DATA`** for that section, naming what is missing and which skill produces it. Never estimate a missing input, infer it from an adjacent artifact, or leave a placeholder number. A "could not run" outcome is a correct outcome.

## Honesty rules
- Never fabricate data, parameter values, citations, results or test outcomes.
- Mark every assumption as an assumption and every judgment as judgment.
- Report negative and inconclusive results as plainly as positive ones.
- State limitations that change the conclusion in the main text.

## Delegation
- Skills (`/team-*`, `/build-*`, ...) are run by the main session, which launches the named agents as subagents, in parallel when steps are independent. Subagents cannot launch further subagents.
- An agent invoked directly acts as an adviser within its own context; it names which other specialists should be involved and the main session launches them.
- Subagents write only to paths named in their instructions and report back; the main session integrates and presents to the user.
- Never delegate validation of a model to anyone who built it.

## Session state
`production/session-state/active.md` holds: current task, completed sections, key decisions, open questions, next step. Read it on resume.
