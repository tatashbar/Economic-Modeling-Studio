#!/usr/bin/env python3
"""The studio as an MCP server (Model Context Protocol), standard library only.

Every operation of the studio protocol (tools/studio_api.py) is an MCP tool: lego.check becomes lego_check,
and so on, including operations added by extensions. Skills are MCP prompts, and the protocol, the port
registry, the brick catalog and the guides are MCP resources.

Run (stdio transport; MCP clients start it for you, see .mcp.json):
    python tools/mcp_server.py
    python tools/mcp_server.py --tools lego,ka        only these groups of operations
    python tools/mcp_server.py --compact              one tool, studio_call, that takes protocol messages and
                                                      batches: for agents that drive many operations at once

To connect many MCP servers to an agent as one, see tools/mcp_gateway.py.
"""
import argparse
import glob
import json
import os
import re
import sys
import threading

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)

import studio_api as S  # noqa: E402

SUPPORTED = ("2025-06-18", "2025-03-26", "2024-11-05")
SERVER_INFO = {"name": "economic-modeling-studio", "version": S.VERSION}
INSTRUCTIONS = ("Economic Modeling Studio. Call studio_hello first: it returns the protocol, the finding codes and "
                "the rules. Findings are [code, brick, subject, ...]; send each 'fix' back unchanged to apply it. "
                "Changes are plans unless apply is true; send base (the fingerprint h you read) with every write. "
                "Sign-off is for people only. Use studio_say to explain any result to a person.")


def tool_name(op):
    return re.sub(r"[^A-Za-z0-9_-]", "_", op if "." in op else "studio." + op)


