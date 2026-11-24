#!/usr/bin/env python3
"""One MCP server in front of many: connect an agent to tens or hundreds of MCP servers at once.

An agent connected to 100 servers directly would carry thousands of tool descriptions in its context and wait
on each server in turn. The gateway starts the servers in parallel, indexes their tools, and offers the agent a
few tools instead: list the servers, search every tool by keyword, call any tool, and call many tools on many
servers in parallel in one request. Servers that fail are marked down without stopping the others.

Configuration (mcp/servers.json, or --config FILE; the same shape as .mcp.json):
    {"mcpServers": {
        "studio": {"command": "python", "args": ["tools/mcp_server.py"]},
        "data":   {"command": "python", "args": ["path/to/data_server.py"], "env": {"KEY": "..."},
                   "allow": ["fetch_*"], "deny": ["delete_*"], "timeout": 30}
    }}

Run:
    python tools/mcp_gateway.py                    serve on stdio (router mode: gateway_* tools)
    python tools/mcp_gateway.py --flat             every upstream tool, named server__tool (for a few servers)
    python tools/mcp_gateway.py --status           start everything, print each server and its tool count, exit
"""
import argparse
import concurrent.futures as cf
import fnmatch
import json
import os
import queue
import re
import subprocess
import sys
import threading
import time

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
DEFAULT_CONFIG = os.path.join(ROOT, "mcp", "servers.json")
PROTOCOL_VERSION = "2025-06-18"
SEP = "__"


class Upstream:
    """A client connection to one MCP server over stdio."""

    def __init__(self, name, spec, cwd=ROOT):
        self.name, self.spec, self.cwd = name, spec, cwd
        self.timeout = float(spec.get("timeout", 30))
        self.proc, self.tools, self.error, self.calls, self.failures = None, [], None, 0, 0
        self._id, self._pending, self._lock = 0, {}, threading.Lock()
        self.started = None

    @property
    def up(self):
        return self.proc is not None and self.proc.poll() is None and self.error is None

    def start(self):
        cmd = [self.spec["command"]] + list(self.spec.get("args", []))
        if cmd[0] in ("python", "python3"):
            cmd[0] = sys.executable
        env = dict(os.environ, **{k: str(v) for k, v in (self.spec.get("env") or {}).items()})
        try:
            self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                         cwd=self.spec.get("cwd", self.cwd), env=env, text=True, encoding="utf-8",
                                         bufsize=1)
        except OSError as x:
            self.error = f"could not start: {x}"
            return self
        threading.Thread(target=self._reader, daemon=True).start()
        try:
            self.request("initialize", {"protocolVersion": PROTOCOL_VERSION, "capabilities": {},
                                        "clientInfo": {"name": "studio-gateway", "version": "1"}})
            self.notify("notifications/initialized")
            self.tools = self._list_tools()
            self.started = time.time()
        except Exception as x:  # noqa: BLE001
            self.error = f"{type(x).__name__}: {x}"
            self.stop()
        return self

    def _list_tools(self):
        out, cursor = [], None
        while True:
            res = self.request("tools/list", {"cursor": cursor} if cursor else {})
            out += res.get("tools", [])
            cursor = res.get("nextCursor")
            if not cursor:
                return [t for t in out if self.allowed(t["name"])]

    def allowed(self, tool):
        allow, deny = self.spec.get("allow"), self.spec.get("deny") or []
        if any(fnmatch.fnmatch(tool, p) for p in deny):
            return False
        return not allow or any(fnmatch.fnmatch(tool, p) for p in allow)

    def _reader(self):
        for line in self.proc.stdout:
            try:
                msg = json.loads(line)
            except ValueError:
                continue
            q = self._pending.pop(msg.get("id"), None)
            if q is not None:
                q.put(msg)
        for q in list(self._pending.values()):   # the server exited: release everyone waiting
            q.put({"error": {"message": "server exited"}})

    def notify(self, method, params=None):
        self._send({"jsonrpc": "2.0", "method": method, **({"params": params} if params else {})})

    def _send(self, msg):
        with self._lock:
            self.proc.stdin.write(json.dumps(msg) + "\n")
            self.proc.stdin.flush()

    def request(self, method, params, timeout=None):
        with self._lock:
            self._id += 1
            rid = self._id
        q = queue.Queue(maxsize=1)
        self._pending[rid] = q
        try:
            self._send({"jsonrpc": "2.0", "id": rid, "method": method, "params": params})
        except (OSError, ValueError) as x:
            self._pending.pop(rid, None)
            raise RuntimeError(f"{self.name}: cannot write to the server ({x})")
        try:
            msg = q.get(timeout=timeout or self.timeout)
        except queue.Empty:
            self._pending.pop(rid, None)
            raise TimeoutError(f"{self.name}: no answer to {method} within {timeout or self.timeout:g}s")
        if "error" in msg:
            raise RuntimeError(f"{self.name}: {msg['error'].get('message')}")
        return msg.get("result", {})

    def call(self, tool, args):
        if not self.allowed(tool):
            raise PermissionError(f"{self.name}: tool {tool} is not allowed by the gateway configuration")
        self.calls += 1
        try:
            return self.request("tools/call", {"name": tool, "arguments": args or {}})
        except Exception:
            self.failures += 1
            raise

    def stop(self):
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.stdin.close()
                self.proc.wait(timeout=5)
            except Exception:  # noqa: BLE001
                self.proc.kill()


