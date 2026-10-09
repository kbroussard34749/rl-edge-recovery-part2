# Incremental implementation gates

This is the current implementation record, not a reconstruction of earlier approvals. The original implementation and measured run already exist at the reference commit in reference_manifest.json. Keith approved the proposed structural direction and then requested incremental gated construction, comments, Part 1 in docs, and presentation alignment. He removed the proposed audience review-path experience from scope.

## Commit sequence

| Increment | Planned scope | Evidence before approval | Status |
|---|---|---|---|
| 1. Foundation | Baseline plan, package foundation, gate policy, protocol, evidence inventory, presentation map | Original source hashes; copied-plan identity; existing implementation unchanged | Committed locally: be7a681 |
| 2. Simulator | State, loads, availability, structural actions, filter, reward, scenario construction | Existing boundary assertions and original-versus-module transitions | Committed locally: c4c50f0 |
| 3. Controllers | Q update, tie-breaking, rule baseline, training, evaluation | Terminal/update assertions and deterministic comparison | Committed locally: bcdfdf7 |
| 4. Experiment | Orchestration, configuration, isolated reproduction, analysis and policy verification | Full planned run and artifact comparisons | Not started |
| 5. Demonstration | Local demo, boundary fixture, run instructions, final presentation path alignment | Actual demo cases and final code/evidence consistency | Not started |
| 6. Release | Approved cumulative changes, package and remote | Clean extraction checks, contents and access status | Not started |

At each stage the changed files and proposed commit are shown before staging. Approval can cover that specific commit and the named next increment; it does not approve later stages or publication. Commit dates reflect actual execution.

## Foundation check-in

Prepared October 9, 2026. Check results are recorded in foundation_checks.json. No new experiment has run, no original experiment file has been edited, and no remote change or package replacement has occurred during this increment.

Approval received October 9, 2026 for the foundation commit and simulator increment. AGENTS.md and .idea/ are excluded from the commit. The simulator commit requires a separate check-in.

Proposed commit: `Establish Part 1 baseline and gated refactor foundation`.

Next proposed increment: implement the commented simulator and scenario modules while retaining the original implementation as a comparison reference.

## Simulator check-in — October 9, 2026

The approved simulator increment extracts environment.py, safety_filter.py, and scenarios.py under src/edge_recovery/. The original recovery.py and runnable commands remain intact. Module comments explain the workflow and consequential assumptions using the requested writing style.

Verification: 17 tests passed (nine retained original tests and eight modular simulator tests). The differential check covered 217 reachable physical states, 5,859 structural transitions, 4,428 executed steps, 7,290 successful-state terminal rejections, and all 2,832 retained evaluation transitions. The 24-start manifest serialization and all feasibility records match. All 187 retained output files match their reference hashes. See simulator_checks.json and simulator_validation.md.

Proposed commit: `Extract commented simulator and verify reference behavior`.

Approval received October 9, 2026 for the simulator commit and the controllers, training, and evaluation increment. The controller-layer commit requires its own check-in. No full refactored training run, push, instructor invitation, or replacement ZIP has occurred.

## Controller-layer check-in — October 9, 2026

The approved increment extracts controllers.py, training.py, evaluation.py, and runtime.py. Comments explain action-value learning, future reward, proposed-command updates, exploration, fixed greedy ties, split boundaries, and metric interpretation.

All 25 tests passed: nine retained original tests, eight modular simulator tests, and eight controller/evaluation tests. Eight 601-episode development cases per implementation (4,808 episodes each) produced identical episode CSVs, curves, and Q-table JSON. Timing and cumulative process RSS were explicitly excluded from equality. Evaluation with all 20 saved final policies matched 420 retained episode records and 2,832 traces. Rule action comparisons and validation score comparisons passed, and all 187 original output hashes remain unchanged.

These development runs are extraction checks, not the full planned experiment. Temporary training files were removed automatically; hashes are recorded in controller_checks.json. Full experiment orchestration, analysis migration, and reproduction remain pending.

Proposed commit: `Extract commented controllers training and evaluation`.

Pre- and post-check-in approval granted October 9, 2026 for the current code, experiment orchestration, evidence relocation, and full isolated reproduction. These stages can be committed after their checks pass. This authorization does not extend to pushing, instructor access, a replacement ZIP, or presentation edits. No push, invitation, presentation edit, or replacement ZIP has occurred.

## Experiment orchestration check-in — October 9, 2026

Pre- and post-check-in approval covers this increment. Added an isolated run command, configuration validation, explicit tuning/freeze/final ordering, read-only original analysis, and policy evidence checks. All 31 tests pass, including overwrite protection and a control-flow test that checks the freeze file before held-out evaluation. The five analysis/policy JSON records recomputed read-only from original evidence match its serialization. Full reproduction follows relocation.

Commit scope: experiment.py, paths.py, evidence.py, policy_verification.py, five scripts for bootstrap/run/validation/analysis/policy checks, test_experiment.py, and these technical records.

Commit: `Add isolated experiment orchestration and evidence checks`.

## Evidence relocation check-in — October 9, 2026

Within the granted pre/post approval, relocated all 187 original outputs with matching hashes, moved unchanged design files into config/, and retained original reference code under tests/reference/. Updated compatibility commands and comparison scripts to use canonical paths. All 31 tests and both extraction comparison scripts pass. Restarted the existing local demo to load its corrected evidence path; no demo redesign is included.

Commit scope: tracked output/config/reference moves, compatibility commands, paths, comparison scripts and check records, package metadata, folder instructions, and technical documentation. AGENTS.md, .idea/, private course attachments, and editable slides remain excluded.

Commit: `Relocate original evidence and connect canonical repository paths`.
