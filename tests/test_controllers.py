"""Check learning bookkeeping, fixed ties, and evaluation boundaries."""

from dataclasses import replace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from edge_recovery.controllers import greedy, update
from edge_recovery.environment import State
from edge_recovery.evaluation import evaluate, score
from edge_recovery.safety_filter import step
from edge_recovery.scenarios import manifest, state_from


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.state = State(
            (True,) * 3, (0, 0, 0), (0, 0, 0), (0, 1, 2), (True, False, True),
        )

    def test_greedy_tie_and_unique_maximum(self):
        self.assertEqual(greedy([0.] * 9), 0)
        self.assertEqual(greedy([-2, 3, 3, 0, 0, 0, 0, 0, 0]), 1)
        self.assertEqual(greedy([-2, 0, 0, 0, 0, 0, 0, 4, 0]), 7)

    def test_nonterminal_target_uses_future_value(self):
        following = replace(self.state, left=19)
        q = {self.state: [4.] + [0.] * 8, following: [10.] * 9}
        update(q, self.state, 0, -2, following, False, .1)
        self.assertAlmostEqual(q[self.state][0], 4.35)
        self.assertEqual(q[following], [10.] * 9)

    def test_terminal_target_ignores_future_values(self):
        following = replace(self.state, running=(True,) * 3, left=0)
        q = {following: [100.] * 9}
        update(q, self.state, 6, -2, following, True, 1.)
        self.assertEqual(q[self.state][6], -2)

    def test_blocked_command_updates_proposal_not_wait(self):
        state = replace(self.state, cpu=(7, 0, 0))
        following, reward, done, info = step(state, 5, True)
        self.assertEqual(info["executed"], "wait")
        q = {}
        update(q, state, 5, reward, following, done, .1)
        self.assertEqual(q[state][5], -2.6)
        self.assertEqual(q[state][8], 0)

    def test_rule_recovers_all_heldout_starts_once(self):
        rows, traces = evaluate({}, manifest(), "rule", None, "test")
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(row["success"] == 1 for row in rows))
        self.assertTrue(all(row["unseen"] == 0 for row in rows))
        self.assertTrue(all(row["violations"] == 0 for row in rows))
        self.assertEqual(len(traces), 12)

    def test_unseen_restart_failure_does_not_change_table(self):
        scenario = next(x for x in manifest() if x["id"] == "cpu_4")
        q = {}
        rows, traces = evaluate(q, [scenario], "filtered", 1000, "test")
        self.assertEqual(q, {})
        self.assertEqual((rows[0]["success"], rows[0]["steps"], rows[0]["unseen"]), (0, 20, 20))
        self.assertTrue(all(row["proposed"] == "restart" for row in traces))

    def test_requested_split_and_optional_traces(self):
        rows, traces = evaluate({}, manifest(), "unshielded", 1000, "validation", False)
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(row["split"] == "validation" for row in rows))
        self.assertEqual(traces, [])

    def test_validation_priority_and_score_sign(self):
        good = [dict(success=1, critical_unavailable=10, return_value=-100)]
        failed = [dict(success=0, critical_unavailable=0, return_value=0)]
        self.assertGreater(score(good), score(failed))
        self.assertEqual(score(good), (1., -10., -100.))


if __name__ == "__main__":
    unittest.main()