def load_config(path):
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    servers = cfg.get("mcpServers") or cfg.get("servers") or {}
    for name in servers:
        if SEP in name or not re.match(r"^[A-Za-z0-9_-]+$", name):
            raise SystemExit(f"server name '{name}': use letters, digits, - and _ only, and no '{SEP}'")
    return servers


class Gateway:
    def __init__(self, servers, flat=False, workers=32, on_call=None):
        self.ups = {n: Upstream(n, s) for n, s in servers.items() if not s.get("disabled")}
        self.flat, self.workers, self.on_call = flat, workers, on_call
        self.pool = cf.ThreadPoolExecutor(max_workers=workers)
        self._started = False

    def start(self):
        if not self._started:
            list(self.pool.map(lambda u: u.start(), self.ups.values()))
            self._started = True
        return self

    def stop(self):
        for u in self.ups.values():
            u.stop()
        self.pool.shutdown(wait=False)

    # ---------------------------------------------------------------- what the agent sees
    def index(self):
        self.start()
        return [(u.name, t) for u in self.ups.values() if u.up for t in u.tools]

    def servers(self):
        self.start()
        return [{"server": n, "up": u.up, "tools": len(u.tools), "calls": u.calls, "failures": u.failures,
                 **({"error": u.error} if u.error else {})} for n, u in sorted(self.ups.items())]

    def search(self, query, limit=20, server=None):
        words = [w for w in re.split(r"\W+", (query or "").lower()) if w]
        scored = []
        for name, t in self.index():
            if server and name != server:
                continue
            hay = f"{name} {t['name']} {t.get('description', '')}".lower()
            toks = re.split(r"[\W_]+", hay)
            ntoks = set(re.split(r"[\W_]+", t["name"].lower()))
            score = sum(3 * toks.count(w) + (w in hay) + 4 * (w in ntoks) for w in words)
            if score or not words:
                scored.append((-score, f"{name}{SEP}{t['name']}", t))
        scored.sort(key=lambda x: (x[0], x[1]))
        return [{"tool": full, "description": t.get("description", ""), "inputSchema": t.get("inputSchema", {})}
                for _, full, t in scored[:limit]]

    def call(self, full, args):
        server, _, tool = full.partition(SEP)
        u = self.ups.get(server)
        if u is None:
            raise KeyError(f"no server '{server}' (tool names are server{SEP}tool)")
        if not u.up:
            u.error = None
            u.start()                          # one restart attempt
            if not u.up:
                raise RuntimeError(f"server '{server}' is down: {u.error}")
        t0 = time.time()
        res = u.call(tool, args)
        if self.on_call:
            self.on_call(server, tool, args, res, time.time() - t0)
        return res

    def batch(self, calls):
        def one(c):
            try:
                return {"tool": c["tool"], "result": self.call(c["tool"], c.get("arguments") or {})}
            except Exception as x:  # noqa: BLE001
                return {"tool": c["tool"], "error": f"{type(x).__name__}: {x}"}
        return list(self.pool.map(one, calls))

    # ---------------------------------------------------------------- MCP server side
    ROUTER_TOOLS = [
        {"name": "gateway_servers", "description": "the connected MCP servers: up or down, tool counts, calls, failures",
         "inputSchema": {"type": "object", "properties": {}}},
        {"name": "gateway_search", "description": "find tools across every connected server by keyword; returns "
         "full names (server__tool) with their input schemas",
         "inputSchema": {"type": "object", "properties": {
             "query": {"type": "string"}, "server": {"type": "string", "description": "only this server"},
             "limit": {"type": "integer"}}, "required": ["query"]}},
        {"name": "gateway_call", "description": "call one tool on any server by its full name (server__tool)",
         "inputSchema": {"type": "object", "properties": {
             "tool": {"type": "string"}, "arguments": {"type": "object"}}, "required": ["tool"]}},
        {"name": "gateway_batch", "description": "call many tools, on many servers, in parallel; results come back "
         "in the same order",
         "inputSchema": {"type": "object", "properties": {"calls": {"type": "array", "items": {
             "type": "object", "properties": {"tool": {"type": "string"}, "arguments": {"type": "object"}},
             "required": ["tool"]}}}, "required": ["calls"]}},
    ]

    def list_tools(self):
        if not self.flat:
            return self.ROUTER_TOOLS
        return [dict(t, name=f"{n}{SEP}{t['name']}", description=f"[{n}] {t.get('description', '')}")
                for n, t in self.index()]

    def call_tool(self, name, args):
        def wrap(obj, is_error=False):
            return {"content": [{"type": "text", "text": json.dumps(obj, ensure_ascii=False)}],
                    "structuredContent": obj if isinstance(obj, dict) else {"items": obj}, "isError": is_error}
        try:
            if name == "gateway_servers":
                return wrap({"servers": self.servers()})
            if name == "gateway_search":
                return wrap({"tools": self.search(args.get("query", ""), int(args.get("limit", 20)), args.get("server"))})
            if name == "gateway_call":
                return self.call(args["tool"], args.get("arguments") or {})
            if name == "gateway_batch":
                return wrap({"results": self.batch(args.get("calls") or [])})
            if SEP in name:
                return self.call(name, args)
            return wrap({"error": f"unknown tool {name}"}, True)
        except Exception as x:  # noqa: BLE001
            return wrap({"error": f"{type(x).__name__}: {x}"}, True)

    def dispatch(self, req):
        method, params, rid = req.get("method"), req.get("params") or {}, req.get("id")
        if rid is None:
            return None
        if method == "initialize":
            result = {"protocolVersion": params.get("protocolVersion", PROTOCOL_VERSION),
                      "capabilities": {"tools": {"listChanged": False}},
                      "serverInfo": {"name": "studio-gateway", "version": "1"},
                      "instructions": "A gateway to many MCP servers. Use gateway_search to find a tool, then "
                                      "gateway_call, or gateway_batch to call many at once in parallel."}
        elif method == "ping":
            result = {}
        elif method == "tools/list":
            result = {"tools": self.list_tools()}
        elif method == "tools/call":
            result = self.call_tool(params.get("name"), params.get("arguments") or {})
        else:
            return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": f"method not found: {method}"}}
        return {"jsonrpc": "2.0", "id": rid, "result": result}

    def serve(self, stdin=None, stdout=None):
        stdin, stdout = stdin or sys.stdin, stdout or sys.stdout
        lock = threading.Lock()

        def answer(req):
            resp = self.dispatch(req)
            if resp is not None:
                with lock:
                    stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
                    stdout.flush()
        for line in stdin:
            if not line.strip():
                continue
            try:
                req = json.loads(line)
            except ValueError:
                continue
            if req.get("method") == "tools/call":
                self.pool.submit(answer, req)    # calls run concurrently; answers carry their ids
            else:
                answer(req)


def main(argv=None):
    ap = argparse.ArgumentParser(description="One MCP server in front of many")
    ap.add_argument("--config", default=DEFAULT_CONFIG)
    ap.add_argument("--flat", action="store_true", help="offer every upstream tool by name instead of the router tools")
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--status", action="store_true", help="start the servers, print their status and exit")
    a = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    gw = Gateway(load_config(a.config), flat=a.flat, workers=a.workers)
    if a.status:
        t0 = time.time()
        rows = gw.servers()
        for r in rows:
            print(f"{'up  ' if r['up'] else 'DOWN'} {r['server']:<24} {r['tools']:>4} tools  {r.get('error', '')}")
        print(f"{sum(r['up'] for r in rows)} of {len(rows)} servers up, {sum(r['tools'] for r in rows)} tools, "
              f"started in {time.time() - t0:.1f}s")
        gw.stop()
        return 0
    try:
        gw.serve()
    finally:
        gw.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
