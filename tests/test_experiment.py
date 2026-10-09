"""Protect retained evidence and enforce selection before held-out evaluation."""

import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from edge_recovery.evidence import analyze
from edge_recovery.experiment import load_design, prepare_output, run
from edge_recovery.paths import ORIGINAL_RUN
from edge_recovery.policy_verification import verify_policy


class ExperimentTests(unittest.TestCase):
    def test_refuses_original_and_nested_destinations(self):
        for destination in (ORIGINAL_RUN, ORIGINAL_RUN / "nested"):
            with self.assertRaises(ValueError):
                prepare_output(destination)

    def test_refuses_existing_run_directory(self):
        with TemporaryDirectory() as directory:
            with self.assertRaises(FileExistsError):
                prepare_output(Path(directory))

    def test_original_analysis_and_policy_checks_are_read_only(self):
        with self.assertRaises(ValueError):
            analyze(ORIGINAL_RUN, write=True)
        with self.assertRaises(ValueError):
            verify_policy(ORIGINAL_RUN, write=True)

    def test_rejects_configuration_that_changes_fixed_model(self):
        config, _ = load_design()
        with TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(dict(config, gamma=.5)))
            with patch("edge_recovery.experiment.CONFIG_PATH", path):
                with self.assertRaises(ValueError):
                    load_design()

    def test_rejects_nonpositive_episode_budget(self):
        with TemporaryDirectory() as directory:
            for episodes in (0, -1):
                with self.assertRaises(ValueError):
                    run(Path(directory) / "invalid", episodes)

    def test_freeze_exists_before_first_heldout_evaluation(self):
        # Stub expensive learning to inspect orchestration order. These temporary
        # files test control flow only and are never scientific experiment data.
        with TemporaryDirectory() as directory:
            output = Path(directory) / "order-check"
            heldout_calls = []

            def training(*args):
                return {}, dict(seconds=0.)

            def evaluation(q, scenarios, controller, seed, split, trace=True):
                if split == "test":
                    frozen = json.loads((output / "frozen_protocol.json").read_text())
                    self.assertEqual(frozen["selection"], {"unshielded": .1, "filtered": .1})
                    self.assertTrue(frozen["frozen_before_test"])
                    heldout_calls.append((controller, seed))
                row = dict(controller=controller, seed=seed, split=split,
                           success=1, critical_unavailable=0, return_value=-2)
                return [row], []

            with patch("edge_recovery.experiment.train", training), patch(
                "edge_recovery.experiment.evaluate", evaluation
            ), patch("builtins.print"):
                run(output, episodes=1)
            self.assertEqual(len(heldout_calls), 21)
            self.assertEqual(json.loads((output / "run_identity.json").read_text())["run_kind"], "development")


if __name__ == "__main__":
    unittest.main()
