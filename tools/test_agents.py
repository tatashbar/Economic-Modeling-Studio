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

    def test_outside_agents_reach_the_studio_agents_and_skills(self):
        n_agents = len([f for f in os.listdir(os.path.join(ROOT, ".claude", "agents")) if f.endswith(".md")])
        self.assertEqual(len(H("agents.list")["r"]), n_agents)
        found = H("agents.list", query="translation equivalence", limit=3)["r"]
        self.assertIn("translation-equivalence-auditor", found)
        r = H("agents.get", name="source-code-analyst")["r"]
        self.assertIn("Source Code Analyst", r["instructions"])
        self.assertNotIn("maxTurns", r["instructions"])                  # the frontmatter is left out
        brief = H("agents.brief", name="source-code-analyst", task="map the do-files in folder X")["r"]["brief"]
        self.assertIn("map the do-files in folder X", brief)
        self.assertIn("never by you", brief)
        self.assertEqual(H("agents.get", name="nobody")["e"][0][0], 106)
        self.assertIn("lego-check", H("skills.list", query="lego")["r"])
        self.assertIn("lego", H("skills.get", name="lego-check")["r"]["workflow"])

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
                        "    api.code(901, 'too_many_lags', 'a brick reads a variable with more than four lags')\n"
                        "    @api.op('mytools.lags', 'list lags', {'m': 'str manifest'})\n"
                        "    def lags(a, ctx):\n"
                        "        src = api.resolve(a)\n"
                        "        return api.ok({'n': sum(len(api.lego.reqs(b)) for b in api.lego.attached(src.doc))})\n")
            S.load_extensions([d])
            self.assertGreater(H("mytools.lags", m=EXAMPLE)["r"]["n"], 0)
            self.assertIn("901", H("hello")["r"]["codes"])
        finally:
            S.OPS.pop("mytools.lags", None)
            S.CODES.pop(901, None)
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


PERSON = {"human": True, "agent": "economist"}

WORKER = """import sys
sys.path.insert(0, sys.argv[1])
import studio_api as S
S.load_extensions()
ws, who, k = sys.argv[2], sys.argv[3], int(sys.argv[4])
done = 0
while done < k:
    g = S.handle({"op": "ws.get", "a": {"t": "count", "ws": ws}}, {"agent": who})
    d = g["r"]["d"]; d["n"] += 1
    r = S.handle({"op": "ws.put", "a": {"t": "count", "d": d, "base": g["h"], "ws": ws}}, {"agent": who})
    done += bool(r["ok"])
"""


