"""Print feasibility checks without training or changing retained evidence."""

import json
import _bootstrap
from edge_recovery.experiment import load_design
from edge_recovery.scenarios import feasible, state_from


if __name__ == "__main__":
    _, scenarios = load_design()
    print(json.dumps([
        dict(id=scenario["id"], **feasible(state_from(scenario["initial"])))
        for scenario in scenarios
    ], indent=2))
