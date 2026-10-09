# Incremental implementation gates

This is the current implementation record, not a reconstruction of earlier approvals. The original implementation and measured run already exist at the reference commit in reference_manifest.json. Keith approved the proposed structural direction and then requested incremental gated construction, comments, Part 1 in docs, and presentation alignment. He removed the proposed audience review-path experience from scope.

## Commit sequence

| Increment | Planned scope | Evidence before approval | Status |
|---|---|---|---|
| 1. Foundation | Baseline plan, package foundation, gate policy, protocol, evidence inventory, presentation map | Original source hashes; copied-plan identity; existing implementation unchanged | Approved for commit |
| 2. Simulator | State, loads, availability, structural actions, filter, reward, scenario construction | Existing boundary assertions and original-versus-module transitions | Not started |
| 3. Controllers | Q update, tie-breaking, rule baseline, training, evaluation | Terminal/update assertions and deterministic comparison | Not started |
| 4. Experiment | Orchestration, configuration, isolated reproduction, analysis and policy verification | Full planned run and artifact comparisons | Not started |
| 5. Demonstration | Local demo, boundary fixture, run instructions, final presentation path alignment | Actual demo cases and final code/evidence consistency | Not started |
| 6. Release | Approved cumulative changes, package and remote | Clean extraction checks, contents and access status | Not started |

At each stage the changed files and proposed commit are shown before staging. Approval can cover that specific commit and the named next increment; it does not approve later stages or publication. Commit dates reflect actual execution.

## Foundation check-in

Prepared October 9, 2026. Check results are recorded in foundation_checks.json. No new experiment has run, no original experiment file has been edited, and no remote change or package replacement has occurred during this increment.

Approval received October 9, 2026 for the foundation commit and simulator increment. AGENTS.md and .idea/ are excluded from the commit. The simulator commit requires a separate check-in.

Proposed commit: `Establish Part 1 baseline and gated refactor foundation`.

Next proposed increment: implement the commented simulator and scenario modules while retaining the original implementation as a comparison reference.
