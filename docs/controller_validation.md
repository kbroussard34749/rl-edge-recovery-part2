# Controller, training, and evaluation validation

The extracted learning and evaluation modules preserve the original behavior in the comparisons completed October 9, 2026. Full experiment orchestration is not yet migrated.

## Logic and workflow

1. controllers.py chooses the greedy command or ranks permitted outcomes for the rule baseline. Its Q update combines actual reward with discounted future value and updates the proposed command. Terminal transitions use reward alone.
2. training.py samples only training starts, explores commands with seeded random draws, steps through recovery, and updates the table. It writes episode histories, curves, policies, and metadata to the caller's directory.
3. evaluation.py selects commands without exploration or table updates. It counts unseen exact states, records command-level outcomes, and accumulates episode metrics. Zero unseen-state values retain the fixed restart tie-break.
4. runtime.py reports cumulative process peak RSS with platform unit handling, separate from learning behavior.

## Executed verification

| Check | Observed result |
|---|---|
| python3 -m unittest discover -s tests -v | 25 tests passed: nine original, eight modular simulator, eight controller/evaluation |
| python3 scripts/verify_controller_equivalence.py --output docs/controller_checks.json | Passed |
| Development training | Eight cases per implementation; alpha .1/.3, seeds 100/1000, both conditions, 601 episodes each |
| Deterministic artifacts | All eight episode CSVs, curves, and Q-table JSON files match byte-for-byte |
| Learning metadata | Seed, alpha, condition, episode count, Q-state count, and nonzero-pair count match |
| Retained final policies | All 20 evaluated without changing their tables |
| Retained evaluation records | All 420 episode rows match |
| Retained traces | All 2,832 trace rows match, including serialization |
| Rule selection | 2,832 original-versus-modular action comparisons pass |
| Validation ranking | 20 comparisons pass; no setting selection or policy revision performed |
| Original output preservation | All 187 retained output files match reference hashes |

The 601-episode budget covers full 200-episode curve intervals and a final partial interval. These are temporary development checks totaling 4,808 episodes per implementation. They do not replace or extend the scientific results of the original 800,000-episode experiment. Their artifact hashes and checked source hashes are recorded in controller_checks.json.

## Limits and next step

Execution time and cumulative process RSS are excluded from equality because they vary with process history and machine conditions. Evaluation comparison uses already saved policies; a full refactored training run is still needed after experiment orchestration is migrated. Original root entry points and the live demo remain in use. Presentation content and recorded scientific findings are unchanged.
