#!/usr/bin/env python3
"""Tests for the machine side of the studio: protocol, MCP server, workspace, improvement loop, economy engine.

Run with the other studio tests (python tools/test_studio.py) or alone: python tools/test_agents.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)

import studio_api as S  # noqa: E402

S.load_extensions()
EXAMPLE = os.path.join(ROOT, "lego", "examples", "small-open-economy.lego.json")


def H(op, **a):
    return S.handle({"op": op, "a": a})


def example():
    with open(EXAMPLE, encoding="utf-8") as f:
        return json.load(f)


class TestProtocol(unittest.TestCase):
    def test_hello_teaches_the_whole_protocol(self):
        r = H("hello")
        self.assertTrue(r["ok"])
        self.assertEqual(r["r"]["protocol"], "esp/1")
        for key in ("keys", "rules", "codes", "limits", "ops"):
            self.assertIn(key, r["r"])
        for name, spec in r["r"]["ops"].items():
            self.assertTrue(spec["s"], name)
        self.assertIn("lego.check", r["r"]["ops"])
        self.assertTrue(r["r"]["ops"]["lego.approve"].get("human"))

    def test_every_pattern_has_a_code(self):
        for c, _ in S.PATTERNS:
            self.assertIn(c, S.CODES)

    def test_check_gives_codes_and_a_stable_fingerprint(self):
        r1 = H("lego.check", m=EXAMPLE)
        r2 = H("lego.check", d=example())
        self.assertTrue(r1["r"]["pass"])
        self.assertEqual(r1["h"], r2["h"])
        self.assertEqual(r1["h"], S.fingerprint(example()))

    def test_agent_repairs_the_bridge_exercise_with_the_fixes_given(self):
        d = example()
        r = H("lego.patch", d=d, b="fiscal-debt-rule", set={"freq": "A"})
        self.assertEqual(r["w"][0][0], 301)
        d = r["r"]["d"]
        for _ in range(5):                       # follow the fixes, unchanged, until the strict check passes
            chk = H("lego.check", d=d, strict=True)
            if chk["r"]["pass"]:
                break
            fx = chk["fix"][0]
            r = H(fx["op"], d=d, **dict(fx["a"], apply=True))
            self.assertTrue(r["ok"], r)
            d = r["r"]["d"]
        self.assertTrue(H("lego.check", d=d, strict=True)["r"]["pass"])
        b = [x for x in d["bricks"] if x["id"] == "fiscal-debt-rule"][0]
        self.assertEqual(b["bridge_test"]["result"], "pass")
        self.assertEqual(b["bridge"]["methods"]["policy_rate"], "average")

    def test_missing_method_and_wrong_measure_are_coded(self):
        d = H("lego.patch", d=example(), b="fiscal-debt-rule", set={"freq": "A"})["r"]["d"]
        d = H("lego.bridge", d=d, b="fiscal-debt-rule", methods={"gdp_growth": "average"})["r"]["d"]
        r = H("lego.check", d=d)
        self.assertIn(211, [e[0] for e in r["e"]])
        self.assertIn({"op": "lego.bridge", "a": {"b": "fiscal-debt-rule", "p": "output_gap", "method": "average"}},
                      r["fix"])
        r = H("lego.bridge", d=d, b="fiscal-debt-rule", auto=True)
        r = H("lego.bridge", d=r["r"]["d"], b="fiscal-debt-rule", p="policy_rate", method="sum")
        self.assertIn(303, [w[0] for w in r["w"]])

    def test_incomplete_data_refused(self):
        r = H("bridge.convert", rows=[["2025Q1", 1], ["2025Q2", 2], ["2025Q2", 3], ["2025Q4", 4]], method="sum",
              **{"from": "Q", "to": "A"})
        self.assertFalse(r["ok"])
        self.assertEqual(r["e"][0][0], 404)
        self.assertIn("2025Q3", r["e"][0][1])

    def test_signoff_is_for_people_only(self):
        r = H("lego.approve", m=EXAMPLE, b="core-gap-open", by="agent")
        self.assertEqual(r["e"][0][0], 104)

    def test_writes_need_the_right_base_and_no_new_errors(self):
        d = tempfile.mkdtemp()
        try:
            path = os.path.join(d, "model.lego.json")
            shutil.copy(EXAMPLE, path)
            h0 = H("lego.check", m=path)["h"]
            r = H("lego.detach", m=path, b="world-exogenous", apply=True, base=h0)
            self.assertEqual(r["e"][0][0], 218)              # would open studs
            self.assertEqual(H("lego.check", m=path)["h"], h0)
            r = H("lego.patch", m=path, b="fiscal-debt-rule", set={"summary": "a note"}, apply=True, base="0" * 12)
            self.assertEqual(r["e"][0][0], 219)              # someone else changed it
            r = H("lego.patch", m=path, b="fiscal-debt-rule", set={"summary": "a note"}, apply=True, base=h0)
            self.assertTrue(r["r"]["applied"], r)
            self.assertNotEqual(H("lego.check", m=path)["h"], h0)
        finally:
            shutil.rmtree(d)

    def test_known_answer_task_never_contains_the_answer(self):
        r = H("ka.task", case="debt-steady-state")
        self.assertIn("parameters.json", r["r"]["files"])
        self.assertNotIn("0.525", json.dumps(r["r"]))
        self.assertTrue(H("ka.check", case="debt-steady-state", result={"debt_ratio": 0.525})["r"]["pass"])
        self.assertEqual(H("ka.check", case="bridge-flow", result={"annual": 4})["e"][0][0], 401)

    def test_batch_errors_and_say(self):
        out = S.handle_any([{"op": "ops", "id": 1}, {"op": "nope", "id": 2}, {"id": 3}])
        self.assertEqual([o["id"] for o in out], [1, 2, 3])
        self.assertEqual(out[1]["e"][0][0], 101)
        self.assertEqual(out[2]["e"][0][0], 100)
        text = S.say(H("lego.check", d=H("lego.detach", d=example(), b="world-exogenous")["r"]["d"]))
        self.assertIn("nothing provides", text)
        self.assertIn("Suggested fix: lego.attach", text)

    def test_serve_transport(self):
        p = subprocess.run([sys.executable, os.path.join(TOOLS, "studio_api.py"), "serve"],
                           input='{"op":"hello","a":{"brief":true},"id":1}\n[{"op":"ka.list"}]\nnot json\n',
                           capture_output=True, text=True, timeout=60)
        lines = [json.loads(x) for x in p.stdout.splitlines()]
        self.assertEqual(lines[0]["id"], 1)
        self.assertIsInstance(lines[1], list)
        self.assertEqual(lines[2]["e"][0][0], 100)

    def test_extensions_add_operations_and_codes(self):
        d = tempfile.mkdtemp()
        try:
            with open(os.path.join(d, "lags.py"), "w", encoding="utf-8") as f:
                f.write("def register(api):\n"
                        "    api.code(601, 'too_many_lags', 'a brick reads a variable with more than four lags')\n"
                        "    @api.op('mytools.lags', 'list lags', {'m': 'str manifest'})\n"
                        "    def lags(a, ctx):\n"
                        "        src = api.resolve(a)\n"
                        "        return api.ok({'n': sum(len(api.lego.reqs(b)) for b in api.lego.attached(src.doc))})\n")
            S.load_extensions([d])
            self.assertGreater(H("mytools.lags", m=EXAMPLE)["r"]["n"], 0)
            self.assertIn("601", H("hello")["r"]["codes"])
        finally:
            S.OPS.pop("mytools.lags", None)
            S.CODES.pop(601, None)
            shutil.rmtree(d)


TINY = """import json, sys
n = sys.argv[1]
for line in sys.stdin:
    r = json.loads(line); i = r.get("id")
    if i is None:
        continue
    m = r["method"]
    if m == "initialize":
        res = {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}}, "serverInfo": {"name": n, "version": "1"}}
    elif m == "tools/list":
        res = {"tools": [{"name": "series_" + n, "description": "statistics series " + n, "inputSchema": {"type": "object"}},
                         {"name": "delete_all", "description": "remove everything", "inputSchema": {"type": "object"}}]}
    elif m == "tools/call":
        res = {"content": [{"type": "text", "text": json.dumps({"server": n, "args": r["params"]["arguments"]})}]}
    else:
        res = {}
    print(json.dumps({"jsonrpc": "2.0", "id": i, "result": res}), flush=True)