class TestWorkspace(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.ws = os.path.join(self.dir, "ws.db")

    def tearDown(self):
        import workspace
        for c in getattr(workspace._local, "conns", {}).values():
            c.close()
        workspace._local.conns = {}
        shutil.rmtree(self.dir, ignore_errors=True)

    def W(self, op, ctx=None, **a):
        return S.handle({"op": op, "a": dict(a, ws=self.ws)}, ctx if ctx is not None else {"agent": "b1"})

    def test_track_edits_are_logged_and_reported(self):
        self.assertTrue(self.W("ws.track", name="main", m=EXAMPLE, goal="annual fiscal rule")["ok"])
        r = self.W("lego.patch", t="main", b="fiscal-debt-rule", set={"freq": "A"}, apply=True)
        self.assertTrue(r["r"]["applied"])
        fx = r["fix"][0]
        self.assertTrue(self.W(fx["op"], t="main", **dict(fx["a"], apply=True))["ok"])
        self.assertTrue(self.W("lego.bridge_test", t="main", apply=True)["r"]["pass"])
        self.assertTrue(self.W("lego.check", t="main", strict=True)["r"]["pass"])
        events = self.W("ws.log", t="main")["r"]["events"]
        self.assertEqual([e[3] for e in events][:4], ["ws.track", "lego.patch", "lego.bridge", "lego.bridge_test"])
        text = self.W("ws.report", PERSON, t="main")["r"]["text"]
        for s in ("Goal: annual fiscal rule", "changed fiscal-debt-rule (freq)", "ran the bridge tests", "0 error(s)"):
            self.assertIn(s, text)

    def test_people_steer_agents_must_listen(self):
        self.W("ws.track", name="main", m=EXAMPLE)
        self.assertEqual(self.W("ws.post", kind="pause", t="main")["e"][0][0], 104)      # agents cannot pause
        self.W("ws.post", PERSON, kind="constraint", text="keep world-exogenous", to="track:main")
        r = self.W("lego.patch", t="main", b="fiscal-debt-rule", set={"summary": "x"}, apply=True)
        self.assertEqual(r["e"][0][0], 503)                                           # unread message from a person
        msgs = self.W("ws.inbox")["r"]
        self.assertEqual(msgs["constraints"], ["keep world-exogenous"])
        self.assertTrue(self.W("lego.patch", t="main", b="fiscal-debt-rule", set={"summary": "x"}, apply=True)["ok"])
        self.W("ws.post", PERSON, kind="freeze", t="main", b="monetary-taylor")
        self.W("ws.inbox")
        r = self.W("lego.patch", t="main", b="monetary-taylor", set={"summary": "y"}, apply=True)
        self.assertEqual(r["e"][0][0], 502)
        self.W("ws.post", PERSON, kind="pause", t="main")
        self.W("ws.inbox")
        r = self.W("lego.patch", t="main", b="fiscal-debt-rule", set={"summary": "z"}, apply=True)
        self.assertEqual(r["e"][0][0], 501)
        self.assertTrue(self.W("lego.check", t="main")["ok"])                         # reading is still allowed
        self.W("ws.post", PERSON, kind="resume", t="main")
        self.W("ws.inbox")
        self.assertTrue(self.W("lego.patch", t="main", b="fiscal-debt-rule", set={"summary": "z"}, apply=True)["ok"])

    def test_veto_rolls_a_track_back(self):
        h0 = self.W("ws.track", name="main", m=EXAMPLE)["h"]
        r = self.W("lego.detach", t="main", b="fan-chart-output", apply=True)
        self.assertTrue(r["r"]["applied"], r)
        seq = self.W("ws.log", t="main")["r"]["events"][-1][0]
        self.assertTrue(self.W("ws.post", PERSON, kind="veto", ref=seq, text="keep the fan chart")["ok"])
        self.assertEqual(self.W("ws.get", t="main")["h"], h0)

    def test_questions_wait_for_a_person(self):
        self.W("ws.track", name="main", m=EXAMPLE)
        q = self.W("ws.post", kind="question", text="swap the Taylor rule?", to="track:main")["r"]["id"]
        self.assertIn("swap the Taylor rule?", self.W("ws.report", PERSON, t="main")["r"]["text"])
        self.W("ws.post", PERSON, kind="answer", ref=q, text="no", to="agent:b1")
        self.assertNotIn("Waiting for a person", self.W("ws.report", PERSON, t="main")["r"]["text"])
        self.assertEqual(self.W("ws.inbox")["r"]["msgs"][-1]["text"], "no")

    def test_leases_and_promotion(self):
        self.W("ws.track", name="main", m=EXAMPLE)
        self.W("ws.track", name="try", **{"from": "main"})
        self.assertTrue(self.W("ws.lease", resource="brick:fiscal", ttl=30)["ok"])
        r = self.W("ws.lease", {"agent": "b2"}, resource="brick:fiscal")
        self.assertEqual(r["e"][0][0], 504)
        self.W("lego.patch", t="try", b="fiscal-debt-rule", set={"summary": "better"}, apply=True)
        head = self.W("ws.get", t="main")["h"]
        self.assertEqual(self.W("ws.promote", t="try", into="main", base="0" * 12)["e"][0][0], 219)
        self.assertTrue(self.W("ws.promote", t="try", into="main", base=head)["ok"])
        self.assertEqual(self.W("ws.get", t="main")["h"], self.W("ws.get", t="try")["h"])

    def test_no_write_is_lost_with_many_writers(self):
        import threading
        self.W("ws.track", name="count", d={"n": 0}, kind="json")

        def worker(i):
            done = 0
            while done < 3:
                g = self.W("ws.get", {"agent": f"t{i}"}, t="count")
                d = dict(g["r"]["d"], n=g["r"]["d"]["n"] + 1)
                done += bool(self.W("ws.put", {"agent": f"t{i}"}, t="count", d=d, base=g["h"])["ok"])
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(40)]
        [t.start() for t in threads]
        procs = [subprocess.Popen([sys.executable, "-c", WORKER, TOOLS, self.ws, f"p{i}", "5"]) for i in range(4)]
        [t.join() for t in threads]
        [p.wait(timeout=300) for p in procs]
        self.assertEqual(self.W("ws.get", t="count")["r"]["d"]["n"], 40 * 3 + 4 * 5)


