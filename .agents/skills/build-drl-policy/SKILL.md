---
name: build-drl-policy
description: "Builds a deep reinforcement learning policy environment and agent for monetary, fiscal or macroprudential policy."
---
<!-- Generated from .claude/skills/build-drl-policy/SKILL.md by tools/sync_agents.py. Edit the source, then run the script. -->

# /build-drl-policy — Build DRL Policy

**Category:** Build (AI) · **Primary agent:** `deep-reinforcement-learning-specialist`

Builds a deep reinforcement learning policy environment and agent for monetary, fiscal or macroprudential policy.

Arguments: whatever the user wrote after the command name.

## Purpose
Build a deep reinforcement learning environment and agent that learns a monetary, fiscal or macroprudential policy inside a validated structural simulator, and test whether the learned policy is better than simple rules, robust outside its training conditions, and explainable. The output is a policy evaluation, not a recommendation, until all comparisons and robustness tests pass.

**Use it when** the policy problem is nonlinear or high-dimensional enough that classical optimal-policy methods are impractical, or robustness across models and regimes is the focus.

**Do not use it when** a linear-quadratic optimal policy or optimized simple rule can be computed directly (`/policy-simulation`), or the simulator itself is not yet validated (`/validate-model`).

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

Each agent is defined in `.claude/agents/<name>.md`. If your tool runs subagents, run these agents as subagents, in parallel where the steps are independent; otherwise read each agent's file and apply its instructions in turn. Subagents only write to the paths named in your instructions.

## Key design decisions (present options, let the user choose)
| Decision | Typical options | What it changes |
|---|---|---|
| Simulator | semi-structural, DSGE, agent-based | Realism and speed |
| Observation | observable data only, latent states | Real-world implementability |
| Reward | welfare, quadratic loss with mandate weights | What the policy optimizes |
| Algorithm | PPO, SAC, TD3, model-based | Stability and sample efficiency |
| Robustness design | domain randomization, adversarial shocks, model ensembles | Out-of-distribution performance |

## Workflow
1. Agree the welfare-based reward with the economic-reasoning-specialist and write the environment spec
   - States, actions with bounds, reward, discounting, episode design
2. Verify the environment: known-optimal cases and unit tests for state transitions
   - Reproduce known optimal policies in a linear-quadratic special case
3. Train agents (PPO/SAC/TD3) with multiple seeds; log learning curves
4. Compare the learned policy with Taylor-type and optimal-policy benchmarks
   - Same shock sequences for all policies; welfare differences with uncertainty
5. Stress-test out-of-distribution: other shocks, parameters, misspecified models
   - Explain the learned policy with policy-function plots or a surrogate rule
6. Register the model as a lego set (`/lego-map`): a baseplate plus bricks with declared studs (variables, units, timing) and stubs, so components can later be attached, detached or swapped

## Checkpoints with the user
- After the reward: confirm it matches the mandate
- After environment verification: confirm the simulator is fit for purpose
- After benchmarks: decide whether robustness testing is warranted

## Common pitfalls
- Reward that differs from welfare
- Policies that exploit simulator artifacts
- Best-seed reporting
- Recommending policies without simple-rule comparison

## Output
`models/ai/<name>-drl/ and docs/models/<name>/experiment-log.md (+ model.lego.json)`

The model folder holds the environment, agent code, training logs across seeds, benchmark comparisons and robustness results; the experiment log records every run; the lego manifest registers the policy brick.

## Gate / verdict
- Reward is welfare-based and approved
- Simple-rule benchmark compared
- Out-of-distribution test passed or limits documented
- Lego manifest passes `python tools/lego.py check`
- Results are reported across seeds
- The learned policy is explained with a policy-function plot or surrogate rule

## Suggested next steps
- `/ai-audit`
- `/validate-model`
- `/lego-map`
