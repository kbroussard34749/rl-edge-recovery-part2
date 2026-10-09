"""Compare a full reproduction with the original scientific artifacts.

Equality covers policies, episode histories, curves, selection, evaluation and
analysis. Runtime and cumulative process memory are compared separately because
they depend on execution history. Historical logs remain original records.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import _bootstrap
from edge_recovery.evaluation import evaluate, score
from edge_recovery.paths import CONFIG_PATH, ORIGINAL_RUN, ROOT, SCENARIOS_PATH
from edge_recovery.scenarios import state_from


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(run_dir: Path) -> dict:
    """Prove the full budget and retained-artifact identity at this run path."""
    run_dir = run_dir.resolve()
    baseline = json.loads((ROOT / "docs/reference_manifest.json").read_text())
    for item in baseline["tracked_reference_files"]:
        if item["path"].startswith("outputs/"):
            relocated = ORIGINAL_RUN / item["path"].removeprefix("outputs/")
            assert digest(relocated) == item["sha256"], item["path"]

    identity = json.loads((run_dir / "run_identity.json").read_text())
    assert identity["status"] == "completed" and identity["run_kind"] == "full_reproduction"
    for name, expected in identity["source_sha256"].items():
        assert digest(ROOT / name) == expected, ("Source changed since execution", name)
    assert digest(run_dir / "config.json") == identity["config_sha256"] == digest(CONFIG_PATH)
    assert digest(run_dir / "scenarios.json") == identity["scenario_sha256"] == digest(SCENARIOS_PATH)

    exact = []
    timing_differences = []
    histories = sorted(ORIGINAL_RUN.glob("**/episodes.csv"))
    assert len(histories) == 42
    total_episodes = 0
    pilot_episodes = 0
    for history in histories:
        relative = history.relative_to(ORIGINAL_RUN)
        folder = relative.parent
        for filename in ("episodes.csv", "curve.json", "policy.json"):
            old = ORIGINAL_RUN / folder / filename
            new = run_dir / folder / filename
            assert old.read_bytes() == new.read_bytes(), str(folder / filename)
            exact.append(dict(path=str(folder / filename), sha256=digest(new)))
        old = json.loads((ORIGINAL_RUN / folder / "training.json").read_text())
        new = json.loads((run_dir / folder / "training.json").read_text())
        variable = {"seconds", "process_peak_rss_bytes"}
        assert {key: value for key, value in old.items() if key not in variable} == {
            key: value for key, value in new.items() if key not in variable
        }, str(folder)
        with (run_dir / folder / "episodes.csv").open(newline="") as stream:
            rows = list(csv.DictReader(stream))
        assert len(rows) == new["episodes"]
        assert [int(row["episode"]) for row in rows] == list(range(1, new["episodes"] + 1))
        if relative.parts[0] == "pilot":
            pilot_episodes += len(rows)
        else:
            total_episodes += len(rows)
        timing_differences.append(dict(
            path=str(folder / "training.json"),
            original={key: old[key] for key in sorted(variable)},
            reproduction={key: new[key] for key in sorted(variable)},
        ))
    assert (total_episodes, pilot_episodes) == (800000, 2000)

    stable = (
        "scenario_validation.json", "frozen_protocol.json", "validation.csv",
        "evaluation.csv", "traces.jsonl", "seed_aggregates.json", "summary.json",
        "per_fault.json", "evidence_checks.json", "policy_checks.json",
    )
    for filename in stable:
        assert (ORIGINAL_RUN / filename).read_bytes() == (run_dir / filename).read_bytes(), filename
        exact.append(dict(path=filename, sha256=digest(run_dir / filename)))

    old_pilot = json.loads((ORIGINAL_RUN / "pilot.json").read_text())
    new_pilot = json.loads((run_dir / "pilot.json").read_text())
    variable = {"seconds", "process_peak_rss_bytes"}
    assert [{k: v for k, v in item.items() if k not in variable} for item in old_pilot] == [
        {k: v for k, v in item.items() if k not in variable} for item in new_pilot
    ]
    old_provenance = json.loads((ORIGINAL_RUN / "provenance.json").read_text())
    new_provenance = json.loads((run_dir / "provenance.json").read_text())
    variable = {"total_seconds", "process_peak_rss"}
    assert {k: v for k, v in old_provenance.items() if k not in variable} == {
        k: v for k, v in new_provenance.items() if k not in variable
    }

    # Independently derive the alpha selection from all saved tuning policies.
    # This also recovers the alpha dimension absent from the pooled validation CSV.
    config = json.loads((run_dir / "config.json").read_text())
    scenarios = json.loads((run_dir / "scenarios.json").read_text())
    frozen = json.loads((run_dir / "frozen_protocol.json").read_text())
    expected_validation = []
    selection = {}
    scores = {}
    for controller in ("unshielded", "filtered"):
        candidates = []
        for alpha in config["alphas"]:
            pooled = []
            for seed in config["tuning_seeds"]:
                path = run_dir / "tuning" / controller / str(alpha) / str(seed) / "policy.json"
                q = {state_from(x["state"]): x["values"] for x in json.loads(path.read_text())}
                rows, _ = evaluate(q, scenarios, controller, seed, "validation", False)
                pooled.extend(rows)
                expected_validation.extend(rows)
            candidates.append((score(pooled), alpha))
        selection[controller] = max(candidates, key=lambda item: item[0])[1]
        scores[controller] = [dict(alpha=alpha, score=values) for values, alpha in candidates]
    assert selection == frozen["selection"] == {"unshielded": .1, "filtered": .1}
    with (run_dir / "validation.csv").open(newline="") as stream:
        saved = list(csv.DictReader(stream))
    assert [{k: str(v) for k, v in row.items()} for row in expected_validation] == saved
    freeze_time = (run_dir / "frozen_protocol.json").stat().st_mtime_ns
    assert all(freeze_time <= path.stat().st_mtime_ns for path in (run_dir / "final").glob("*/*/policy.json"))
    assert freeze_time <= (run_dir / "evaluation.csv").stat().st_mtime_ns
    return dict(
        passed=True, reference_commit=baseline["reference_commit"],
        run_path=str(run_dir.relative_to(ROOT)), original_output_files_preserved=187,
        model_runs=42, training_episodes=total_episodes, pilot_episodes=pilot_episodes,
        exact_artifact_matches=len(exact), exact_artifacts=exact,
        configuration_snapshots_match=True, checked_source_hashes_match=True,
        training_metadata_scientific_fields_match=True,
        training_metadata_timing_and_memory=timing_differences,
        original_provenance=old_provenance, reproduction_provenance=new_provenance,
        selected_alpha=selection, validation_scores=scores, validation_rows_verified=len(saved),
        freeze_precedes_final_policy_files=True,
        analysis_and_policy_records_match=True,
        excluded_original_records="Historical execution/test logs and demonstration text exports remain preserved originals; they are not reproduction equivalence targets.",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    result = verify(arguments.run_dir)
    arguments.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in (
        "passed", "model_runs", "training_episodes", "pilot_episodes",
        "exact_artifact_matches", "selected_alpha", "validation_rows_verified",
    )}, indent=2))
