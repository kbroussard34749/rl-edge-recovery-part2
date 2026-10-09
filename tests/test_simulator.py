"""Independent simulator boundary assertions for the modular implementation.

Run from the repository root: python3 -m unittest discover -s tests -v.
The src bootstrap supports this intermediate gate before package installation.
"""

from dataclasses import replace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from edge_recovery.environment import State, available, loads, success
from edge_recovery.safety_filter import step
from edge_recovery.scenarios import feasible, manifest, state_from


class SimulatorTests(unittest.TestCase):
    def setUp(self):
        self.state = State(
            (True,) * 3, (0, 0, 0), (0, 0, 0), (0, 0, 0), (True,) * 3,
        )

    def test_capacity_equality_and_throttle(self):
        self.assertTrue(success(replace(self.state, cpu=(1, 0, 0))))
        overloaded = replace(self.state, cpu=(2, 0, 0))
        self.assertFalse(success(overloaded))
        after, reward, done, _ = step(overloaded, 1, True)
        self.assertEqual(loads(after), ((10, 0, 0), (9, 0, 0)))
        self.assertEqual(reward, -3)
        self.assertTrue(done)

    def test_dependency_and_wait_cost(self):
        state = replace(self.state, place=(0, 1, 2), running=(True, False, True))
        self.assertEqual(available(state), (False, False, True))
        self.assertEqual(step(state, 8, True)[1], -21)

    def test_blocked_proposal_and_unshielded_execution(self):
        state = replace(
            self.state, place=(0, 1, 2), running=(True, False, True), cpu=(7, 0, 0),
        )
        after, reward, _, info = step(state, 5, True)
        self.assertEqual(after, replace(state, left=19))
        self.assertEqual(reward, -26)
        self.assertEqual((info["proposed"], info["executed"]), ("restore_N1", "wait"))
        self.assertEqual((info["replaced"], info["violations"]), (1, 0))
        unshielded, _, _, unshielded_info = step(state, 5, False)
        self.assertTrue(unshielded.running[1])
        self.assertEqual(unshielded_info["violations"], 1)

    def test_failed_node_restore_and_invalid_migration(self):
        state = replace(self.state, health=(False, True, True))
        after, _, _, info = step(state, 6, True)
        self.assertEqual(after.place[1], 1)
        self.assertFalse(after.health[0])
        self.assertEqual(info["cost"], 3)
        invalid, _, _, invalid_info = step(state, 3, True)
        self.assertEqual(invalid, replace(state, left=19))
        self.assertEqual((invalid_info["invalid"], invalid_info["prohibited"]), (1, 0))

    def test_memory_overload_requires_placement_change(self):
        state = replace(self.state, mem=(2, 0, 0))
        after, _, done, _ = step(state, 3, True)
        self.assertTrue(done)
        self.assertTrue(success(after))
        self.assertEqual(after.place[1], 1)

    def test_last_command_success_and_budget_exhaustion(self):
        state = replace(self.state, running=(False, True, True), left=1)
        _, reward, done, info = step(state, 0, True)
        self.assertEqual(reward, -2)
        self.assertTrue(done)
        self.assertEqual(info["success"], 1)
        exhausted, reward, done, info = step(state, 8, True)
        self.assertEqual(reward, -31)
        self.assertTrue(done)
        self.assertEqual(info["success"], 0)
        with self.assertRaises(ValueError):
            step(exhausted, 8, True)

    def test_preserves_available_critical_service(self):
        state = replace(self.state, place=(0, 1, 2), cpu=(7, 0, 0), mem=(0, 0, 8))
        after, _, _, info = step(state, 2, True)
        self.assertEqual(info["replaced"], 1)
        self.assertTrue(available(after)[0])

    def test_all_faults_in_all_splits_and_feasible_starts(self):
        scenarios = manifest()
        self.assertEqual(len(scenarios), 24)
        for fault in ("crash", "cpu", "memory", "node"):
            counts = [
                sum(x["fault"] == fault and x["split"] == split for x in scenarios)
                for split in ("train", "validation", "test")
            ]
            self.assertEqual(counts, [3, 1, 2])
        self.assertEqual(len({state_from(x["initial"]) for x in scenarios}), 24)
        for scenario in scenarios:
            initial = state_from(scenario["initial"])
            self.assertTrue(success(state_from(scenario["before"])))
            self.assertFalse(success(initial))
            self.assertTrue(feasible(initial)["feasible"])


if __name__ == "__main__":
    unittest.main()
