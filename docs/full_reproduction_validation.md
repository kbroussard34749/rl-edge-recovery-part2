# Full isolated reproduction validation

The refactored experiment completed October 9, 2026 in results/reproductions/full_2026-10-09/. It reproduces the original scientific artifacts while retaining the original run separately.

## Executed protocol

Runtime: Python 3.12.14 on macOS-27.0.1-arm64-arm-64bit. The experiment validates all 24 starts, runs two 1,000-episode pilots, tunes five seeds per alpha and learner, freezes alpha selection, trains ten fresh final seeds per learner, and evaluates the frozen policies on held-out and training-diagnostic starts. The deterministic baseline runs once per configuration. All 31 implementation tests pass in the retained tests.log.

## Artifact comparison

| Requirement | Verified evidence |
|---|---|
| Complete workload | 42 model runs: 800,000 training episodes and 2,000 pilot episodes |
| Learned behavior retained | All 42 policies, 42 episode CSVs, and 42 curves match byte-for-byte |
| Design retained | Configuration and scenario snapshots match source design bytes |
| Tuning and freeze | Both conditions select alpha .1; all 80 validation rows independently reconstructed from saved tuning policies |
| Selection before testing | Freeze precedes final policy and evaluation files; separate control-flow test checks freeze presence at first held-out call |
| Final results | Evaluation CSV and every decision trace match byte-for-byte |
| Analysis | Seed aggregates, summary, per-fault results and evidence/policy checks match byte-for-byte |
| Original evidence | All 187 original output hashes remain unchanged |
| Source identity | Current package hashes match run_identity.json |

The comparison covers 136 exact scientific-artifact matches, plus the two matching configuration snapshots. All scientific fields in 42 training metadata files match. Pilot and provenance scientific fields also match. Original historical logs and demonstration text exports remain preserved records rather than byte-equality targets for a new execution.

## Runtime and memory differences

Original experiment time: 6.956021 seconds. Reproduction time: 6.987298 seconds. Original peak RSS: 52,674,560 bytes. Reproduction peak RSS: 51,494,912 bytes. These are whole-process measurements including caches and prior process activity, not isolated learner-memory estimates or a controlled timing comparison.

The canonical reproduction uses Python 3.12.14 and the package source identified in `run_identity.json`. Auxiliary completed executions retained outside this package are execution records, not additional independent training seeds. The committed reproduction is the source for the comparison reported here.

## Findings preserved

Both learned controllers recover all training starts and 2/8 held-out starts per seed. The rule controller recovers 8/8 held-out starts. All held-out learner decisions use unseen exact states and fixed zero-value ties select restart. Final evaluation has no prohibited proposals or executed violations, so it does not establish filter advantage. The original 90% held-out planning target remains unmet. The structural refactor changes organization and documentation, not these conclusions.

## Reproduce this verification

Run scripts/run_experiment.py with a fresh --output path, then scripts/analyze_results.py and scripts/verify_policy.py with that --run-dir and --write. Finally run scripts/verify_reproduction.py --run-dir PATH --output CHECK_RECORD.json. The comparison requires the full original design and budget. Original writes and reuse of an existing run directory are rejected.

The comparison record is [full_reproduction_checks.json](full_reproduction_checks.json). The reproduction directory retains run.log, analysis.log, tests.log, configuration snapshots, policies, episode records, metrics, traces, provenance, and run identity. No remote synchronization, repository invitation, presentation edit, recording, or submission is established by these checks.

## Verification after distribution

ZIP extraction and Git checkout assign new file timestamps. For an extracted or copied checkout, add --archived-checkout to verify_reproduction.py. This preserves every source, design, policy, history, trace, metric, and validation comparison, while recording freeze_precedes_final_policy_files as null and chronology_check_mode as not_established_from_archived_timestamps. The original strict command still requires execution-order timestamps. The archived check does not replace the original execution-order evidence or the freeze-before-testing control-flow test.