class TestEconomy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import economy
        cls.E = economy
        cls.small = economy.default_config(households=300, firms=15, periods=60)

    def test_known_answers_of_the_engine(self):
        r = H("economy.known")
        self.assertTrue(r["r"]["pass"], r)
        self.assertGreaterEqual(len(r["r"]["tests"]), 7)

    def test_money_is_conserved_and_moments_are_sane(self):
        r = H("economy.run", d=self.small)
        self.assertTrue(r["ok"], r)
        self.assertLess(r["r"]["accounting_error"], 1e-9)
        m = r["r"]["moments"]
        self.assertTrue(0 <= m["unemployment"] <= 1)
        self.assertTrue(0 < m["cons_share"] < 1.2)
        self.assertTrue(0 <= m["wealth_gini"] < 1)

    def test_a_thousand_households(self):
        r = self.E.run(self.E.default_config(households=1000, firms=50, periods=40))
        self.assertEqual(r["households"], 1000)
        self.assertLess(r["accounting_error"], 1e-9)

    def test_rules_are_formulas_from_a_short_list(self):
        cfg = dict(self.small, rules={"consume": "min(w + y, 0.9 * y)"})
        self.assertTrue(H("economy.check", d=cfg)["r"]["pass"])
        self.assertNotEqual(H("economy.run", d=cfg)["r"]["moments"], H("economy.run", d=self.small)["r"]["moments"])
        for bad in ("__import__('os').getcwd()", "open('x')", "y.__class__", "[y for y in w]", "lambda: 1", "'a'"):
            r = H("economy.check", d=dict(self.small, rules={"consume": bad}))
            self.assertEqual(r["e"][0][0], 601, bad)
        r = H("economy.run", d=dict(self.small, params=dict(self.small["params"], tau=3)))
        self.assertEqual(r["e"][0][0], 602)

    def test_seeds_average_and_shocks_apply(self):
        r = H("economy.run", d=self.small, seeds=[1, 2], workers=1)
        self.assertEqual(r["r"]["runs"], 2)
        shocked = dict(self.small, shocks=[{"param": "g_share", "value": 0.3, "at": 20}])
        self.assertNotEqual(H("economy.run", d=shocked)["r"]["moments"], H("economy.run", d=self.small)["r"]["moments"])

    def test_other_entities_join_and_money_still_adds_up(self):
        cfg = dict(self.small, entities=[
            {"type": "foreign"}, {"type": "pension_fund", "count": 3}, {"type": "charity"},
            {"type": "custom", "name": "fund", "params": {"take": 2}, "flows": {"levy": "take", "pay": "0.5 * bal"},
             "pay_to": "employed"}])
        self.assertTrue(H("economy.check", d=cfg)["r"]["pass"])
        r = H("economy.run", d=cfg)
        self.assertTrue(r["ok"], r)
        self.assertLess(r["r"]["accounting_error"], 1e-9)
        ents = r["r"]["entities"]
        self.assertEqual(ents["pension_fund"]["count"], 3)
        self.assertGreater(ents["foreign"]["bought"], 0)
        self.assertAlmostEqual(ents["fund"]["levied"], 2 * self.small["periods"], places=6)
        self.assertNotEqual(r["r"]["moments"], H("economy.run", d=self.small)["r"]["moments"])
        self.assertIn("foreign", H("economy.entities")["r"]["types"])

    def test_every_behaviour_is_a_rule(self):
        rules = H("economy.rules")["r"]["rules"]
        for name in ("consume", "price", "wage", "policy", "plan", "expect", "dividend", "default", "purchases", "tax",
                     "benefit", "reservation"):
            self.assertIn(name, rules)
        base = H("economy.run", d=self.small)["r"]["moments"]
        for name, formula in (("purchases", "0"), ("dividend", "0"), ("tax", "0.1"), ("benefit", "0"),
                              ("plan", "exp_sales"), ("default", "t % 10 == 9")):
            r = H("economy.run", d=dict(self.small, rules={name: formula}))
            self.assertTrue(r["ok"], (name, r))
            self.assertLess(r["r"]["accounting_error"], 1e-9, name)
            self.assertNotEqual(r["r"]["moments"], base, name)

    def test_parameter_rules_changes_and_checks(self):
        cfg = dict(self.small, periods=60,
                   param_rules={"surcharge": "0.05 if debt > 0.65 else 0", "tau": "0.22 + surcharge"},
                   checks={"unemployment below 30%": "u < 0.3", "never": "u < 0"},
                   entities=[{"type": "custom", "name": "fund", "flows": {"levy": "100 * surcharge"}}],
                   changes=[{"at": 10, "add": [{"type": "foreign"}]},
                            {"at": 20, "rules": {"policy": "0.04"}, "params": {"g_share": 0.2}},
                            {"at": 30, "remove": ["foreign"]},
                            {"at": 40, "param_rules": {"benefit": "0.5 if u > 0.05 else 0.4"}}])
        self.assertTrue(H("economy.check", d=cfg)["r"]["pass"])
        r = self.E.run(cfg, series=True)
        self.assertLess(r["accounting_error"], 1e-9)
        self.assertEqual(r["changes_applied"], [10, 20, 30, 40])
        self.assertTrue(r["checks"]["unemployment below 30%"]["held"])
        self.assertEqual(r["checks"]["never"]["first"], 0)
        self.assertEqual(r["entities"]["foreign"]["removed_at"], 30)
        self.assertTrue(all(x == 0.04 for x in r["series"]["rate"][20:]))
        self.assertIsNone(r["series"]["param:benefit"][39])
        self.assertIsNotNone(r["series"]["param:benefit"][40])

    def test_bad_changes_are_refused(self):
        for bad in ({"param_rules": {"u": "1"}}, {"changes": [{"at": 999}]},
                    {"changes": [{"at": 5, "remove": ["ghost"]}]}, {"changes": [{"at": 5, "rules": {"policy": "open(1)"}}]},
                    {"changes": [{"at": 5, "params": {"tau": 5}}]}, {"checks": {"x": "w > 0"}}, {"period": "week"}):
            r = H("economy.check", d=dict(self.small, **bad))
            self.assertFalse(r["r"]["pass"], bad)

    def test_months_and_years(self):
        for period in ("month", "year"):
            r = H("economy.run", d=dict(self.small, period=period))
            self.assertTrue(r["ok"], r)
            self.assertLess(r["r"]["accounting_error"], 1e-9)

    def test_bad_entities_are_refused(self):
        for bad in ({"type": "dragon"}, {"type": "foreign", "count": 0},
                    {"type": "custom", "flows": {"levy": "__import__('os')"}},
                    {"type": "custom", "flows": {"steal": "1"}}, {"type": "custom", "pay_to": "nobody"},
                    {"type": "custom", "params": {"bal": 1}}):
            r = H("economy.check", d=dict(self.small, entities=[bad]))
            self.assertIn(r["e"][0][0], (601, 606), bad)
        r = H("economy.check", d=dict(self.small, entities=[{"type": "foreign", "params": {"export_share": 3}}]))
        self.assertEqual(r["e"][0][0], 602)
        r = H("economy.check", d=dict(self.small, entities=[{"type": "foreign"}, {"type": "foreign"}]))
        self.assertEqual(r["e"][0][0], 606)                      # two of one kind need their own names

    def test_extensions_can_add_entity_types(self):
        self.E.entity_type("exporter_union", "test kind", {"cut": (0.1, 0, 1, "share")}, {"levy": "cut * wages"})
        try:
            r = self.E.run(dict(self.small, entities=[{"type": "exporter_union"}]))
            self.assertGreater(r["entities"]["exporter_union"]["levied"], 0)
            self.assertLess(r["accounting_error"], 1e-9)
        finally:
            self.E.ENTITY_TYPES.pop("exporter_union", None)

    def test_an_economy_on_a_workspace_track(self):
        d = tempfile.mkdtemp()
        try:
            ws = os.path.join(d, "ws.db")
            S.handle({"op": "ws.track", "a": {"name": "eco", "d": self.small, "kind": "economy", "ws": ws}})
            r = S.handle({"op": "economy.run", "a": {"t": "eco", "ws": ws}})
            self.assertTrue(r["ok"], r)
            text = S.handle({"op": "ws.report", "a": {"t": "eco", "ws": ws}}, PERSON)["r"]["text"]
            self.assertIn("300 households", text)
        finally:
            import workspace
            for c in getattr(workspace._local, "conns", {}).values():
                c.close()
            workspace._local.conns = {}
            shutil.rmtree(d, ignore_errors=True)


