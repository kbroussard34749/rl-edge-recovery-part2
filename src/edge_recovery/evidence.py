"""Summarize recovery evidence and reconcile every saved evaluation decision.

Episode metrics are first summarized within each seed, then across seeds.
The deterministic baseline is evaluated once per configuration. Variability
across seeds is descriptive and does not remove scenario-selection uncertainty.
"""

import csv
import json
from pathlib import Path
import statistics

from .controllers import rule
from .environment import ACTIONS
from .paths import protect_original
from .safety_filter import step
from .scenarios import state_from

FIELDS = [
    "success", "steps", "return_value", "critical_unavailable", "batch_unavailable",
    "throttled", "cost", "prohibited", "violations", "replaced", "invalid", "unseen",
]
SUMMARY_FIELDS = (
    "success_rate", "steps_mean", "return_value_mean", "critical_unavailable_mean",
    "violations_mean", "prohibited_mean", "unseen_fraction", "filter_intervention_rate",
)


def analyze(run_dir: Path, write: bool = False) -> dict:
    """Return summaries after replay checks; optionally write to a new run.

    With write=False this reads original evidence without modifying it. Outage
    metrics count service-decision intervals rather than clock time. This does
    not test significance, convergence, or population generalization.
    """
    run_dir = run_dir.resolve()
    if write:
        protect_original(run_dir)
    with (run_dir / "evaluation.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        for field in FIELDS:
            row[field] = float(row[field])

    # Summarize within each seed first. Success-only steps retain a denominator
    # separate from all-episode steps, which include budget-exhaustion failures.
    aggregates = []
    keys = sorted(set((row["controller"], row["seed"], row["split"]) for row in rows))
    for controller, seed, split in keys:
        group = [row for row in rows if
                 (row["controller"], row["seed"], row["split"]) == (controller, seed, split)]
        recovered = [row for row in group if row["success"]]
        aggregate = dict(
            controller=controller, seed=seed, split=split, episodes=len(group),
            success_count=len(recovered), success_rate=len(recovered) / len(group),
            successful_steps=statistics.mean(row["steps"] for row in recovered) if recovered else None,
        )
        for field in FIELDS[1:]:
            aggregate[field + "_mean"] = statistics.mean(row[field] for row in group)
        decisions = sum(row["steps"] for row in group)
        aggregate["unseen_fraction"] = sum(row["unseen"] for row in group) / decisions
        aggregate["filter_intervention_rate"] = sum(row["replaced"] for row in group) / decisions
        aggregates.append(aggregate)

    # Across-seed spread describes these runs. The single deterministic rule
    # evaluation has no across-seed SD; store None rather than invent variation.
    summary = []
    for controller, split in sorted(set((row["controller"], row["split"]) for row in rows)):
        group = [row for row in aggregates if row["controller"] == controller and row["split"] == split]
        item = dict(controller=controller, split=split, seeds=len(group),
                    configurations_per_seed=group[0]["episodes"])
        for field in SUMMARY_FIELDS:
            values = [row[field] for row in group]
            item[field] = dict(
                mean=statistics.mean(values), sd=statistics.stdev(values) if len(values) > 1 else None,
                min=min(values), max=max(values),
            )
        summary.append(item)

    fault_rows = []
    keys = sorted(set((row["controller"], row["split"], row["fault"]) for row in rows))
    for controller, split, fault in keys:
        group = [row for row in rows if
                 (row["controller"], row["split"], row["fault"]) == (controller, split, fault)]
        seeds = sorted(set(row["seed"] for row in group))
        rates = []
        for seed in seeds:
            one_seed = [row for row in group if row["seed"] == seed]
            rates.append(statistics.mean(row["success"] for row in one_seed))
        fault_rows.append(dict(
            controller=controller, split=split, fault=fault, seeds=len(seeds),
            configurations_per_seed=len(group) // len(seeds), success_mean=statistics.mean(rates),
            success_sd=statistics.stdev(rates) if len(rates) > 1 else None,
        ))

    # Replay decisions before writing summaries. Then independently reconcile
    # their totals with CSV episodes so a plausible aggregate cannot hide errors.
    traces = [json.loads(line) for line in (run_dir / "traces.jsonl").read_text().splitlines()]
    for decision in traces:
        state = state_from(decision["state"])
        action = ACTIONS.index(decision["proposed"])
        following, reward, done, info = step(state, action, decision["controller"] == "filtered")
        assert following == state_from(decision["next_state"]) and reward == decision["reward"]
        assert done == bool(decision["success"] or following.left == 0)
        assert all(decision[key] == value for key, value in info.items())
        if decision["controller"] == "rule":
            assert action == rule(state)
    for row in rows:
        group = [decision for decision in traces if
                 decision["controller"] == row["controller"]
                 and str(decision["seed"] or "") == row["seed"]
                 and decision["scenario"] == row["scenario"] and decision["split"] == row["split"]]
        assert len(group) == row["steps"] and sum(x["reward"] for x in group) == row["return_value"]
        assert group[-1]["success"] == row["success"]
        for field in ("critical_unavailable", "violations", "prohibited", "replaced",
                      "cost", "invalid", "batch_unavailable", "throttled"):
            assert sum(decision[field] for decision in group) == row[field]
    verification = dict(evaluation_rows=len(rows), trace_rows=len(traces),
                        replay_and_metric_checks_passed=True)
    artifacts = {
        "seed_aggregates.json": aggregates, "summary.json": summary,
        "per_fault.json": fault_rows, "evidence_checks.json": verification,
    }
    if write:
        for filename, value in artifacts.items():
            (run_dir / filename).write_text(json.dumps(value, indent=2))
    return artifacts
