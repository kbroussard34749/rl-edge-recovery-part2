# Demonstration gate verification — October 11, 2026

The dedicated demonstration executes saved final policies against the existing simulator. It reads retained evidence without training or writing experiment files. The increment is prepared and verified, approved for commit on October 11, 2026.

## Actual checks

Python 3.12.14 ran the complete suite: 37 tests passed, including six new demonstration checks. Comparison covers all 420 retained final episode records and 2,832 decision traces. Display fields are removed before trace comparison. The rule reference seed is None; the demo's seed argument selects learner policies and does not identify a learned rule policy.

The hand-built harmful restore fixture serializes exactly like results/original_run/boundary_demo.json.txt. Unfiltered execution violates the modeled constraint; filtered execution substitutes wait, retains the outage, spends one command, and records reward −26. This is a development fixture outside the final benchmark.

HTTP checks verify loopback binding, all 24 scenario options, successful episode execution, invalid controller/scenario/seed rejection, and unknown-route handling. Three dedicated terminal demonstrations match recovery.py demo output, and both fixture entry points match the retained export. git diff --check passes.

A separate hash comparison confirms that demo execution does not change retained evidence. The read-only full-reproduction verifier passes: all 187 original outputs retain reference hashes, all 136 scientific artifacts match, the original 800,000 training and 2,000 pilot episodes remain verified, and 80 tuning-validation rows are reconstructed. No new training run was needed.

Browser inspection on local port 8766 confirms:

| Controller and case | Observed behavior |
|---|---|
| Filtered node_0, training | Three restoration commands; all services available; N1 remains failed |
| Filtered cpu_4, held out | Restart on unseen states; unsuccessful budget exhaustion at step 20 |
| Rule cpu_4, held out | One migrate_N1; successful recovery; training-state coverage shown as not applicable |

Screenshots and raw test/verification logs are retained privately in ../.build/demo_gate_2026-10-11/. Machine-readable results and current v4/guide identities are in demo_checks.json. The PPTX was inspected for demo cases, canonical source paths, and test-count wording; it was not modified by this gate. Its earlier rendering check remains separate evidence.

## Commands and concise recording sequence

Run from the repository root using Python 3.12:

```sh
python3 scripts/serve_demo.py
python3 scripts/demo_agent.py --controller filtered --scenario node_0
python3 scripts/demo_agent.py --controller filtered --scenario cpu_4
python3 scripts/demo_agent.py --controller rule --scenario cpu_4
python3 scripts/boundary_demo.py
```

The browser is http://127.0.0.1:8765. Use --port 8766 if another local demo already occupies 8765. Root recovery.py demo, demo_server.py, and boundary_demo.py remain compatible.

Allocate about 90 seconds within slide 12's 2:20 target: 25 seconds for training recovery, 25 for held-out restart failure, 20 for the rule comparison, and 20 for the separate boundary fixture. Keep slides, face, and narration visible throughout. Playback can advance repeated decisions while explaining the failure; identify any edit that skips repetitions. The adjacent rehearsal guide records this sequence. These are rehearsal allocations, not measured recording durations.

## Exact proposed commit scope

Proposed message: `Extract and verify the simulation demonstration`.

The following 20 files form this demonstration check-in:

```text
README.md
boundary_demo.py
demo_server.py
pyproject.toml
recovery.py
scripts/README.md
scripts/boundary_demo.py
scripts/demo_agent.py
scripts/serve_demo.py
src/edge_recovery/README.md
src/edge_recovery/demo.html
src/edge_recovery/demo.py
src/edge_recovery/demo_web.py
tests/test_demo.py
docs/decisions.md
docs/implementation_gates.md
docs/presentation_alignment.md
docs/demo_checks.json
docs/demo_validation.md
docs/gate_history_before_demo.md
```

The decisions, gate, and presentation-alignment files already contained pending documentation edits before this increment. Their current versions, including those revisions, are included in the proposed scope; the preserved gate history retains the earlier committed approvals and six-stage sequence.

Other pre-existing documentation changes are excluded: docs/README.md, controller_validation.md, experiment_protocol.md, full_reproduction_validation.md, references.md, simulator_validation.md, visual_plan.md, and the untracked documentation_review.md. They remain pending for a separate review.

The adjacent rehearsal-guide revision is course preparation outside the repository and outside this commit. AGENTS.md, .idea/, private course attachments, screenshots/logs in the adjacent build folder, and editable decks remain outside the commit.

## Gate boundary and next increment

Keith approved the exact scope and commit message, along with advancement to release-package preparation, on October 11, 2026. The approval precedes staging and committing. Release preparation would build a new candidate distribution package and verify its extracted commands and evidence. Replacing the existing ZIP, pushing GitHub, and changing instructor access require separate explicit authorization. Instructor access remains on hold.

Verification does not establish a recorded presentation, measured delivery duration, instructor access, remote synchronization, or submission. No recording or LMS submission was performed by this increment.
