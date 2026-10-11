# Experiment protocol and Part 1 alignment

The submitted Part 1 report defines a simulation-only comparison of filtered Q-learning, unshielded Q-learning, and a deterministic rule controller. The completed implementation retains its state, action, reward, split, seed, and budget design. A full isolated reproduction confirms that the structural refactor preserves the original scientific artifacts.

## Model and learning design

Each of three nodes has CPU and memory capacity of 10 abstract units. Web, database, and batch instances require (3, 2), (4, 4), and (2, 3) units respectively. Batch throttling reduces CPU demand to 1 without changing memory demand. Web availability depends on database availability.

The state contains node health, fixed background demand, service placement and running status, throttling, and the remaining 20-command budget. Diagnosis is supplied, interventions are instantaneous, and failed nodes remain failed. Restoration assumes recoverable data outside the failed node. Concurrent faults, transfer delays, migration overhead, and database consistency are excluded.

Nine commands represent restart, batch throttling, migration to each node, restoration to each node, and wait. The physical model targets a nonoperational database first, then web, then batch. Structurally invalid commands are logged no-ops. Every command consumes a step.

The fixed filter replaces executable proposals that exceed destination capacity or remove an available critical service with wait. The reward remains attached to the proposed command and reflects the actual resulting state:

$$
r = -1 - 10U_c - 2U_b - B - I - 5P - 20F
$$

$U_c$ counts unavailable critical services; $U_b$ indicates unavailable batch; $B$ indicates operational throttled batch; $I$ is executed intervention cost; $P$ indicates a prohibited proposal; and $F$ indicates unsuccessful budget exhaustion. Availability is measured after execution. Restart and throttling cost 1; migration and restoration cost 3.

Q-learning updates the proposed command using the actual transition and reward. Terminal transitions use zero bootstrap. Discount factor $\gamma$ is 0.95; candidate learning rates are 0.1 and 0.3. Exploration decreases from 1.0 to 0.1 over the first 16,000 of 20,000 episodes, then remains 0.1. Greedy evaluation uses fixed command-order ties and zero values for unseen states.

## Design-to-implementation map

Paths below refer to the current repository. Retained original results are under `results/original_run/`; the isolated reproduction is under `results/reproductions/full_2026-10-09/`.

| Part 1 requirement | Current implementation or evidence | Verification |
|---|---|---|
| Node resources, service demand, and dependency | `environment.py`: `State`, `DEMAND`, `loads`, `physical`, `available` | Boundary assertions and differential comparisons |
| Exact state and 20-command budget | `environment.py`: `State`; saved `policy.json` | State and terminal accounting checks |
| Nine commands and physical target order | `environment.py`: `ACTIONS`, `transition` | Structural transition comparisons |
| Fixed filter and actual-outcome reward | `safety_filter.py`: `step` | Blocked-proposal, critical-loss, and trace checks |
| Proposed-command Q update | `controllers.py`: `update` | Nonterminal, terminal, and blocked-command assertions |
| Seeded exploration and sparse Q-table | `training.py`; `config/experiment.json` | Paired training and full policy/history comparison |
| 24 starts: 12 training, four validation, eight held-out | `config/scenarios.json`; `scenarios.py`; `scenario_validation.json` | Exact manifest and development-only feasibility checks |
| Five tuning seeds per alpha and condition | `experiment.py`; `tuning/`; `validation.csv` | All 80 validation rows reconstructed from tuning policies |
| Selection before held-out testing | `frozen_protocol.json`; `experiment.py` | Control-flow check and saved-file order |
| Ten fresh final seeds per learner | `final/`; `evaluation.py` | All 20 final policies and 420 evaluation rows verified |
| Full workload | `provenance.json`; per-model episode CSVs | 800,000 training episodes and 2,000 pilot episodes counted |
| Seed-first and per-fault analysis | `evidence.py`; `seed_aggregates.json`, `per_fault.json` | Recomputed summaries and transition totals |
| Deterministic rule comparison | `controllers.py`: `rule` | One evaluation per configuration and action comparisons |

## Results and interpretation

Both learners recover all 12 training configurations across ten final seeds. Each recovers two of eight held-out configurations per seed (25%); the rule controller recovers all eight (100%) once each. Held-out learner decisions use unseen exact states. Zero action values and fixed ties select restart, which resolves the two crash configurations but fails persistent overload and node-failure configurations.

No final evaluation contains prohibited proposals or executed violations. The benchmark therefore provides no observed filter intervention from which to estimate a performance advantage. The separate development fixture verifies blocking behavior. The 90% held-out planning target is not achieved. These findings describe the retained configuration set; they do not establish population generalization, convergence, or production safety.

## Changes from the proposal

The implementation uses standard-library `random.Random`, CSV, and JSON instead of proposed NumPy/pandas bookkeeping. Deterministic transition caching accelerates repeated simulation. Specific legal configurations and the tie order were instantiated. The pilot supported the full planned budget without seed or episode reductions. The proposed ten relative workdays are not treated as elapsed execution time. One controller manages three nodes; no multi-agent or neural architecture is implemented.

## Evidence preservation

The [reference manifest](reference_manifest.json) identifies the original files. The [relocation record](relocation_checks.json) maps historical `outputs/` paths to `results/original_run/` with matching hashes. Reproduction writes to a fresh directory and preserves the original evidence. The [full reproduction comparison](full_reproduction_checks.json) verifies deterministic artifacts and records timing and memory differences separately.
