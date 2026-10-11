"""Check demo evidence fidelity, fixture separation, and local HTTP behavior."""

import csv
from dataclasses import replace
import hashlib
from http.client import HTTPConnection
import json
from pathlib import Path
import sys
import threading
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from edge_recovery.demo import boundary_fixture, run_episode
from edge_recovery.demo_web import make_server
from edge_recovery.paths import ORIGINAL_RUN
from edge_recovery.scenarios import state_from


class DemoTests(unittest.TestCase):
    def test_all_retained_final_episodes_and_decisions_match(self):
        """Compare 420 episodes and 2,832 decisions, not just success totals."""
        with (ORIGINAL_RUN / "evaluation.csv").open(newline="") as source:
            rows = list(csv.DictReader(source))
        traces = [json.loads(line) for line in (ORIGINAL_RUN / "traces.jsonl").read_text().splitlines()]
        groups = {}
        for trace in traces:
            key = (trace["controller"], str(trace["seed"]), trace["scenario"])
            groups.setdefault(key, []).append(trace)
        self.assertEqual(len(rows), 420)
        self.assertEqual(len(traces), 2832)
        for row in rows:
            seed = int(row["seed"]) if row["controller"] != "rule" else 1000
            episode = run_episode(row["controller"], row["scenario"], seed)
            for field, value in episode["summary"].items():
                if field == "seed" and row["controller"] == "rule":
                    continue  # Demo seed selects learner policy; baseline is deterministic.
                self.assertEqual(str(value), row[field], (row["scenario"], field))
            reference_seed = "None" if row["controller"] == "rule" else row["seed"]
            expected = groups[(row["controller"], reference_seed, row["scenario"])]
            actual = []
            for trace in episode["trace"]:
                audit = {k: v for k, v in trace.items() if k not in ("loads", "availability", "seen")}
                if row["controller"] == "rule":
                    audit["seed"] = None
                actual.append(json.loads(json.dumps(audit)))
            self.assertEqual(actual, expected)

    def test_presentation_cases_and_training_coverage(self):
        learned = run_episode("filtered", "node_0")
        failed = run_episode("filtered", "cpu_4")
        baseline = run_episode("rule", "cpu_4")
        self.assertEqual((learned["summary"]["success"], learned["summary"]["steps"]), (1, 3))
        self.assertTrue(all(t["seen"] for t in learned["trace"]))
        self.assertEqual((failed["summary"]["success"], failed["summary"]["steps"]), (0, 20))
        self.assertTrue(all(not t["seen"] and t["proposed"] == "restart" for t in failed["trace"]))
        self.assertEqual((baseline["summary"]["success"], baseline["summary"]["steps"]), (1, 1))
        self.assertTrue(all(t["seen"] is None for t in baseline["trace"]))

    def test_boundary_records_preserve_original_and_do_not_claim_recovery(self):
        records = boundary_fixture()
        text = "\n".join(json.dumps(row, indent=2) for row in records) + "\n"
        self.assertEqual(text, (ORIGINAL_RUN / "boundary_demo.json.txt").read_text())
        unfiltered, filtered = records
        self.assertEqual((unfiltered["violations"], filtered["violations"]), (1, 0))
        self.assertEqual((filtered["executed"], filtered["reward"], filtered["success"]), ("wait", -26, 0))
        self.assertEqual(state_from(filtered["after"]), replace(state_from(filtered["before"]), left=19))
        self.assertTrue(all("NOT held-out" in r["fixture"] for r in records))

    def test_invalid_inputs_rejected_before_policy_loading(self):
        for arguments in [("unknown", "cpu_4", 1000), ("filtered", "../../plan", 1000), ("filtered", "cpu_4", 0)]:
            with self.assertRaises(ValueError):
                run_episode(*arguments)

    def test_demo_does_not_write_retained_evidence(self):
        def hashes():
            return {p.relative_to(ORIGINAL_RUN).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in ORIGINAL_RUN.rglob("*") if p.is_file()}
        before = hashes()
        run_episode("filtered", "cpu_4")
        boundary_fixture()
        self.assertEqual(hashes(), before)

    def test_http_endpoints_and_loopback_binding(self):
        with make_server(0) as server:
            self.assertEqual(server.server_address[0], "127.0.0.1")
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            try:
                connection = HTTPConnection(*server.server_address, timeout=5)
                for path, expected in [("/", 200), ("/scenarios", 200), ("/run?controller=rule&scenario=cpu_4", 200),
                                       ("/run?seed=bad", 400), ("/run?scenario=missing", 400), ("/run?controller=bad", 400),
                                       ("/run?seed=999", 400), ("/missing", 404)]:
                    connection.request("GET", path)
                    response = connection.getresponse()
                    body = response.read()
                    self.assertEqual(response.status, expected, path)
                    if path == "/scenarios":
                        self.assertEqual(len(json.loads(body)), 24)
                    if path.startswith("/run?controller=rule"):
                        self.assertEqual(json.loads(body)["summary"]["success"], 1)
                connection.close()
            finally:
                server.shutdown()
                worker.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
