# Experiment protocol and Part 1 alignment

The submitted Part 1 document in plan/ is the baseline. This protocol records the retained original experiment and the preservation requirements for the incremental refactor. Verification of new modules is pending.

| Part 1 requirement | Retained implementation/evidence | Refactor acceptance condition |
|---|---|---|
| Three nodes; CPU/memory capacity 10 | recovery.py State and load helpers | Identical state and derived-load behavior |
| Web (3,2), database (4,4), batch (2,3); throttle batch CPU to 1 | DEMAND and loads | Preserve demands and memory behavior |
| Web depends on database; fixed background demand, failed nodes remain failed | physical, available, transition | Preserve availability and failed-node restoration assumptions |
| Exact state includes 20-action budget | State; policy.json state fields | Preserve hashable representation and action-budget accounting |
| Nine commands; database/web/batch physical target order | ACTIONS and transition | Preserve command indices, target order and structural validity |
| Filter executable capacity/critical-loss proposals to wait | step and shared transition checker | Preserve actual transition and proposed-action penalty |
| Reward −1−10Uc−2Ub−B−I−5P−20F | step, evaluation traces | Compare rewards and metrics for identical transitions |
| Sparse Q values; gamma .95; alpha .1/.3; terminal zero bootstrap | update, train, config.json | Preserve Q update and random draw order |
| Epsilon 1 to .1 over first 16,000 of 20,000 episodes | train and episode histories | Preserve exploration schedule |
| 24 starts: 12 train, 4 validation, 8 held-out, all four faults per split | scenarios.json and scenario_validation.json | Preserve manifest bytes and development-only search separation |
| Five tuning seeds per alpha, ten fresh final seeds per learner | outputs/tuning, outputs/final, frozen_protocol.json | Preserve selection before held-out evaluation |
| Planned 800,000 training episodes plus pilot | provenance.json and pilot histories | Reproduce complete budget without replacing original evidence |
| Seed-first summaries, per-fault results, visible failure cases | evaluation.csv, traces.jsonl, seed_aggregates.json, per_fault.json | Compare all retained analysis outputs |
| Practical rule comparison | rule and rule evaluation rows | Preserve deterministic once-per-configuration baseline |

## Results retained as reference

The learners each recover 2/8 held-out starts per seed (25%); the rule controller recovers 8/8 (100%). Both learners recover all training configurations. Held-out learner decisions use unseen exact states; zero Q values with fixed restart tie-breaking explain the observed failure pattern. No final evaluation controller executes prohibited actions; the benchmark does not establish filter superiority. The separate development boundary fixture demonstrates filtering, not learned superiority. These conclusions remain subject to comparison of the refactored code against retained evidence.

## Explicit deviations from the proposal

The completed original implementation uses standard-library random.Random, CSV, and JSON instead of proposed NumPy/pandas bookkeeping. Transition caching accelerates deterministic operations. Exact configurations and tie order were instantiated. The full budget was feasible on October 9; the proposed ten relative workdays are not claimed as elapsed work. Three nodes are controlled by one agent; no multi-agent or neural architecture was added.

## Evidence preservation

Original files are inventoried at the reference Git commit. Original outputs have been relocated from outputs/ to results/original_run/ byte-for-byte. docs/relocation_checks.json records every moved path and hash. New execution writes separately under results/reproductions/. Source hashes, paths, timing, and process memory metadata may differ; every difference will be identified. Equal outcome totals alone are insufficient to establish behavioral equivalence.
