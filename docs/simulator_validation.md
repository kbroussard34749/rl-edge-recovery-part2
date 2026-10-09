# Simulator increment validation

The extracted simulator preserves the original implementation in the comparisons completed October 9, 2026. This check does not train or evaluate a new policy.

## Implemented workflow

1. environment.py observes immutable state, calculates loads and service availability, then models the structural proposal and its immediate constraint effects.
2. safety_filter.py executes the proposal or replaces it with wait, calculates reward from the actual outcome, and returns proposed/executed audit fields and termination.
3. scenarios.py constructs the fixed starts and checks development-only recovery feasibility. Its search results do not enter training.

Comments explain this flow, physical targeting, the web/database dependency, blocked-proposal accounting, resource assumptions, and final-command success.

## Executed checks

| Check | Observed result |
|---|---|
| python3 -m unittest discover -s tests -v | 17 tests passed: nine original and eight modular boundary tests |
| python3 scripts/verify_simulator_equivalence.py --output docs/simulator_checks.json | Passed |
| Scenario manifest | All 24 starts match, including JSON serialization |
| Feasibility records | Identical to all retained records |
| Reachable physical states compared | 217, including both conditions and development boundary fixtures |
| Structural transition comparisons | 5,859 |
| Executed-step comparisons | 4,428, at budgets 20, 2, and 1 |
| Successful-state terminal rejections | 7,290 |
| Retained evaluation trace replays | All 2,832 match next state, reward, termination, and every audit field |
| Original output preservation | All 187 retained output files match reference SHA-256 hashes |

simulator_checks.json records the reference commit, counts, and source hashes. The comparison reads the original recovery.py and retained artifacts; it writes only the requested check report.

## Limits and next increment

These checks establish equivalence for the exercised simulator state space, not all arbitrary states or production behavior. Controllers, training, evaluation orchestration, and the live demo still use the original root implementation. They have not been migrated or reproduced in this increment. Original scientific findings and presentation content remain unchanged.
