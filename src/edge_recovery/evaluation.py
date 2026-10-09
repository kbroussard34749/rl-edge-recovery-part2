"""Evaluate fixed policies without exploration or Q-table updates.

Each requested start produces one episode record and optional decision traces.
These records keep recovery, outages, cost, and constraint behavior separate.
Training-start evaluation is a diagnostic; held-out evaluation measures transfer
within the frozen scenario set. Neither establishes production reliability.
"""

from dataclasses import asdict

from .controllers import greedy, rule
from .safety_filter import step
from .scenarios import state_from


def evaluate(q: dict, scenarios: list, controller: str, seed,
             split: str, trace: bool = True) -> tuple:
    """Return episode rows and traces for the selected split and controller.

    The learner uses zero values for unseen exact states and fixed greedy ties.
    Evaluation counts those decisions without inserting states into the table.
    The deterministic rule controller has no learned-state coverage measure.
    """
    results = []
    traces = []
    for scenario in scenarios:
        if scenario["split"] != split:
            continue
        state = state_from(scenario["initial"])
        total = 0
        metrics = dict(
            cost=0, critical_unavailable=0, batch_unavailable=0, throttled=0,
            prohibited=0, violations=0, replaced=0, invalid=0,
        )
        unseen = 0
        for decision in range(20):
            if controller == "rule":
                action = rule(state)
            else:
                unseen += int(state not in q)
                action = greedy(q.get(state, [0.] * 9))
            next_state, reward, done, info = step(state, action, controller == "filtered")
            total += reward
            # Outage sums count post-command service-decision intervals, not
            # elapsed seconds. Every failed episode retains all budget steps.
            for key in metrics:
                metrics[key] += info[key]
            if trace:
                traces.append(dict(
                    controller=controller, seed=seed, scenario=scenario["id"],
                    split=split, step=decision + 1, state=asdict(state),
                    next_state=asdict(next_state), reward=reward, **info,
                ))
            state = next_state
            if done:
                break
        results.append(dict(
            controller=controller, seed=seed, scenario=scenario["id"],
            fault=scenario["fault"], split=split, success=info["success"],
            steps=decision + 1, return_value=total, unseen=unseen, **metrics,
        ))
    return results, traces


def score(rows: list) -> tuple:
    """Rank validation results by success, lower critical outage, then return.

    This function supplies the original selection criterion. The experiment
    layer will apply it before held-out evaluation; it does not select here.
    """
    return (
        sum(x["success"] for x in rows) / len(rows),
        -sum(x["critical_unavailable"] for x in rows) / len(rows),
        sum(x["return_value"] for x in rows) / len(rows),
    )
