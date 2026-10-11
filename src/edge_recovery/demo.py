"""Demonstrate fixed policies and a separate development boundary fixture.

Episodes execute the same simulator used in evaluation. Saved policies are read
without training, exploration, or writes to retained evidence. Browser fields
are added to copies of traces so the scientific audit fields remain intact.
"""

import argparse
from dataclasses import asdict
import json

from .environment import State, available, loads
from .evaluation import evaluate
from .paths import ORIGINAL_RUN
from .safety_filter import step
from .scenarios import manifest, state_from

CONTROLLERS = ("filtered", "unshielded", "rule")
FINAL_SEEDS = tuple(range(1000, 1010))


def run_episode(controller="filtered", scenario_id="cpu_4", seed=1000):
    """Execute a retained policy on one named frozen scenario.

    Only final experiment seeds are allowed. The rule baseline has no training
    seed or learned-state coverage, so its browser coverage field is None.
    """
    if controller not in CONTROLLERS:
        raise ValueError("Unknown controller")
    if seed not in FINAL_SEEDS:
        raise ValueError("Choose a final seed from 1000 through 1009")
    scenario = next((x for x in manifest() if x["id"] == scenario_id), None)
    if scenario is None:
        raise ValueError("Unknown scenario")
    q = {}
    if controller != "rule":
        path = ORIGINAL_RUN / "final" / controller / str(seed) / "policy.json"
        q = {state_from(x["state"]): x["values"] for x in json.loads(path.read_text())}
    rows, traces = evaluate(q, [scenario], controller, seed, scenario["split"])
    displayed = []
    for trace in traces:
        following = state_from(trace["next_state"])
        displayed.append(dict(
            trace, loads=loads(following), availability=available(following),
            seen=None if controller == "rule" else state_from(trace["state"]) in q,
        ))
    return dict(summary=rows[0], trace=displayed)


def boundary_fixture():
    """Compare one harmful proposal with and without immediate filtering.

    This hand-built state is outside the final benchmark. The command restores
    the database onto the occupied web host and overloads that node. Filtering
    preserves the physical state and spends a step; it does not recover service.
    """
    state = State((True,) * 3, (7, 0, 0), (0, 0, 0), (0, 1, 2), (True, False, True))
    records = []
    for filtered in (False, True):
        following, reward, _, info = step(state, 5, filtered)
        records.append(dict(
            fixture="restore database to occupied web host; NOT held-out evaluation",
            filtered=filtered, before=asdict(state), after=asdict(following),
            reward=reward, **info,
        ))
    return records


def episode_main():
    """Print original audit fields and summary for terminal demonstrations."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controller", choices=CONTROLLERS, default="filtered")
    parser.add_argument("--scenario", default="cpu_4")
    parser.add_argument("--seed", type=int, choices=FINAL_SEEDS, default=1000)
    args = parser.parse_args()
    try:
        episode = run_episode(args.controller, args.scenario, args.seed)
    except ValueError as error:
        parser.error(str(error))
    for trace in episode["trace"]:
        audit = {k: v for k, v in trace.items() if k not in ("loads", "availability", "seen")}
        print(json.dumps(audit, indent=2))
    print("SUMMARY", json.dumps(episode["summary"], indent=2))


def boundary_main():
    """Print the two fixture records without saving or pooling them."""
    for record in boundary_fixture():
        print(json.dumps(record, indent=2))
