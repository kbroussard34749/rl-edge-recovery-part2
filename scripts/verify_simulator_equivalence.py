"""Compare modular simulation with the original code and retained traces.

This development check does not train, tune, or evaluate a new policy. It reads
the retained evidence and writes only the explicitly selected check report.
Run: python3 scripts/verify_simulator_equivalence.py --output docs/simulator_checks.json
"""

from collections import deque
from dataclasses import asdict, replace
from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests/reference"))
import recovery_reference as original
from edge_recovery import environment as model
from edge_recovery.safety_filter import step
from edge_recovery.scenarios import feasible, manifest, state_from


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_step(state, action, filtered):
    """Compare full transition semantics, not just success or total return."""
    reference = original.state_from(asdict(state))
    actual = step(state, action, filtered)
    expected = original.step(reference, action, filtered)
    assert asdict(actual[0]) == asdict(expected[0]), (state, action, filtered)
    assert actual[1:] == expected[1:], (state, action, filtered)
    return actual


def verify():
    baseline = json.loads((ROOT / "docs/reference_manifest.json").read_text())
    original_hash = next(
        entry["sha256"] for entry in baseline["tracked_reference_files"]
        if entry["path"] == "recovery.py"
    )
    assert digest(ROOT / "tests/reference/recovery_reference.py") == original_hash, "Reference code changed"
    assert model.ACTIONS == original.ACTIONS
    assert model.DEMAND == original.DEMAND
    scenarios = manifest()
    assert scenarios == original.manifest()
    # JSON serialization also checks retained ordering and representation.
    assert json.dumps(scenarios, indent=2) == (ROOT / "config/scenarios.json").read_text()
    audits = [dict(id=x["id"], **feasible(state_from(x["initial"]))) for x in scenarios]
    assert audits == json.loads((ROOT / "results/original_run/scenario_validation.json").read_text())

    # Explore physical states reachable under either condition, including unsafe
    # unshielded candidates. Budget variants exercise normal and final commands.
    queue = deque(state_from(x["initial"]) for x in scenarios)
    queue.extend([
        model.State((True,) * 3, (7, 0, 0), (0, 0, 0), (0, 1, 2), (True, False, True)),
        model.State((True,) * 3, (7, 0, 0), (0, 0, 8), (0, 1, 2), (True,) * 3),
        model.State((True,) * 3, (1, 0, 0), (0, 0, 0), (0, 0, 0), (True,) * 3),
    ])
    seen = set()
    transition_checks = 0
    step_checks = 0
    terminal_checks = 0
    while queue:
        state = replace(queue.popleft(), left=20)
        if state in seen:
            continue
        seen.add(state)
        reference = original.state_from(asdict(state))
        assert model.loads(state) == original.loads(reference)
        assert model.physical(state) == original.physical(reference)
        assert model.available(state) == original.available(reference)
        assert model.success(state) == original.success(reference)
        for left in (20, 2, 1):
            current = replace(state, left=left)
            reference = original.state_from(asdict(current))
            for action in range(9):
                actual = model.transition(current, action)
                expected = original.transition(reference, action)
                assert asdict(actual[0]) == asdict(expected[0])
                assert actual[1:] == expected[1:]
                transition_checks += 1
                for filtered in (False, True):
                    if model.success(current):
                        try:
                            step(current, action, filtered)
                        except ValueError:
                            terminal_checks += 1
                        else:
                            raise AssertionError("Accepted a terminal state")
                    else:
                        after, _, _, _ = compare_step(current, action, filtered)
                        step_checks += 1
                        if left == 20:
                            queue.append(after)

    trace_checks = 0
    with (ROOT / "results/original_run/traces.jsonl").open() as stream:
        for line in stream:
            row = json.loads(line)
            state = state_from(row["state"])
            action = model.ACTIONS.index(row["proposed"])
            after, reward, done, info = compare_step(state, action, row["controller"] == "filtered")
            # Rule traces have no prohibited proposals; this preserves their
            # actual recorded behavior without assuming a filter advantage.
            assert asdict(after) == asdict(state_from(row["next_state"]))
            assert reward == row["reward"]
            assert done == bool(row["success"] or after.left == 0)
            assert info == {key: row[key] for key in info}
            trace_checks += 1

    retained = [
        entry for entry in baseline["tracked_reference_files"]
        if entry["path"].startswith("outputs/")
    ]
    assert all(digest(ROOT / entry["path"].replace("outputs/", "results/original_run/", 1)) == entry["sha256"] for entry in retained)
    checked_source = [
        "src/edge_recovery/environment.py", "src/edge_recovery/safety_filter.py",
        "src/edge_recovery/scenarios.py", "tests/test_simulator.py",
        "scripts/verify_simulator_equivalence.py",
    ]
    return dict(
        passed=True, scope="Simulator extraction; no refactored controller or training run",
        reference_commit=baseline["reference_commit"], scenarios=len(scenarios),
        manifest_serialization_identical=True, feasibility_records_identical=True,
        reachable_physical_states=len(seen), transition_comparisons=transition_checks,
        step_comparisons=step_checks, successful_terminal_rejections=terminal_checks,
        retained_trace_replays=trace_checks, original_output_files_unchanged=len(retained),
        source_sha256={name: digest(ROOT / name) for name in checked_source},
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
