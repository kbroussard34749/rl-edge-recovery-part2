"""Check controller extraction using temporary training and retained policies.

Development training compares random draw order, updates, and serialized output
without replacing the final study. Saved final policies then exercise the new
evaluation layer against every retained evaluation episode and decision trace.
"""

import argparse
import csv
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests/reference"))
import recovery_reference as original
from edge_recovery.controllers import rule
from edge_recovery.evaluation import evaluate, score
from edge_recovery.scenarios import manifest, state_from
from edge_recovery.training import train


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_policy(path, convert):
    """Read the same portable policy into each implementation's State type."""
    return {
        convert(entry["state"]): entry["values"]
        for entry in json.loads(path.read_text())
    }


def verify():
    baseline = json.loads((ROOT / "docs/reference_manifest.json").read_text())
    expected_hash = next(
        x["sha256"] for x in baseline["tracked_reference_files"] if x["path"] == "recovery.py"
    )
    assert digest(ROOT / "tests/reference/recovery_reference.py") == expected_hash
    scenarios = manifest()
    runs = []
    # 601 episodes include full 200-episode bins and a final partial interval.
    # This is an extraction check, not the full 20,000-episode study budget.
    with TemporaryDirectory(prefix="rl-controller-check-") as directory:
        root = Path(directory)
        for filtered in (False, True):
            for alpha in (.1, .3):
                for seed in (100, 1000):
                    case = f"{filtered}-{alpha}-{seed}"
                    old_dir = root / case / "reference"
                    new_dir = root / case / "modular"
                    old_q, old_meta = original.train(scenarios, alpha, seed, filtered, 601, old_dir)
                    new_q, new_meta = train(scenarios, alpha, seed, filtered, 601, new_dir)
                    artifacts = ("episodes.csv", "curve.json", "policy.json")
                    assert all((old_dir / name).read_bytes() == (new_dir / name).read_bytes() for name in artifacts), case
                    variable = {"seconds", "process_peak_rss_bytes"}
                    assert {k: v for k, v in old_meta.items() if k not in variable} == {
                        k: v for k, v in new_meta.items() if k not in variable
                    }, case
                    assert len(old_q) == len(new_q)
                    # Fixed CPU and memory values identify the starting fault
                    # background; no validation or test starts enter training.
                    training_backgrounds = {
                        (state_from(x["initial"]).cpu, state_from(x["initial"]).mem)
                        for x in scenarios if x["split"] == "train"
                    }
                    assert all((state.cpu, state.mem) in training_backgrounds for state in new_q)
                    runs.append(dict(
                        filtered=filtered, alpha=alpha, seed=seed, episodes=601,
                        artifact_sha256={name: digest(new_dir / name) for name in artifacts},
                        q_states=new_meta["q_states"],
                    ))

    all_rows = []
    all_traces = []
    validation_score_checks = 0
    for controller in ("unshielded", "filtered"):
        for seed in range(1000, 1010):
            path = ROOT / "results/original_run/final" / controller / str(seed) / "policy.json"
            q = read_policy(path, state_from)
            reference_q = read_policy(path, original.state_from)
            # Evaluation must leave every saved value and table key untouched.
            before = json.dumps([dict(state=asdict(s), values=v) for s, v in q.items()])
            for split in ("test", "train"):
                rows, traces = evaluate(q, scenarios, controller, seed, split)
                expected_rows, expected_traces = original.evaluate(reference_q, scenarios, controller, seed, split)
                assert rows == expected_rows
                assert json.dumps(traces) == json.dumps(expected_traces)
                all_rows.extend(rows)
                all_traces.extend(traces)
            rows, traces = evaluate(q, scenarios, controller, seed, "validation", False)
            expected, _ = original.evaluate(reference_q, scenarios, controller, seed, "validation", False)
            assert rows == expected and traces == []
            assert score(rows) == original.score(expected)
            validation_score_checks += 1
            after = json.dumps([dict(state=asdict(s), values=v) for s, v in q.items()])
            assert before == after

    for split in ("test", "train"):
        rows, traces = evaluate({}, scenarios, "rule", None, split)
        expected_rows, expected_traces = original.evaluate({}, scenarios, "rule", None, split)
        assert rows == expected_rows
        assert json.dumps(traces) == json.dumps(expected_traces)
        all_rows.extend(rows)
        all_traces.extend(traces)

    with (ROOT / "results/original_run/evaluation.csv").open(newline="") as stream:
        retained_rows = list(csv.DictReader(stream))
    normalized_rows = [
        {key: "" if value is None else str(value) for key, value in row.items()}
        for row in all_rows
    ]
    assert normalized_rows == retained_rows
    rendered_traces = "".join(json.dumps(row) + "\n" for row in all_traces)
    assert rendered_traces == (ROOT / "results/original_run/traces.jsonl").read_text()
    # Test rule action selection on every retained decision state, not only the
    # decisions originally assigned to the deterministic baseline.
    rule_checks = 0
    for row in all_traces:
        state = state_from(row["state"])
        assert rule(state) == original.rule(original.state_from(row["state"]))
        rule_checks += 1

    retained = [x for x in baseline["tracked_reference_files"] if x["path"].startswith("outputs/")]
    assert all(digest(ROOT / x["path"].replace("outputs/", "results/original_run/", 1)) == x["sha256"] for x in retained)
    source = [
        "src/edge_recovery/controllers.py", "src/edge_recovery/training.py",
        "src/edge_recovery/evaluation.py", "src/edge_recovery/runtime.py",
        "tests/test_controllers.py", "scripts/verify_controller_equivalence.py",
    ]
    return dict(
        passed=True, reference_commit=baseline["reference_commit"],
        scope="Controller extraction; full experiment orchestration is pending",
        development_training_runs_per_implementation=len(runs),
        development_episodes_per_implementation=sum(x["episodes"] for x in runs),
        training_comparisons=runs,
        nonmatching_metadata_allowed=["seconds", "process_peak_rss_bytes"],
        retained_final_policies_evaluated=20, evaluation_rows_matched=len(all_rows),
        trace_rows_matched=len(all_traces), rule_action_comparisons=rule_checks,
        validation_score_comparisons=validation_score_checks,
        evaluated_policy_tables_unchanged=True, original_output_files_unchanged=len(retained),
        source_sha256={name: digest(ROOT / name) for name in source},
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    report = verify()
    text = json.dumps(report, indent=2) + "\n"
    if arguments.output:
        arguments.output.write_text(text)
    print(text)