class Server:
    def __init__(self, groups=None, compact=False, ctx=None):
        S.load_extensions()
        self.groups = set(groups) if groups else None
        self.compact = compact
        self.ctx = ctx if ctx is not None else {}
        self.lock = threading.Lock()
        self.names = {}

    # ---------------------------------------------------------------- tools
    def tools(self):
        out = []
        if self.compact:
            out.append({"name": "studio_call", "description": "Send one studio protocol message or a batch (a list). "
                        "Call it with {\"msg\": {\"op\": \"hello\"}} first to learn the protocol.",
                        "inputSchema": {"type": "object", "properties": {
                            "msg": {"description": "a message {op, a, id} or a list of messages"},
                            "stop": {"type": "boolean", "description": "stop a batch at the first failure"}},
                            "required": ["msg"]}})
            self.names = {"studio_call": None}
            return out
        self.names = {}
        for name, spec in sorted(S.OPS.items()):
            if self.groups and spec["group"] not in self.groups and spec["group"] not in ("hello", "ops", "explain",
                                                                                          "say"):
                continue
            if spec["human"]:
                continue                      # people's operations are not offered to agents at all
            t = tool_name(name)
            self.names[t] = name
            desc = spec["summary"] + (" (changes the model only with apply: true)" if spec["mutates"] else "")
            tool = {"name": t, "description": desc, "inputSchema": S._arg_schema(spec)}
            tool["annotations"] = {"readOnlyHint": not spec["mutates"], "idempotentHint": not spec["mutates"],
                                   "openWorldHint": False}
            out.append(tool)
        return out

    def call(self, name, args):
        if not self.names:
            self.tools()
        if name not in self.names:
            return {"isError": True, "content": [{"type": "text", "text": f"unknown tool {name}"}]}
        if name == "studio_call":
            resp = S.handle_any(args.get("msg"), dict(self.ctx, stop=bool(args.get("stop"))))
        else:
            resp = S.handle({"op": self.names[name], "a": args or {}}, self.ctx)
        ok = all(r.get("ok") for r in resp) if isinstance(resp, list) else resp.get("ok")
        text = json.dumps(resp, separators=(",", ":"), ensure_ascii=False)
        out = {"content": [{"type": "text", "text": text}], "isError": not ok}
        if isinstance(resp, dict):
            out["structuredContent"] = resp
        else:
            out["structuredContent"] = {"batch": resp}
        return out

    # ---------------------------------------------------------------- resources
    def resources(self):
        res = [
            {"uri": "studio://protocol", "name": "Studio protocol", "mimeType": "application/json",
             "description": "the handshake: keys, rules, operations, finding codes, limits"},
            {"uri": "studio://ports", "name": "Port registry", "mimeType": "application/json",
             "description": "every shared variable with its unit, timing and measure"},
            {"uri": "studio://catalog", "name": "Brick catalog", "mimeType": "application/json",
             "description": "reusable bricks with what they provide and require"},
            {"uri": "studio://docs/agents", "name": "Guide for AI agents", "mimeType": "text/markdown"},
            {"uri": "studio://docs/lego", "name": "Lego guide", "mimeType": "text/markdown"},
            {"uri": "studio://agents-md", "name": "Project instructions (AGENTS.md)", "mimeType": "text/markdown"},
        ]
        for p in sorted(glob.glob(os.path.join(ROOT, "lego", "examples", "*.lego.json"))):
            n = os.path.basename(p)
            res.append({"uri": f"studio://examples/{n}", "name": f"Example model {n}", "mimeType": "application/json"})
        return res

    def read(self, uri):
        files = {"studio://docs/agents": "docs/agents.md", "studio://docs/lego": "docs/lego.md",
                 "studio://agents-md": "AGENTS.md"}
        if uri == "studio://protocol":
            return "application/json", json.dumps(S.handle({"op": "hello"})["r"])
        if uri == "studio://ports":
            return "application/json", json.dumps(S.handle({"op": "lego.ports"})["r"])
        if uri == "studio://catalog":
            return "application/json", json.dumps(S.handle({"op": "lego.catalog"})["r"])
        if uri in files:
            with open(os.path.join(ROOT, files[uri]), encoding="utf-8") as f:
                return "text/markdown", f.read()
        mt = re.match(r"studio://examples/([\w.-]+\.lego\.json)$", uri)
        if mt and os.path.isfile(os.path.join(ROOT, "lego", "examples", mt.group(1))):
            with open(os.path.join(ROOT, "lego", "examples", mt.group(1)), encoding="utf-8") as f:
                return "application/json", f.read()
        mt = re.match(r"studio://skills/([a-z0-9-]+)$", uri)
        if mt and os.path.isfile(os.path.join(ROOT, ".claude", "skills", mt.group(1), "SKILL.md")):
            with open(os.path.join(ROOT, ".claude", "skills", mt.group(1), "SKILL.md"), encoding="utf-8") as f:
                return "text/markdown", f.read()
        raise KeyError(uri)

    # ---------------------------------------------------------------- prompts (the skills)
    def _skills(self):
        out = []
        for p in sorted(glob.glob(os.path.join(ROOT, ".claude", "skills", "*", "SKILL.md"))):
            with open(p, encoding="utf-8") as f:
                text = f.read()
            mt = re.search(r"^description:\s*\"?(.*?)\"?\s*$", text, re.M)
            out.append((os.path.basename(os.path.dirname(p)), mt.group(1) if mt else "", text))
        return out

    def prompts(self):
        return [{"name": n, "description": d[:300],
                 "arguments": [{"name": "request", "description": "what you want done", "required": False}]}
                for n, d, _ in self._skills()]

    def prompt(self, name, args):
        for n, d, text in self._skills():
            if n == name:
                body = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
                req = (args or {}).get("request", "")
                msg = f"Run the studio workflow '/{n}'" + (f" for: {req}" if req else "") + \
                    f". Follow these instructions.\n\n{body}"
                return {"description": d, "messages": [{"role": "user", "content": {"type": "text", "text": msg}}]}
        raise KeyError(name)

    # ---------------------------------------------------------------- JSON-RPC
    def dispatch(self, req):
        method, params, rid = req.get("method"), req.get("params") or {}, req.get("id")
        if rid is None:                       # a notification: nothing to answer
            return None
        try:
            if method == "initialize":
                want = params.get("protocolVersion")
                result = {"protocolVersion": want if want in SUPPORTED else SUPPORTED[0],
                          "capabilities": {"tools": {"listChanged": False},
                                           "resources": {"subscribe": False, "listChanged": False},
                                           "prompts": {"listChanged": False}},
                          "serverInfo": SERVER_INFO, "instructions": INSTRUCTIONS}
            elif method == "ping":
                result = {}
            elif method == "tools/list":
                result = {"tools": self.tools()}
            elif method == "tools/call":
                result = self.call(params.get("name"), params.get("arguments") or {})
            elif method == "resources/list":
                result = {"resources": self.resources()}
            elif method == "resources/templates/list":
                result = {"resourceTemplates": [{"uriTemplate": "studio://skills/{name}", "name": "Skill instructions",
                                                 "mimeType": "text/markdown"}]}
            elif method == "resources/read":
                try:
                    mime, text = self.read(params.get("uri", ""))
                except KeyError:
                    return _error(rid, -32002, f"resource not found: {params.get('uri')}")
                result = {"contents": [{"uri": params["uri"], "mimeType": mime, "text": text}]}
            elif method == "prompts/list":
                result = {"prompts": self.prompts()}
            elif method == "prompts/get":
                try:
                    result = self.prompt(params.get("name"), params.get("arguments"))
                except KeyError:
                    return _error(rid, -32602, f"no prompt named {params.get('name')}")
            else:
                return _error(rid, -32601, f"method not found: {method}")
        except Exception as x:  # noqa: BLE001
            return _error(rid, -32603, f"{type(x).__name__}: {x}")
        return {"jsonrpc": "2.0", "id": rid, "result": result}

    def handle_line(self, line):
        try:
            req = json.loads(line)
        except ValueError:
            return _error(None, -32700, "parse error")
        if isinstance(req, list):             # JSON-RPC batch (older protocol versions)
            out = [r for r in (self.dispatch(x) for x in req) if r is not None]
            return out or None
        return self.dispatch(req)

    def serve(self, stdin=None, stdout=None):
        stdin, stdout = stdin or sys.stdin, stdout or sys.stdout
        for line in stdin:
            if not line.strip():
                continue
            resp = self.handle_line(line)
            if resp is not None:
                stdout.write(json.dumps(resp, separators=(",", ":"), ensure_ascii=False) + "\n")
                stdout.flush()


def _error(rid, code, msg):
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": msg}}


def main(argv=None):
    ap = argparse.ArgumentParser(description="The studio as an MCP server (stdio)")
    ap.add_argument("--tools", help="comma-separated operation groups to offer (default: all)")
    ap.add_argument("--compact", action="store_true", help="one tool, studio_call, taking protocol messages")
    ap.add_argument("--list", action="store_true", help="print the tools and exit")
    a = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    srv = Server(a.tools.split(",") if a.tools else None, a.compact)
    if a.list:
        for t in srv.tools():
            print(f"{t['name']:<24} {t['description']}")
        return 0
    srv.serve()
    return 0


if __name__ == "__main__":
    sys.exit(main())