"""


def rpc(i, method, params=None):
    return {"jsonrpc": "2.0", "id": i, "method": method, "params": params or {}}


class TestMCP(unittest.TestCase):
    def setUp(self):
        import mcp_server
        self.M = mcp_server
        self.srv = mcp_server.Server()

    def ask(self, method, params=None):
        return self.srv.dispatch(rpc(1, method, params))

    def test_initialize_and_capabilities(self):
        r = self.ask("initialize", {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "t"}})
        self.assertEqual(r["result"]["protocolVersion"], "2025-03-26")
        for cap in ("tools", "resources", "prompts"):
            self.assertIn(cap, r["result"]["capabilities"])
        self.assertIn("studio_hello", r["result"]["instructions"])
        self.assertIsNone(self.srv.dispatch({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_every_operation_is_a_tool_except_sign_off(self):
        tools = self.ask("tools/list")["result"]["tools"]
        names = {t["name"] for t in tools}
        for opname, spec in S.OPS.items():
            (self.assertNotIn if spec["human"] else self.assertIn)(self.M.tool_name(opname), names)
        for t in tools:
            self.assertEqual(t["inputSchema"]["type"], "object")

    def test_tool_call_returns_structured_protocol_response(self):
        r = self.ask("tools/call", {"name": "lego_check", "arguments": {"m": EXAMPLE}})["result"]
        self.assertFalse(r["isError"])
        self.assertTrue(r["structuredContent"]["r"]["pass"])
        r = self.ask("tools/call", {"name": "lego_detach", "arguments": {"m": EXAMPLE, "b": "world-exogenous",
                                                                         "apply": True}})["result"]
        self.assertTrue(r["isError"])
        self.assertEqual(r["structuredContent"]["e"][0][0], 218)

    def test_compact_mode_takes_batches(self):
        srv = self.M.Server(compact=True)
        tools = srv.dispatch(rpc(1, "tools/list"))["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["studio_call"])
        r = srv.dispatch(rpc(2, "tools/call", {"name": "studio_call", "arguments": {"msg": [
            {"op": "hello", "a": {"brief": True}}, {"op": "lego.check", "a": {"m": EXAMPLE}}]}}))["result"]
        self.assertEqual(len(r["structuredContent"]["batch"]), 2)

    def test_skills_are_prompts_and_guides_are_resources(self):
        prompts = self.ask("prompts/list")["result"]["prompts"]
        self.assertEqual(len(prompts), len(os.listdir(os.path.join(ROOT, ".claude", "skills"))))
        r = self.ask("prompts/get", {"name": "lego-check", "arguments": {"request": "my model"}})["result"]
        self.assertIn("my model", r["messages"][0]["content"]["text"])
        uris = [x["uri"] for x in self.ask("resources/list")["result"]["resources"]]
        self.assertIn("studio://protocol", uris)
        proto = json.loads(self.ask("resources/read", {"uri": "studio://protocol"})["result"]["contents"][0]["text"])
        self.assertEqual(proto["protocol"], "esp/1")
        self.assertIn("error", self.ask("resources/read", {"uri": "studio://nothing"}))
        self.assertIn("error", self.ask("no/such/method"))

    def test_stdio_server(self):
        msgs = [rpc(1, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t"}}),
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                rpc(2, "tools/call", {"name": "ka_check", "arguments": {"case": "bridge-flow", "result": {"annual": 10}}})]
        p = subprocess.run([sys.executable, os.path.join(TOOLS, "mcp_server.py")],
                           input="\n".join(json.dumps(m) for m in msgs) + "\n", capture_output=True, text=True,
                           timeout=60, cwd=ROOT)
        out = [json.loads(x) for x in p.stdout.splitlines()]
        self.assertEqual([o["id"] for o in out], [1, 2])
        self.assertTrue(out[1]["result"]["structuredContent"]["r"]["pass"])

    def test_project_mcp_config_points_at_the_server(self):
        with open(os.path.join(ROOT, ".mcp.json"), encoding="utf-8") as f:
            cfg = json.load(f)
        spec = list(cfg["mcpServers"].values())[0]
        self.assertTrue(os.path.exists(os.path.join(ROOT, spec["args"][0])))


class TestGateway(unittest.TestCase):
    N = 30

    @classmethod
    def setUpClass(cls):
        import mcp_gateway
        cls.G = mcp_gateway
        cls.dir = tempfile.mkdtemp()
        tiny = os.path.join(cls.dir, "tiny.py")
        with open(tiny, "w", encoding="utf-8") as f:
            f.write(TINY)
        servers = {f"s{i}": {"command": "python", "args": [tiny, str(i)], "deny": ["delete_*"]} for i in range(cls.N)}
        servers["studio"] = {"command": "python", "args": ["tools/mcp_server.py"]}
        servers["broken"] = {"command": "no-such-program-for-the-studio-test"}
        cls.cfg = os.path.join(cls.dir, "servers.json")
        with open(cls.cfg, "w", encoding="utf-8") as f:
            json.dump({"mcpServers": servers}, f)
        cls.gw = mcp_gateway.Gateway(mcp_gateway.load_config(cls.cfg), workers=32)
        cls.gw.start()

    @classmethod
    def tearDownClass(cls):
        cls.gw.stop()
        shutil.rmtree(cls.dir, ignore_errors=True)

    def test_many_servers_start_and_a_broken_one_does_not_stop_them(self):
        rows = {r["server"]: r for r in self.gw.servers()}
        self.assertEqual(sum(r["up"] for r in rows.values()), self.N + 1)
        self.assertFalse(rows["broken"]["up"])
        self.assertIn("error", rows["broken"])
        self.assertEqual(rows["s3"]["tools"], 1)          # delete_all is denied by the configuration

    def test_search_finds_tools_across_servers(self):
        found = [x["tool"] for x in self.gw.search("bridge frequency", 5)]
        self.assertIn("studio__bridge_convert", found)
        self.assertEqual(self.gw.search("series 7", 1)[0]["tool"], "s7__series_7")

    def test_batch_runs_in_parallel_and_keeps_order(self):
        calls = [{"tool": f"s{i}__series_{i}", "arguments": {"k": i}} for i in range(self.N)]
        calls += [{"tool": "studio__lego_check", "arguments": {"m": EXAMPLE}}, {"tool": "s1__delete_all"},
                  {"tool": "nobody__x"}]
        out = self.gw.batch(calls)
        for i in range(self.N):
            self.assertEqual(json.loads(out[i]["result"]["content"][0]["text"])["args"], {"k": i})
        self.assertTrue(out[self.N]["result"]["structuredContent"]["r"]["pass"])
        self.assertIn("not allowed", out[self.N + 1]["error"])
        self.assertIn("no server", out[self.N + 2]["error"])

    def test_router_and_flat_tool_lists(self):
        names = [t["name"] for t in self.gw.list_tools()]
        self.assertEqual(names, ["gateway_servers", "gateway_search", "gateway_call", "gateway_batch"])
        flat = self.G.Gateway({}, flat=True)
        flat.ups, flat._started = self.gw.ups, True
        self.assertIn("studio__lego_check", [t["name"] for t in flat.list_tools()])
        r = self.gw.call_tool("gateway_call", {"tool": "studio__ka_list"})
        self.assertIn("ar1-ols", r["structuredContent"]["r"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