def _toy(spec, states, seeds, workers):
    """A model whose training cases reward x up to 1, but whose hidden cases (seeds of 10000 and more) punish x > 0.5:
    a candidate that chases the training cases past 0.5 is overfitting."""
    out = []
    for s in states:
        x, y = s["params"]["x"], s["params"].get("y", 0.0)
        losses = [(x - 1) ** 2 + y ** 2 + (10 * max(0, x - 0.5) if sd >= 10000 else 0) for sd in seeds]
        out.append((sum(losses) / len(losses), {"x": x}, ""))
    return out


class TestEvolve(unittest.TestCase):
    def setUp(self):
        import evolve
        evolve.OBJECTIVES["toy"] = _toy
        self.dir = tempfile.mkdtemp()
        self.ws = os.path.join(self.dir, "ws.db")
        self.W("ws.track", name="toy", d={"params": {"x": 0.0, "y": 0.5}}, kind="toy")

    def tearDown(self):
        import workspace
        for c in getattr(workspace._local, "conns", {}).values():
            c.close()
        workspace._local.conns = {}
        shutil.rmtree(self.dir, ignore_errors=True)

    def W(self, op, ctx=None, **a):
        return S.handle({"op": op, "a": dict(a, ws=self.ws)}, ctx if ctx is not None else {"agent": "a1"})

    def start(self, **kw):
        r = self.W("evolve.start", name="s", t="toy", targets={"x": [1, 1]}, free={"x": [0, 1], "y": [0, 1]},
                   budget=kw.pop("budget", 400), pop=kw.pop("pop", 6), tolerance=0.2, **kw)
        self.assertTrue(r["ok"], r)

    def test_proposals_are_checked_against_the_study(self):
        self.start()
        self.assertEqual(self.W("evolve.propose", name="s", params={"z": 1})["e"][0][0], 701)
        self.assertEqual(self.W("evolve.propose", name="s", params={"x": 2})["e"][0][0], 701)
        self.assertEqual(self.W("evolve.propose", name="s", rules={"consume": "y"})["e"][0][0], 701)
        self.assertTrue(self.W("evolve.propose", name="s", params={"x": 0.4, "y": 0.1}, note="closer")["ok"])

    def test_the_loop_improves_and_refuses_overfitting(self):
        self.start()
        self.W("evolve.propose", name="s", params={"x": 0.45, "y": 0.0})
        self.W("evolve.propose", name="s", params={"x": 1.0, "y": 0.0})       # best on training, bad on hidden
        r = self.W("evolve.step", name="s")["r"]
        self.assertIn(3, r["overfit_refused"])
        self.assertEqual(r["champion"]["params"], {"x": 0.45, "y": 0.0})
        for _ in range(6):
            self.W("evolve.step", name="s")
        st = self.W("evolve.status", name="s")["r"]
        self.assertLessEqual(st["champion"]["params"]["x"], 0.55)   # never far past the limit the hidden cases set
        self.assertNotIn("hidden", json.dumps(st))                            # agents never see the hidden results
        self.assertIn("hidden_loss", self.W("evolve.status", PERSON, name="s")["r"]["champion"])   # people do
        self.assertEqual(self.W("ws.get", t="toy")["r"]["d"]["params"], st["champion"]["params"])
        text = self.W("ws.report", PERSON, t="toy")["r"]["text"]
        self.assertIn("refused because they did worse on the hidden cases", text)

    def test_people_freeze_pause_and_stop(self):
        self.start()
        self.W("ws.post", PERSON, kind="freeze", t="toy", b="y")
        self.assertEqual(self.W("evolve.propose", name="s", params={"y": 0.0})["e"][0][0], 502)
        self.W("evolve.step", name="s")
        for _ in range(3):
            self.W("evolve.step", name="s")
        self.assertEqual(self.W("ws.get", t="toy")["r"]["d"]["params"]["y"], 0.5)   # the loop leaves y alone too
        self.W("ws.post", PERSON, kind="pause", t="toy")
        self.assertEqual(self.W("evolve.step", name="s")["e"][0][0], 501)
        self.W("ws.post", PERSON, kind="resume", t="toy")
        self.assertEqual(self.W("evolve.stop", name="s")["e"][0][0], 104)           # agents cannot stop a study
        self.assertTrue(self.W("evolve.stop", PERSON, name="s")["ok"])
        self.assertEqual(self.W("evolve.step", name="s")["e"][0][0], 704)

    def test_budget(self):
        self.start(budget=10, pop=4)
        self.W("evolve.step", name="s")
        self.W("evolve.step", name="s")
        codes = [self.W("evolve.step", name="s").get("e", [[0]])[0][0] for _ in range(3)]
        self.assertIn(703, codes)

    def test_economy_study_runs(self):
        import economy
        cfg = economy.default_config(households=120, firms=8, periods=40)
        self.W("ws.track", name="eco", d=cfg, kind="economy")
        r = self.W("evolve.start", name="cal", t="eco", targets={"unemployment": [0.06, 1]},
                   free={"search": [1, 8], "res_decay": [0, 0.5]}, budget=60, pop=3, seeds=[1])
        self.assertTrue(r["ok"], r)
        r = self.W("evolve.step", name="cal", workers=1)
        self.assertTrue(r["ok"], r)
        self.assertIn("champion", r["r"])


class TestSwarm(unittest.TestCase):
    def test_a_small_swarm_with_a_person_stepping_in(self):
        d = tempfile.mkdtemp()
        try:
            report = os.path.join(d, "report.md")
            p = subprocess.run([sys.executable, os.path.join(TOOLS, "swarm.py"), "--agents", "20", "--households", "100",
                                "--firms", "8", "--periods", "30", "--rounds", "2", "--per-round", "8", "--pace", "0.05",
                                "--workers", "1", "--person-at", "1", "keep the tax rate", "--ws",
                                os.path.join(d, "ws.db"), "--report", report],
                               capture_output=True, text=True, timeout=600, cwd=ROOT)
            self.assertEqual(p.returncode, 0, p.stderr[-2000:])
            out = p.stdout
            for s in ("20 agents", "round 1:", "round 2:", "a person stepped in", "protocol messages", "champion"):
                self.assertIn(s, out)
            self.assertNotIn("agent error", out)
            with open(report, encoding="utf-8") as f:
                text = f.read()
            self.assertIn("Constraint: keep the tax rate", text)
            self.assertIn("Frozen: theta_w", text)
            self.assertIn("Improvement studies on this track", text)
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
