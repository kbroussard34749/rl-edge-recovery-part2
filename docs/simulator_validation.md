# Simulator increment validation

Simulator-stage comparisons completed on October 9, 2026 preserve the original physical and reward behavior within the exercised state space. The stage used 17 tests; the completed implementation later reached 31 tests. These comparisons do not train or evaluate a new policy.

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

simulator_checks.json records the reference commit, counts, and source hashes. The current comparison script reads the unchanged reference source at `tests/reference/recovery_reference.py` and evidence at `results/original_run/`. It writes only the selected check report.

## Scope and subsequent verification

These checks establish equivalence for the exercised simulator state space, not arbitrary inputs or production conditions. Controller extraction and full experiment reproduction were completed in later stages and are documented in [controller_validation.md](controller_validation.md) and [full_reproduction_validation.md](full_reproduction_validation.md). Root compatibility commands now use modular code. Original scientific findings remain unchanged.
