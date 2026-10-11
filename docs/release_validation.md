# Release candidate — October 11, 2026

The demonstration increment is committed as 9bba42e. Keith approved advancement to release preparation. This stage prepares a fresh candidate package and reconciles the remaining documentation with the current v4 presentation and 38-test suite (37 demonstration checks plus one archive-verification check). It does not authorize publication, replacement of the existing ZIP, or instructor access changes.

The candidate includes the source checkout, standard-library dependency record, configuration, original experiment evidence, verified reproduction, tests, and technical documentation. It excludes Git metadata, IDE settings, local AGENTS instructions, caches, private adjacent course records, and editable presentation files. The submitted Part 1 design remains included as the controlling project baseline.

Build a fresh candidate from the checkout:

```sh
python3 scripts/package_release.py --output ../packages/NEW_CANDIDATE_NAME.zip
```

The command refuses an existing ZIP or manifest and requires an output outside the repository. The accompanying .manifest.json records every included path, size, SHA-256, current HEAD, pending checkout revisions, and the complete ZIP hash. Fixed archive metadata makes identical file contents produce identical ZIP bytes. Packaging includes pending documented revisions; it does not represent them as committed or approved.

Extract the ZIP and run commands from its rl-edge-recovery folder using Python 3.12. The README contains experiment and demo instructions. Run the complete test suite, retained analysis/policy checks, and full-reproduction verifier:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/analyze_results.py
python3 scripts/verify_policy.py
python3 scripts/verify_reproduction.py --run-dir results/reproductions/full_2026-10-09 --output CHECK_RECORD.json --archived-checkout
```

The archive flag retains every scientific/source/configuration check and explicitly declines to infer execution chronology from reassigned file timestamps. The strict command without the flag remains applicable to the executed checkout. Browser serving uses 127.0.0.1; the commands contain no infrastructure-control interface.

Verification status is recorded in the adjacent package validation report after actual extraction checks. The old distribution ZIP is retained unchanged. Candidate validation does not establish a recorded presentation, remote synchronization, repository accessibility to the instructor, or LMS submission.

Proposed release-preparation commit: `Prepare and validate the repository release candidate`.

Exact proposed scope: docs/README.md, docs/controller_validation.md, docs/experiment_protocol.md, docs/full_reproduction_validation.md, docs/references.md, docs/simulator_validation.md, docs/visual_plan.md, docs/documentation_review.md, docs/release_validation.md, scripts/package_release.py, scripts/verify_reproduction.py, scripts/README.md, tests/test_release_verification.py, and docs/implementation_gates.md. The first eight are the previously pending documentation revisions, now reconciled for release. Learning, simulator behavior, model configuration, and measured evidence are unchanged. Verification now separates archive byte identity from execution chronology.

Status: prepared and verified. Extraction checks pass for all 449 included file hashes, 38 tests, retained analysis/policy checks, three terminal demo cases, the boundary fixture, all 187 original outputs, and 136 reproduction artifact matches; no release commit, push, ZIP replacement, instructor invitation, recording, or submission has occurred in this stage. Approval to commit the exact scope and perform each release action remains required by AGENTS.md.

Keith approved the exact release commit, distribution ZIP replacement, and push of main on October 11, 2026. Instructor access remains on hold. The released archive is built from the approved commit and verified before replacement; its external manifest and validation report record byte identity and execution outcomes.
