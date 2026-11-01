---
name: build-drl-policy
description: "Builds a deep reinforcement learning policy environment and agent for monetary, fiscal or macroprudential policy."
argument-hint: "[policy problem]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, Task
---

# /build-drl-policy — Build DRL Policy

**Category:** Build (AI) · **Primary agent:** `deep-reinforcement-learning-specialist`

Builds a deep reinforcement learning policy environment and agent for monetary, fiscal or macroprudential policy.

Arguments: `$ARGUMENTS`

## Before you start
1. **Check required inputs.** For each input below record `FOUND` or `ABSENT` (never 'assumed'):
   - Structural simulator or approved environment spec
   - Welfare criterion
   If a required input is `ABSENT`, that part is **`NOT ASSESSED — NO DATA`**: do not estimate or invent it; name what is missing and which skill produces it. If all required inputs are absent, stop and say so.
2. **Check confidentiality.** Identify the data classification level of the inputs (`.claude/docs/confidentiality-and-ai-use.md`). Do not proceed with restricted or confidential data in a way the policy does not allow.
3. **Collaboration.** Follow `.claude/docs/collaboration-protocol.md`: ask questions first, present options, get approval before writing files, and update `production/session-state/active.md` after each approved section.

## Agents
- `deep-reinforcement-learning-specialist` — primary agent; coordinates the work and integrates results
- `monetary-policy-rules-specialist` — Designs and evaluates monetary policy rules
- `multi-agent-rl-specialist` — Builds multi-agent reinforcement learning systems for strategic economic interaction
- `differentiable-programming-specialist` — Builds differentiable economic models in JAX/PyTorch/Julia

Run these agents as subagents (the `Task` tool), in parallel where the steps are independent. Subagents only write to the paths named in your instructions.

## Workflow
1. Agree the welfare-based reward with the economic-reasoning-specialist and write the environment spec
2. Verify the environment: known-optimal cases and unit tests for state transitions
3. Train agents (PPO/SAC/TD3) with multiple seeds; log learning curves
4. Compare the learned policy with Taylor-type and optimal-policy benchmarks
5. Stress-test out-of-distribution: other shocks, parameters, misspecified models
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Output
`models/ai/<name>-drl/ and docs/models/<name>/experiment-log.md (+ model.lego.json)`

## Gate / verdict
- Reward is welfare-based and approved
- Simple-rule benchmark compared
- Out-of-distribution test passed or limits documented
- Lego manifest passes `python tools/lego.py check`

## Suggested next steps
- `/ai-audit`
- `/validate-model`
- `/lego-map`
