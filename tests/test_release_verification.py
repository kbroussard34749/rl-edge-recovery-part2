"""Preserve strict chronology while distinguishing archive-byte verification."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = spec_from_file_location("release_verifier", ROOT / "scripts/verify_reproduction.py")
verifier = module_from_spec(spec)
spec.loader.exec_module(verifier)


class ReleaseVerificationTests(unittest.TestCase):
    def test_archive_mode_does_not_claim_execution_order(self):
        original_stat = Path.stat

        def reassigned_timestamp(path, *args, **kwargs):
            if path.name == "frozen_protocol.json":
                return SimpleNamespace(st_mtime_ns=10**30)
            return original_stat(path, *args, **kwargs)

        run = ROOT / "results/reproductions/full_2026-10-09"
        with patch.object(Path, "stat", reassigned_timestamp):
            with self.assertRaisesRegex(AssertionError, "File chronology unavailable"):
                verifier.verify(run)
            result = verifier.verify(run, archived_checkout=True)
        self.assertTrue(result["passed"])
        self.assertIsNone(result["freeze_precedes_final_policy_files"])
        self.assertEqual(result["chronology_check_mode"], "not_established_from_archived_timestamps")
        self.assertEqual(result["exact_artifact_matches"], 136)
        self.assertTrue(result["checked_source_hashes_match"])


if __name__ == "__main__":
    unittest.main()
