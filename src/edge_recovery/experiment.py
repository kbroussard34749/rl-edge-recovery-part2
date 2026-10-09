"""Run the frozen Part 1 experiment in a fresh, isolated output directory.

The order matters: validate scenarios, measure the pilot, compare validation
scores, save the selected settings, and only then evaluate final policies on
held-out starts. Configuration snapshots and source hashes identify each run.
The experiment preserves the original seed order and random draw sequence.
"""

import csv
import hashlib
import json
from pathlib import Path
import platform
import time

from .environment import ACTIONS, success
from .evaluation import evaluate, score
from .paths import CONFIG_PATH, ROOT, SCENARIOS_PATH, protect_original
from .runtime import peak_rss_bytes
from .scenarios import feasible, manifest, state_from
from .training import train


def load_design() -> tuple:
    """Read and validate the retained experiment design before execution.

    Some simulator and training constants are intentionally fixed. Reject a
    configuration that changes them rather than silently running another design.
    Algorithm revisions require a separately specified experiment.
    """
    config = json.loads(CONFIG_PATH.read_text())
    expected = dict(
        episodes=20000, gamma=.95, alphas=[.1, .3],
        tuning_seeds=list(range(100, 105)), final_seeds=list(range(1000, 1010)),
        epsilon_initial=1., epsilon_final=.1, decay_fraction=.8,
        budget=20, capacity=10, tie_break=list(ACTIONS),
        rng="Python random.Random", state="exact tuple including remaining budget",
        heldout_tuning=False,
    )
    if config != expected:
        raise ValueError("Configuration differs from the frozen design")
    scenarios = json.loads(SCENARIOS_PATH.read_text())
    # JSON restores tuple fields as lists; compare the serialized representation.
    if scenarios != json.loads(json.dumps(manifest())):
        raise ValueError("Scenario manifest differs from the frozen design")
    return config, scenarios


def prepare_output(destination: Path) -> Path:
    """Create a new run directory; never reuse a partial or completed run."""
    destination = destination.resolve()
    protect_original(destination)
    if destination.exists():
        raise FileExistsError("Output already exists; choose a new run directory")
    destination.mkdir(parents=True)
    return destination


def write_csv(path: Path, rows: list):
    """Preserve original field order and CSV serialization for comparisons."""
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(destination: Path, episodes: int = 20000) -> dict:
    """Execute the protocol and return provenance for the completed run.

    An explicit smaller episode count supports development checks. Such a run
    keeps the original split and seed design but is labeled development in its
    separate identity record. It cannot replace full-budget evidence.
    """
    if episodes <= 0:
        raise ValueError("Episode count must be positive")
    config, scenarios = load_design()
    config = dict(config, episodes=episodes)
    audit = [dict(id=x["id"], **feasible(state_from(x["initial"]))) for x in scenarios]
    if not all(
        result["feasible"] and success(state_from(scenarios[index]["before"]))
        for index, result in enumerate(audit)
    ):
        raise AssertionError("Invalid manifest")
    out = prepare_output(destination)
    # Snapshots belong to this run, leaving source configuration untouched.
    (out / "config.json").write_text(json.dumps(config, indent=2))
    (out / "scenarios.json").write_text(json.dumps(scenarios, indent=2))
    (out / "scenario_validation.json").write_text(json.dumps(audit, indent=2))
    started = time.perf_counter()
    pilots = []
    for controller in ("unshielded", "filtered"):
        _, metadata = train(
            scenarios, .1, 7, controller == "filtered", 1000,
            out / "pilot" / controller,
        )
        pilots.append(dict(controller=controller, **metadata))
    (out / "pilot.json").write_text(json.dumps(pilots, indent=2))
    print("PILOT", json.dumps(pilots), flush=True)

    tuning_rows = []
    selection = {}
    for controller in ("unshielded", "filtered"):
        candidates = []
        for alpha in config["alphas"]:
            pooled = []
            for seed in config["tuning_seeds"]:
                q, metadata = train(
                    scenarios, alpha, seed, controller == "filtered", episodes,
                    out / "tuning" / controller / str(alpha) / str(seed),
                )
                rows, _ = evaluate(q, scenarios, controller, seed, "validation", False)
                pooled += rows
                tuning_rows += rows
                print("TUNED", controller, alpha, seed, round(metadata["seconds"], 2), flush=True)
            candidates.append((score(pooled), alpha))
        # The candidate list puts .1 first; max retains it on an exact score tie.
        selection[controller] = max(candidates, key=lambda item: item[0])[1]
    write_csv(out / "validation.csv", tuning_rows)
    frozen = dict(
        config=config, selection=selection,
        scenario_sha256=hashlib.sha256((out / "scenarios.json").read_bytes()).hexdigest(),
        selection_rule="mean success, then lower critical outage, then return; alpha .1 wins exact tie",
        frozen_before_test=True,
    )
    # Save the selection before any final held-out policy evaluation occurs.
    (out / "frozen_protocol.json").write_text(json.dumps(frozen, indent=2))
    results = []
    traces = []
    for controller in ("unshielded", "filtered"):
        for seed in config["final_seeds"]:
            q, metadata = train(
                scenarios, selection[controller], seed, controller == "filtered",
                episodes, out / "final" / controller / str(seed),
            )
            for split in ("test", "train"):
                rows, decisions = evaluate(q, scenarios, controller, seed, split)
                results += rows
                traces += decisions
            print("FINAL", controller, seed, round(metadata["seconds"], 2), flush=True)
    # Repeat-free rule evaluation supplies one deterministic episode per start.
    for split in ("test", "train"):
        rows, decisions = evaluate({}, scenarios, "rule", None, split)
        results += rows
        traces += decisions
    write_csv(out / "evaluation.csv", results)
    with (out / "traces.jsonl").open("w") as stream:
        for row in traces:
            stream.write(json.dumps(row) + "\n")
    provenance = dict(
        python=platform.python_version(), platform=platform.platform(),
        total_seconds=time.perf_counter() - started,
        total_planned_training_episodes=40 * episodes, pilot_episodes=2000,
        process_peak_rss=peak_rss_bytes(),
        peak_memory_scope="whole experiment process including transition caches; not isolated per learner",
        submission_performed=False, publication_performed=False,
    )
    (out / "provenance.json").write_text(json.dumps(provenance, indent=2))
    # Keep extra execution identity separate so original evidence formats match.
    source = sorted((ROOT / "src/edge_recovery").glob("*.py"))
    identity = dict(
        status="completed", run_kind="full_reproduction" if episodes == 20000 else "development",
        source_sha256={str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in source},
        config_sha256=hashlib.sha256((out / "config.json").read_bytes()).hexdigest(),
        scenario_sha256=frozen["scenario_sha256"],
    )
    (out / "run_identity.json").write_text(json.dumps(identity, indent=2))
    print("COMPLETE", json.dumps(provenance), flush=True)
    return provenance
