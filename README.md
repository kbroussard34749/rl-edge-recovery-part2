# Q-learning with a safety filter for simulated edge-cluster recovery

PhDAI-830 Part 2, Keith G. Broussard. Simulation only. No network-device, hypervisor, service-management, SSH, cloud, or production-control interface is included. Submitted Part 1 is the design baseline; this repository contains implementation and measured evidence created October 9, 2026.

## Run from a clean extracted directory

Requires Python 3.12 (tested 3.12.14). Experiment, tests, summaries, and live demo use the standard library. No pip installation is required. Commands assume this directory is current and `python3` points to Python 3.12.

```sh
python3 -m unittest discover -s tests -v
python3 recovery.py validate
python3 recovery.py run
python3 analyze.py
python3 recovery.py demo --controller filtered --scenario node_0
python3 recovery.py demo --controller filtered --scenario cpu_4
python3 boundary_demo.py
python3 demo_server.py
```

Open http://127.0.0.1:8765 for the live demo. It binds only to this computer. Stop with Ctrl+C. Choose `node_0` for learned training recovery, `cpu_4` for a held-out failure, then rule/`cpu_4` for comparison. Boundary-demo output is an explicitly separate development test, not a held-out agent achievement. The browser runs the real Python simulator with the saved final seed-1000 policy. Retained policies use portable JSON, not pickle. All scenarios can be replayed with `--scenario`; controller options are filtered/unshielded/rule. The CLI supports `--seed 1000` through `1009` for final policies.

`run` regenerates experiment outputs at the same locations. Copy outputs if you need to preserve the original run before rerunning. It trains 40 models x 20,000 episodes = 800,000 episodes, plus two 1,000-episode pilots; evaluates 5 tuning seeds per alpha (.1/.3) per learner; freezes selection before final held-out evaluation; then trains 10 fresh seeds per learner. Configuration and physical scenario manifests are committed JSON. The experiment writes its manifests deterministically from the reviewed source. Use `--episodes` only for development; any such run is a changed experimental budget and must not be presented as the retained full run.

## Files and evidence

- `recovery.py`: immutable simulator state, action validity, immediate filter, Q update, rule controller, manifest, BFS validation, pilot, training and evaluation.
- `tests/test_recovery.py`: capacity boundaries, dependency, costs, blocked proposals, proposed-action update, restore/migration, terminal accounting, and scenario splits/feasibility.
- `config.json`, `scenarios.json`: actual run design and split assignments, including valid pre-fault states and one injected fault.
- `outputs/frozen_protocol.json`: alpha selection and scenario hash frozen before held-out results.
- `outputs/pilot.json`, `outputs/provenance.json`: measured runtime and process peak RSS; RSS is cumulative for the experiment process including caches, not isolated learner memory.
- `outputs/tuning/` and `outputs/final/`: per-run episode CSVs, 200-episode curves, JSON Q-table policies, and metadata. These CSVs are episode-level training summaries, not full training-transition logs.
- `outputs/validation.csv`: validation results; no test data used for selection.
- `outputs/evaluation.csv`: every final test/training-diagnostic episode. `outputs/traces.jsonl`: every transition of those evaluations.
- `analyze.py`, `outputs/seed_aggregates.json`, `outputs/summary.json`: seed-first descriptive summaries, denominators, sample SD and min/max. No significance or convergence claim. `outputs/evidence_checks.json`: replay and metric crosschecks.
- `demo_server.py`, `boundary_demo.py`: live display and separately labeled boundary fixture.

## State, reward, filter, and terminal rules

State contains node health; fixed background CPU/memory; service placement/running status; batch throttle flag; and remaining 20 steps. Loads and availability are derived. Web requires database availability. Target physically nonoperational database first, then web, then batch. Nine commands cover five categories. Invalid commands are logged no-ops; every command consumes a step. Failed nodes stay failed; restore assumes recoverable data elsewhere. Migration/restore operations are instantaneous.

Reward is `-1 - 10*Uc - 2*Ub - B - I - 5*P - 20*F`: post-step critical unavailable count, batch unavailable, operational throttled batch, executed intervention cost, prohibited proposal, and unsuccessful budget exhaustion. Restart/throttle cost 1; migrate/restore cost 3. Terminal Q updates bootstrap zero. Filtered Q values are values of proposed actions under the fixed filter and actual transition/reward. A blocked proposal becomes wait and retains its proposal penalty. Filtering rejects executable actions exceeding destination capacity or removing an already available critical service. Invalid structural commands are not mislabeled as prohibited proposals. Initial fault overload is separate from action-created violations.

`critical_unavailable` sums post-step unavailability across web/database; it counts service-decision intervals, not wall-clock seconds. Successful recovery steps exclude failures and preserve the denominator in seed aggregates. All-episode steps include budget-exhaustion failures. Unseen fraction is unseen decisions divided by all evaluated decisions; it is inapplicable to the rule controller (stored zero). Filter intervention rate is replaced proposals divided by all proposals.

## Results and limits

Both learned controllers recover all 12 training configurations across all 10 final seeds. On eight held-out configurations, each recovers 2/8 per seed (25%); the deterministic rule controller recovers 8/8 (100%) once each. All held-out learner states are unseen. Fixed greedy tie-breaking selects restart from zero Q-values, succeeding on the two crash configurations and failing CPU/memory/node faults. The 90% planning target is not achieved.

No controller proposes or executes prohibited actions in these final evaluations. The benchmark does not establish a filter advantage; spare destination resources make these scenarios weak safety stress tests. The separate boundary fixture exercises blocking, but is not evidence of learned policy superiority. Training return improves without establishing convergence or transfer. Ten identical aggregate held-out outcomes have sample SD zero; that does not remove scenario-selection uncertainty. Eight hand-designed configurations are not a population sample.

## Reconciliation with Part 1

Core simulation/state/action/reward/filter design, 24 configurations, splits, algorithms, alpha candidates, seeds, and episode budget are retained. Specific legal starting configurations and deterministic ties have been instantiated. Standard-library `random.Random`, CSV and JSON replace proposed NumPy/pandas bookkeeping; no RL behavior change is claimed, and cross-library seeds are not assumed equivalent. Transition caching accelerates repeated deterministic transitions without changing their definitions. The complete pilot allowed the planned budget, so no deadline-driven episode/seed reduction was needed. The relative ten-workday timeline was replaced by the actual October 9 execution; runtime is not evidence of ten days of work. Neural architectures and MARL were not added. An exact lookup limitation is reported rather than tuned away on test scenarios.

## AI assistance and unresolved disclosure placement

OpenAI Codex assisted with source inspection, implementation, test construction, experiment execution, evidence checking, analysis, and preparation of presentation materials. Keith's review, explanation, and personal reflection remain separate requirements; this file does not claim that those are complete. The assignment lists video, slides, and repository, but says AI use must be disclosed “in your written report.” That placement remains unresolved. This README and the deck carry a visible disclosure; no extra report requirement is invented.

## Access and submission

This is a complete local repository/package. A local Git commit or ZIP does not establish instructor access. Remote destination, reviewer access, and the final recording still require confirmation/checking. No publication or LMS submission has occurred. Course manuscripts and local/private course archives are not bundled into this repository; scholarly references should use their public publication URLs.
