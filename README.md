# Q-learning with a safety filter for simulated edge-cluster recovery

Keith G. Broussard · PhDAI-830 · Professor Atif Farid Mohammad

This simulation compares filtered Q-learning, unshielded Q-learning, and a deterministic rule controller. The [submitted Part 1 plan](docs/plan/RL_Project_Part_1_Plan_and_Design_Report_Keith_Broussard.docx) controls the design. The original October 9 experiment is retained unchanged; an incremental refactor separates its implementation into commented modules. Experiment orchestration, evidence relocation, and the full isolated reproduction are complete and verified.

## Structure

```text
src/edge_recovery/       Simulator, controllers, training, evaluation, experiment and evidence checks
scripts/                Commands for experiments, validation, analysis and policy checks
config/                 Frozen experiment configuration and scenario manifest
results/original_run/   Original policies, episode histories, traces, metrics and logs
results/reproductions/  Separate executions of the refactored implementation
results/figures/        Reserved for source-backed presentation visuals
tests/                  Boundary, controller and orchestration checks; frozen reference code
docs/                   Part 1 plan, technical decisions, protocol and verification records
```

## Python and PyCharm

Python 3.12 is required; the original runtime was Python 3.12.14 on macOS. The experiment, analysis and demo use the standard library, so no pip packages are required. Open this repository folder in PyCharm and choose a Python 3.12 interpreter. Run commands from the repository root. The scripts load the local src package automatically.

Windows execution has not been tested. Peak RSS is unavailable when the standard-library resource module is absent. RSS includes the process's previous work and caches; it is not isolated learner memory.

## Check the retained evidence

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate_scenarios.py
python3 scripts/analyze_results.py
python3 scripts/verify_policy.py
python3 scripts/verify_simulator_equivalence.py
python3 scripts/verify_controller_equivalence.py
```

Analysis and policy commands default to read-only checks of results/original_run/. The equivalence scripts compare the new modules with the original code retained in tests/reference/. Their small temporary training runs are extraction checks, not replacement scientific results.

## Run a full isolated experiment

Choose a directory that does not already exist:

```sh
python3 scripts/run_experiment.py --output results/reproductions/my_full_run
python3 scripts/analyze_results.py --run-dir results/reproductions/my_full_run --write
python3 scripts/verify_policy.py --run-dir results/reproductions/my_full_run --write
```

The verified [October 9 reproduction](docs/full_reproduction_validation.md) is retained at results/reproductions/full_2026-10-09/ and matches the original scientific evidence.

The command runs the two 1,000-episode pilots and all 800,000 planned training episodes. It validates 24 starts, tunes alpha on four validation starts using five seeds per candidate and condition, saves selected settings, then trains ten fresh final seeds per learner. Evaluation uses eight held-out starts plus a separate twelve-start training diagnostic. The rule controller runs once per configuration.

The command refuses existing output directories and destinations inside the retained original run. A smaller --episodes value is development only and is identified as such in run_identity.json. It is not the full planned budget. Each new run includes config/scenario snapshots, policy and episode files, evaluation traces, provenance, and source hashes.

## Demonstrate the agent

These compatibility commands now use the modular implementation and relocated original policies:

```sh
python3 recovery.py demo --controller filtered --scenario node_0
python3 recovery.py demo --controller filtered --scenario cpu_4
python3 recovery.py demo --controller rule --scenario cpu_4
python3 boundary_demo.py
python3 demo_server.py
```

Open http://127.0.0.1:8765. The server binds only to this computer; stop with Ctrl+C. The browser uses final seed 1000. node_0 shows learned training recovery; cpu_4 shows held-out learner failure and rule recovery. The boundary fixture demonstrates a blocked harmful proposal separately from the held-out experiment. The root recovery.py run command also requires --output; it no longer overwrites retained evidence.

## Design and measured limits

State contains node health, fixed background demand, service placement/running status, batch throttling, and remaining budget. Web depends on the database. The simulator targets physically nonoperational database, then web, then batch. Invalid commands consume a step. Failed nodes remain failed; restore assumes recoverable data elsewhere. Interventions are instantaneous.

The step reward is:

$$
r = -1 - 10U_c - 2U_b - B - I - 5P - 20F
$$

Here, $U_c$ counts unavailable critical services; $U_b$ indicates unavailable batch; $B$ indicates operational throttled batch; $I$ is the executed intervention cost; $P$ indicates a prohibited proposal; and $F$ indicates unsuccessful budget exhaustion. Availability is measured after the command.

The fixed filter converts executable capacity/critical-loss proposals to wait. The learner updates the proposed command using the actual outcome. Terminal updates bootstrap zero.

The original learners recover 100% of training starts and 2/8 held-out starts per seed (25%). The rule controller recovers 8/8 held-out starts (100%). Held-out learner decisions use unseen exact states; zero values with fixed ties choose restart. No final evaluation executes prohibited actions, so the experiment does not establish filter superiority. Seed SD zero does not remove uncertainty from eight hand-designed held-out configurations. Training curves do not establish convergence.

The [protocol](docs/experiment_protocol.md), [technical decisions](docs/decisions.md), [presentation alignment](docs/presentation_alignment.md), and [verification records](docs/implementation_gates.md) distinguish the original study from later extraction checks and reproduction. Scholarly sources are in [references](docs/references.md). The [visual plan](docs/visual_plan.md) maps workflow diagrams, evidence charts, trace storyboards, and conclusions to a possible presentation revision.

## AI assistance and access

OpenAI Codex assisted with source inspection, implementation, tests, experiment execution, evidence checks, analysis, presentation preparation, and the incremental refactor.

The remote repository is https://github.com/kbroussard34749/rl-edge-recovery-part2. Instructor access is on hold. Local refactor commits do not establish remote synchronization or instructor access. The recording is a separate pending artifact. No LMS submission has occurred. Editable slides remain in the adjacent course presentation folder.
