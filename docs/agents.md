# The studio for AI agents

People use the studio through commands and readable reports. From version 3.0 the studio and its agents can also be used by outside agents: any AI agent or system of agents, on any model or framework. They need something else: short messages, numbered findings they can act on, fixes they can send back unchanged, and safe ways for many of them to work on the same model. This guide covers the machine side of the studio.

- [The studio protocol](#the-studio-protocol)
- [The studio as an MCP server](#the-studio-as-an-mcp-server)
- [Many MCP servers through one gateway](#many-mcp-servers-through-one-gateway)
- [A shared workspace for many agents, with people in charge](#a-shared-workspace-for-many-agents-with-people-in-charge)
- [The Agent Economy Lab (AEL)](#the-agent-economy-lab-ael)
- [The improvement loop](#the-improvement-loop)
- [A swarm in one command](#a-swarm-in-one-command)
- [Putting it together](#putting-it-together)

## The studio protocol
`tools/studio_api.py` is one interface to the studio for programs and agents. A message is a JSON object with an operation and its arguments; a response says whether it worked, gives the result, the findings as numbered codes, a fingerprint of the state and, where the studio knows one, the operations that would fix each finding.

```
{"op": "lego.check", "a": {"m": "lego/examples/small-open-economy.lego.json"}, "id": 1}
{"id": 1, "ok": true, "r": {"pass": true, "n": {"joints": 17, "stubs": 7, ...}}, "h": "380d46b3cd16"}
```

**Learn it in one call.** `hello` returns the whole protocol: the meaning of every key, the rules, every operation with its arguments, every finding code and the limits. An agent reads it once and works from there.

```
python tools/studio_api.py hello
```

**Findings are codes.** A finding is a list: the code, the brick, then the subject and details. `[211, "fiscal-debt-rule", "output_gap", "Q", "A"]` means the fiscal brick sends `output_gap` across a frequency boundary from Q to A without a conversion method. Codes are stable; the messages for people are not. `python tools/studio_api.py codes` lists them:

| Range | Area | Examples |
|---|---|---|
| 1xx | the protocol | 100 bad message, 101 unknown operation, 104 for people only, 105 over a limit |
| 2xx | wiring errors | 206 baseplate count, 210 open stud, 211 bridge without a method, 218 change blocked, 219 state changed |
| 3xx | warnings | 301 no bridge, 303 method contradicts the port's measure, 304 bridge untested, 309 not square |
| 4xx | validation | 401 known answer failed, 402 untestable, 403 bridge not passed, 404 data refused |
| 5xx | the shared workspace | 501 paused, 502 frozen, 503 unread message from a person, 504 lease held |
| 6xx | the economy engine | 601 bad rule, 602 parameter out of bounds, 603 money not conserved, 604 known answer failed, 606 bad entity |
| 7xx | the improvement loop | 701 outside the study, 702 overfit, 703 budget spent, 704 study stopped |
| 900-999 | extensions | added with `api.code(...)` |

**Fixes come with the finding.** Where the studio knows the fix, the response carries it as an operation: send it back unchanged. For the bridge exercise, an agent that changes the fiscal brick to annual gets warning 301 and the fix `{"op": "lego.bridge", "a": {"b": "fiscal-debt-rule", "auto": true}}`, which declares a method for each crossing variable from its measure (a flow is summed, a stock takes the last value, a rate is averaged). The next response carries warning 304 (untested) and the fix `lego.bridge_test` with `apply`, after which `lego.check` with `strict` passes.

**Plans first, writes on request.** Every change is a plan unless `apply` is true. A model can live in a file (`m`, a path) or inline in the message (`d`, the model itself). With an inline model a plan returns the new model, so an agent can try many changes in memory, at no cost to anyone else, and write only the one it keeps.

**Safe writes.** Every response carries `h`, a fingerprint of the state. A write that sends `base` (the fingerprint it assumed) is refused with code 219 if someone else changed the model in the meantime; the agent reads it again and retries. Nothing is lost when many agents write.

**Batches.** A list of messages is answered by a list of responses in the same order, in one round trip.

**People stay in charge of judgment.** The economist's sign-off (`lego.approve`) is refused to agents with code 104. A person gives it with `python tools/lego.py approve`. Validation verdicts need a report as evidence, and validation is refused until the bridges have passed their known-answer tests.

**Back to plain language.** `say` turns any response, or a batch, into text a person can read, and `lego.text` gives the same report as the command line. `python tools/studio_api.py call '<message>' --say` does it from the command line.

### Operations

| Group | Operations |
|---|---|
| protocol | `hello`, `ops`, `explain`, `say` |
| lego | `lego.catalog`, `lego.ports`, `lego.get`, `lego.check`, `lego.text`, `lego.new`, `lego.attach`, `lego.detach`, `lego.swap`, `lego.patch`, `lego.bridge`, `lego.bridge_test`, `lego.validate`, `lego.approve` (people only) |
| bridges | `bridge.methods`, `bridge.convert` |
| known answers | `ka.list`, `ka.task` (inputs inline, never the answer), `ka.check` |
| the studio's agents and skills | `agents.list`, `agents.get` (a specialist's full instructions), `agents.brief` (those instructions plus your task, ready for your own model or subagent), `skills.list`, `skills.get` |

### Transports
The same messages travel in three ways:

| Transport | Use it for |
|---|---|
| `python tools/studio_api.py call '<message or batch>'` | one-off calls and scripts |
| `python tools/studio_api.py serve` | one process, JSON lines on standard input and output: the fastest way for a program to send many messages |
| `import studio_api; studio_api.handle(message)` | Python agents in the same process |

### Extensions
A Python file in `extensions/` (or in a folder listed in the `STUDIO_EXTENSIONS` environment variable) that defines `register(api)` adds operations, finding codes and places a model can live:

```python
def register(api):
    api.code(901, "too_many_lags", "a brick reads a variable with more than four lags")

    @api.op("mytools.lags", "list the lags each brick reads", {"m": "str manifest path (or d, or t)"})
    def lags(a, ctx):
        src = api.resolve(a)
        rows = [[b["id"], q["port"], q["lag"]] for b in api.lego.attached(src.doc) for q in api.lego.reqs(b)]
        return api.ok({"lags": rows}, h=src.h)
```

Extensions can also add checks that run before or after every operation (`api.hooks["before"]`, `api.hooks["after"]`). The protocol, the MCP server and the workspace pick up new operations without changes.

## The studio as an MCP server
`tools/mcp_server.py` offers the studio to any client of the Model Context Protocol (Claude Code, Claude Desktop, Cursor, Codex, Gemini CLI, VS Code and others). It uses only the standard library and the stdio transport.

- **Tools.** Every operation of the protocol is a tool: `lego.check` is `lego_check`, `hello` is `studio_hello`. Operations added by extensions appear without changes. The sign-off is not offered at all. Tools that change a model are marked as such and change it only with `apply: true`. Each result carries the protocol response as structured content, so an agent reads codes, fixes and fingerprints directly.
- **Prompts.** The 94 skills are prompts: `/lego-check`, `/validate-model` and the rest, with the full instructions.
- **Resources.** The protocol (`studio://protocol`), the port registry, the brick catalog, the example models, `AGENTS.md`, the guides, each skill (`studio://skills/<name>`) and each specialist agent (`studio://agents/<name>`).
- **Compact mode.** `--compact` offers a single tool, `studio_call`, that takes protocol messages and batches: one tool description instead of twenty, and many operations per call.
- **Fewer tools.** `--tools lego,ka` offers only some groups.

To see the tools: `python tools/mcp_server.py --list`.

### Connecting MCP clients
The server is plain MCP over standard input and output, so any MCP client can use it. The command is `python tools/mcp_server.py`, run from the repository folder.

| Client | Where it is set up |
|---|---|
| Claude Code | `.mcp.json` (included); approve the server the first time |
| Cursor | `.cursor/mcp.json` (included) |
| VS Code with GitHub Copilot (agent mode) | `.vscode/mcp.json` (included) |
| Gemini CLI | `.gemini/settings.json` (included) |
| Codex | `~/.codex/config.toml`: `[mcp_servers.economic-modeling-studio]` with `command = "python"`, `args = ["tools/mcp_server.py"]` and `cwd` set to the repository |
| Claude Desktop, Windsurf, others | the client's MCP settings, with the command above and the repository as the working folder |

Each agent can carry its own name into the shared workspace with `--agent NAME` or the `STUDIO_AGENT` environment variable.

## Many MCP servers through one gateway
An agent connected directly to 100 MCP servers would carry thousands of tool descriptions in its context and call the servers one at a time. `tools/mcp_gateway.py` stands in front of them as one MCP server:

- It starts every server in parallel and indexes their tools. A server that fails to start, or stops, is marked down and the others carry on; the next call to it tries to start it again.
- It offers the agent four tools instead of thousands: `gateway_servers` (which servers are up, with tool counts, calls and failures), `gateway_search` (find tools on every server by keyword, with their input schemas), `gateway_call` (call any tool by its full name, `server__tool`) and `gateway_batch` (many calls on many servers in parallel, answered in order).
- Each server can be limited to some tools (`allow`) or have some refused (`deny`), for example `"deny": ["delete_*"]`, with its own timeout.
- `--flat` offers every tool by its full name instead, which suits a handful of servers.

The servers are listed in `mcp/servers.json`, in the same form as `.mcp.json`:

```json
{"mcpServers": {
  "studio": {"command": "python", "args": ["tools/mcp_server.py"]},
  "statistics": {"command": "python", "args": ["../stats-server/server.py"], "allow": ["series_*"], "timeout": 60}
}}
```

`python tools/mcp_gateway.py --status` starts them all and prints their state. In a test on a laptop, 100 small servers and the studio started in about three seconds, and a batch of 102 calls across them came back in a few hundredths of a second. The tests in `tools/test_agents.py` start 30 servers, one of which cannot start, and check search, parallel calls, order, and refusal of denied tools.

## A shared workspace for many agents, with people in charge
`tools/workspace.py` is where many agents build models together. It is one SQLite file (standard library), safe for many processes at once, kept in `production/session-state/` (outside git) unless `STUDIO_WORKSPACE` or the `ws` argument names another.

**Tracks.** Agents work on tracks: named lines of work, each pointing at the current state of a model, a lego manifest, an economy or any JSON. `ws.track` starts one from a manifest, an inline model or another track (a fork). Wherever an operation expects a model, `t` names a track: `{"op": "lego.attach", "a": {"t": "main", "brick": "trade-sector-armington", "apply": true}}`.

**No write is lost.** Every state is stored once, by its fingerprint. Every write to a track is a compare-and-swap on the track's head: if another agent wrote first, the write is refused with code 219 and the agent reads the track again and retries. In a test, 100 agents writing to one track at once made 500 writes, every one of them counted, with 12 conflicts retried. `ws.put` writes any JSON state the same way, and `ws.promote` moves a track to another track's state, also only if it has not moved on.

**Coordination.** `ws.join` registers an agent and its role. `ws.lease` gives an agent a resource (a brick, a task) for some seconds, so a swarm can divide the work without colliding. `ws.post` lets agents leave notes, questions, proposals and progress for each other and for people.

**Everything is logged.** Every write and every refusal is an event: who, what, on which track, the finding codes, and the states before and after. `ws.log` reads them.

**People can look in at any time.** `ws.report` (or `python tools/workspace.py report <track>`) turns a track into plain language: its goal and state, the model's errors and warnings now, what people have set, what each agent did, oldest first, with refusals marked, and the questions waiting for a person.

**People steer, agents listen.**

| A person runs | Effect on agents |
|---|---|
| `python tools/workspace.py note "..."` | a note in every agent's inbox |
| `python tools/workspace.py constraint "no brick may remove the fiscal rule" --to track:main` | agents cannot write until they have read it (code 503), and it stays in every inbox reply |
| `python tools/workspace.py freeze main fiscal-debt-rule` | no agent can change that brick on that track (code 502) |
| `python tools/workspace.py pause main` / `resume main` | no writes on the track until it resumes (code 501); reading still works |
| `python tools/workspace.py veto main <event>` | the track goes back to its state before that event |
| `python tools/workspace.py answer <id> "..."` | answers an agent's question |
| `python tools/workspace.py status` | tracks, agents, operations, open questions |

Agents cannot post constraints, freezes, pauses, vetoes or answers (code 104), and they cannot sign off. Every response to an agent that has unread messages carries `inbox` with their number.

**Over MCP.** `python tools/mcp_server.py --agent builder-7` (or `STUDIO_AGENT`) gives each agent its name in the workspace; the `ws_*` tools are there with the others.

## The Agent Economy Lab (AEL)
`tools/economy.py` is a capability for building agent-based economies at the scale you choose, standard library only, for agents and people to build models on and test them at scale. It is not one fixed model: the number of households and firms, the parameters, the behaviour rules and the shocks are yours to set, and every example in this guide is one configuration of it.

**Who is in it.** Households, each with its own productivity, job or unemployment, reservation wage, income and deposits; firms that plan output from demand, hire and fire, set wages and prices, pay dividends and can default; a bank that lends to firms and the government; a government that taxes, pays unemployment benefits and buys goods under a debt rule; and a monetary authority that sets the policy rate. Each quarter: the policy rate and interest, hiring, production, wages, taxes and benefits, prices, the goods market, profits and defaults.

**A bookkeeping check, not a limit.** Every payment moves money from one account to another, and money can also be created or destroyed on purpose: an entity's `issue` formula does that, and the built-in `money_issuer` creates money and spends it on goods. Each run compares the sum of all accounts with the money that was there at the start plus what was created on purpose, every period, and reports the largest gap (about 1e-15, rounding only). A larger gap means money appeared or vanished without a recorded flow: a mistake in a rule or in the engine (code 603). `"money_check": false` turns the check off.

**Other entities.** Households, firms, the bank, the government and the monetary authority are in every economy. Any economy can add other entities under `"entities"`, as many of each kind as needed. Each kind is a set of parameters and three flow formulas, evaluated every quarter for each entity:

| Flow | What it does |
|---|---|
| `levy` | money the entity collects from households, in proportion to their deposits (never more than they hold) |
| `pay` | money it pays to households in equal parts: to all of them, the employed or the unemployed (`pay_to`) |
| `buy` | money it spends on goods, bought from firms' stocks after the government |
| `issue` | money it creates in its own account each period (negative: money it destroys) |

The formulas can use `gdp` (last quarter's nominal output), `cons` (household spending), `wages`, `dep` (household deposits), `bal` (the entity's own balance), `u`, `pi`, `r`, `t`, `share` (1/count) and `shock`, plus the economy's and the entity's parameters. Built-in kinds:

| Kind | Collects | Pays | Buys |
|---|---|---|---|
| `foreign` | imports, a share of household spending | nothing | exports, a share of output that varies each quarter |
| `pension_fund` | contributions, a share of the wage bill | part of its assets, to all households | nothing |
| `charity` | donations, a share of deposits | all it holds, to the unemployed | nothing |
| `money_issuer` | nothing (it creates new money, a share of output) | nothing | goods, with all it holds |
| `custom` | whatever its formulas say | whatever its formulas say | whatever its formulas say |

```json
"entities": [
  {"type": "foreign"},
  {"type": "pension_fund", "count": 3, "params": {"contrib": 0.06}},
  {"type": "custom", "name": "sovereign_fund", "params": {"rate": 0.01},
   "flows": {"levy": "rate * dep", "pay": "0.02 * max(0, bal)", "buy": "0"}, "pay_to": "all"}
]
```

A new kind needs no code: `custom` with a name, parameters and formulas. Extensions add kinds in code with `economy.entity_type(name, doc, params, flows, pay_to)`. Every flow moves money between accounts, so the accounting check covers entities. An entity's balance earns the deposit rate or, if negative, pays the loan rate to the bank. Formulas are checked against the same whitelist as the rules, and a bad entity is refused with code 606 before anything runs. `python tools/economy.py entities` lists the kinds; `python tools/economy.py run --entity foreign --entity pension_fund:3` adds them to a run; the result reports what each entity collected, paid and bought, and its balance.

**Every behaviour is a rule.** Each is a short formula that a person or an agent can replace in the configuration (`"rules": {"consume": "..."}`), without writing code:

| Rule | Decides |
|---|---|
| `consume` | how much a household spends |
| `plan` | the output a firm plans |
| `expect` | how a firm updates its expected sales |
| `price`, `wage` | a firm's price and wage offer |
| `dividend` | what a firm pays out |
| `default` | whether a firm defaults |
| `purchases` | what the government buys |
| `tax` | the tax rate |
| `benefit` | the unemployment benefit |
| `reservation` | how far an unemployed household lowers the wage it accepts |
| `policy` | the policy rate |

For example, the default spending rule is

    min(w + y, mpc_y * y + mpc_w * w * max(0, 1 - rate_sens * (r - pi - rstar)))

**New rules.** `"param_rules"` sets any parameter, or defines a new quantity, from the state of the economy at the start of every period. Every other formula can use the result, so a rule can switch when a condition is met:

```json
"param_rules": {"surcharge": "0.05 if debt > 0.9 else 0", "tau": "0.22 + surcharge"}
```

The state they see: `t`, `u`, `pi`, `r`, `gdp`, `debt`, `dep`, `gov`, `bank`, `wage`, `price`, `cons`. Each parameter rule's path is in the run's series.

**Checks.** `"checks"` states conditions that should hold every period, for example `{"unemployment below 15%": "u < 0.15"}`. Each run reports which held and when each first failed.

**Changes over time.** `"changes"` lists what changes from a given period: new parameter values, new rules, new parameter rules, entities that join (`add`) and entities that leave (`remove`). An entity that leaves pays what it holds to households, or the bank writes off what it owes, so money still adds up.

```json
"changes": [{"at": 80, "rules": {"policy": "max(0, 0.03 + 2 * (pi - pistar))"}, "params": {"g_share": 0.22}},
            {"at": 100, "add": [{"type": "foreign"}]}, {"at": 150, "remove": ["foreign"]}]
```

**Periods.** `"period"` is `quarter` (the default), `month` or `year`. Rates and inflation are annual in every case. The default parameters are set for quarters, so a monthly or yearly economy needs its own.

A formula may use only its listed variables, the parameters, numbers and `min`, `max`, `abs`, `exp`, `log`, `sqrt`; anything else is refused before it runs (code 601). Parameters have bounds (code 602). `python tools/economy.py rules` and `params` list them, and `economy.rules` gives agents the same, with the state variables.

**Known answers.** `python tools/economy.py known`: money conserved every period; an entity added by configuration collects exactly what its formula says, with money still conserved; a scheduled change and a parameter rule apply from exactly the period they name; the same seed gives the same economy and another seed another draw; with one type of household and no frictions, deposits settle at the level the spending rule implies, (1 - mpc_y) y / mpc_w; the policy rule at known points; and a formula that tries to call anything outside the list is refused.

**Scale.** A thousand households, 50 firms and 200 quarters take about three seconds on a laptop; 10,000 households and 1,000 firms about 17 seconds per hundred quarters. Larger economies (up to a million households) are allowed; time grows roughly in proportion to the number of households. Several seeds or scenarios run in parallel processes (`--seeds 8`, or `seeds` in `economy.run`). Shocks change a parameter from a given quarter (`"shocks": [{"param": "g_share", "value": 0.25, "at": 80}]`).

**For agents.** `economy.new`, `economy.params`, `economy.rules`, `economy.entities`, `economy.check`, `economy.run` and `economy.known`. An economy can live on a workspace track (`ws.track` with `kind: "economy"`), where many agents try changes on their own tracks and the report shows people the parameters and the last results.

**What it is not.** A stylized model for experiments, teaching and testing agents' work, not a calibrated model of any country. Its default parameters give a stable economy with low unemployment and moderate inflation; matching a country's facts is a calibration task (see the improvement loop).

## The improvement loop
`tools/evolve.py` lets many agents improve a model together, round after round, without fooling themselves. We call this recursive self-improvement modeling (RSIM): each round starts from the best model so far, and agents propose the next changes in light of what the previous rounds found.

**A study says what better means.** It names a workspace track (the model to improve), targets for the model's results with weights (for example unemployment 6% and inflation 2%), what candidates may change (parameters within ranges and, if allowed, behaviour rules), the training cases (seeds) agents can see, a budget of model runs, and how many variations the loop adds each round.

**Hidden cases.** When a study starts, the studio draws hidden seeds that no agent ever sees. A candidate that beats the champion on the training cases becomes the new champion only if it also holds up on the hidden cases (within the study's tolerance). One that does not is marked overfit (code 702). Agents see only whether a candidate held up, never its hidden score, so they cannot tune to the hidden cases by trial and error. People see the hidden scores in `evolve.status` and in the report.

**Each round.** Every waiting candidate is scored: those proposed by agents (`evolve.propose`, with a note on why) and the loop's own variations of the best so far. They run in parallel processes, are ranked, and a new champion is written to the study's track (a compare-and-swap, as for any agent). The loop runs with `evolve.step` from any agent, or from the command line:

```
python tools/evolve.py start calib --track eco --target unemployment=0.06 --target inflation=0.02 --free search=1:8 --free theta_w=0:0.1 --budget 400
python tools/evolve.py run calib --rounds 10
```

**People in charge.** A freeze on a parameter (`python tools/workspace.py freeze eco theta_w`) stops agents and the loop from changing it. A pause on the track stops the rounds (code 501). Constraints left in the inbox are read and reported by the loop before it promotes a champion. Only people stop or reopen a study (`python tools/evolve.py stop calib`). The track's report lists each study, its champion, how many candidates each agent proposed and how many were refused as overfit.

**Scores.** The distance to the targets is a weighted sum of squared relative gaps. A run in which money is not conserved, or a candidate that breaks a parameter bound or a rule, is rejected. Models other than the economy plug in with `evolve.objective("kind")`; a lego model can be scored on its errors and warnings.

In a test with 200 households, eight rounds of twelve candidates each cut the distance to the targets from 1.47 to 0.21 in about 25 seconds, and the hidden cases refused several candidates along the way.

## A swarm in one command
`tools/swarm.py` shows all of the above working together. It starts a workspace with an economy of 1,000 households, opens a study (unemployment 6%, inflation 2%, a wealth Gini of 0.35) and runs 100 built-in agents:

| Role | What it does |
|---|---|
| explorers | read the leaderboard and propose candidates: a nudge to one parameter, a blend of two good candidates, or a long jump, each with a reason |
| critics | read each new champion's results and leave a note on what is furthest from target; a lease makes sure only one critic writes about each champion |
| validators | rerun the champion at small scale and the engine's known-answer tests, and report |
| a runner | holds the loop's lease and runs its rounds: scoring in parallel, hidden cases, promotion |

The built-in agents use no AI service; they use the protocol exactly as any agent does. Language-model agents join the same workspace over MCP (`python tools/mcp_server.py --agent NAME`, with `STUDIO_WORKSPACE` pointing at the same file) or the protocol, as more names on the same tracks.

```
python tools/swarm.py --agents 100 --households 1000 --rounds 6 --person-at 3 "keep the tax rate as it is" --report swarm-report.md
```

With `--person-at`, a person steps in after the given round: they read the report, leave a constraint and freeze `theta_w`. From that moment every agent must read the message before it can propose again, and nothing changes `theta_w`. While the swarm runs, anyone can do the same from another terminal with `tools/workspace.py`.

In a test on a 16-core laptop, 100 agents exchanged about 28,000 protocol messages in 81 seconds (about 340 a second). Four rounds of 32 candidates on the 1,000-household economy each took about 15 seconds. The distance to the targets fell from 1.58 to 0.73, every champion held up on the hidden cases, and the person's constraint and freeze were obeyed from the round they were set.

## Putting it together
A typical setup for a team of agents:

1. A person starts a track from a model (`python tools/workspace.py track main models/.../model.lego.json --goal "..."`) or an economy, and if it is to be improved, a study with targets (`python tools/evolve.py start ...`).
2. Agents connect over MCP or the protocol, each with its own name, and read `hello` (or the `studio://protocol` resource). If they need data or other tools, the gateway gives them many MCP servers through one connection.
3. Agents work on their own forks of the track, propose to the study, divide work with leases and leave notes. Their writes never collide.
4. People look in whenever they like (`report`, `status`), answer questions, set constraints, freeze what must not change and pause or undo when needed.
5. The model's numbers are validated independently, and the economist's sign-off (`python tools/lego.py approve`) is given by a person, never by an agent.
