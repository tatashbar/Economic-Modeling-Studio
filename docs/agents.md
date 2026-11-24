# The studio for AI agents

People use the studio through commands and readable reports. AI agents need something else: short messages, numbered findings they can act on, fixes they can send back unchanged, and safe ways for many of them to work on the same model. This guide covers the machine side of the studio.

- [The studio protocol](#the-studio-protocol)
- [The studio as an MCP server](#the-studio-as-an-mcp-server)
- [Many MCP servers through one gateway](#many-mcp-servers-through-one-gateway)

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
| 600-999 | extensions | added with `api.code(...)` |

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
    api.code(601, "too_many_lags", "a brick reads a variable with more than four lags")

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
- **Resources.** The protocol (`studio://protocol`), the port registry, the brick catalog, the example models, `AGENTS.md`, the guides, and each skill (`studio://skills/<name>`).
- **Compact mode.** `--compact` offers a single tool, `studio_call`, that takes protocol messages and batches: one tool description instead of twenty, and many operations per call.
- **Fewer tools.** `--tools lego,ka` offers only some groups.

Claude Code picks up the server from `.mcp.json` in the repository and asks you to approve it the first time. For other clients, register the command `python tools/mcp_server.py` with the repository as the working folder. To see the tools: `python tools/mcp_server.py --list`.

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
