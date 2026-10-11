# Documentation style and alignment review

The documentation was reviewed on October 9, 2026 for academic technical style, consistency with implemented behavior, and alignment with the Part 2 assignment. The review uses the submitted Part 1 design, current source and configuration, retained experiment evidence, the then-current v3 slide text, Week 7 learning materials, assignment directions, and rubric. It does not assess an unrecorded presentation or infer a grade.

## Writing revisions

The revised prose states technical purposes and findings directly, connects evidence to interpretation, and removes conversational history and personal commentary. Implementation decisions describe code choices, rationale, consequences, and status. The stage record describes acceptance criteria and observed results rather than permission exchanges.

Current paths replace obsolete implementation references. Historical test counts are labeled by stage: nine in the original study, then 17, 25, and 31 during refactoring. The protocol and decision records no longer describe completed orchestration or reproduction as pending.

The submitted DOCX and its paragraph-text extraction remain unchanged source records. Authorship attribution, technical filenames, and the literal assignment disclosure wording are retained where necessary for provenance. Machine-readable checkpoint records remain unchanged; their stage-specific values are interpreted as historical evidence.

## Code and results consistency

The read-only reproduction verifier passes against the current package hashes and retained data. It confirms 42 model runs, 800,000 training episodes, 2,000 pilot episodes, 136 exact scientific-artifact matches, matching design snapshots, and 80 validation rows reconstructed from saved tuning policies. All 187 original output files retain their reference hashes. These checks do not require a new training run.

| Held-out metric | Filtered Q-learning | Unshielded Q-learning | Rule controller |
|---|---:|---:|---:|
| Recovery per seed | 2/8 (25%) | 2/8 (25%) | 8/8 (100%), evaluated once |
| Mean steps per episode | 15.25 | 15.25 | 1.50 |
| Mean cumulative reward | −360.50 | −360.50 | −9.00 |
| Critical-service outage intervals per episode | 30.00 | 30.00 | 0.25 |
| Mean executed violations per episode | 0 | 0 | 0 |
| Unseen-state decision fraction | 100% | 100% | Not applicable |

Learner results summarize eight held-out configurations within each of ten final seeds before aggregation. The deterministic baseline uses the configurations once. Outages count post-command service-decision intervals, not seconds. Zero seed variability does not remove uncertainty from configuration selection. Final evaluations contain no prohibited proposals, so they do not establish filter superiority.

The learning-loop diagram now represents the terminal Q update before episode termination, consistent with training.py. Evaluation excludes exploration and table updates. The fixed rule ranking and safety filter are not learned components. Three nodes controlled by one learner do not constitute MARL.

## Eight required presentation sections

| Section | Documentation and evidence support | Remaining verification boundary |
|---|---|---|
| Project introduction | Part 1 objectives; sequential recovery motivation; implemented simulator | Narrated organization and delivery |
| Background and context | Selected Part 1 references and Module 7 context | Full source review is not established by bounded inspection records |
| Methodology | State, actions, reward, Q update, filter, terminal rules | Depth of explanation in the recording |
| Implementation | Modular source, sparse table, tools, training sequence, actual deviations | Slide source paths and test-count wording need reconciliation in a future revision |
| Results and analysis | Policies, curves, seed-first metrics, per-fault results, failure traces | Rendered revision and narration consistency |
| Demonstration | Recorded simulator traces and local working-agent implementation | Working-agent footage in the final recording |
| Ethical considerations | Immediate safety scope, restoration assumptions, simulation and reliability limits | Narrated discussion |
| Conclusion and future work | Unmet 90% target, unseen-state failure, rule comparison, proposed improvements | Reflective discussion in the recording |

## Rubric alignment

| Criterion | Weight | Supported scope | Unverified scope |
|---|---:|---|---|
| Introduction, organization, and delivery | 25% | Documented problem and connection to Part 1 | Confidence, pacing, transitions, and explanation beyond reading slides |
| Methodology, implementation, and understanding | 30% | Code-consistent design, workflow, training, and changes | Demonstrated command of the material in narration |
| Results, demonstration, analysis, and reflection | 30% | Verified metrics, traces, limitations, ethics, and future directions | Recorded demo and reflective delivery |
| Slides, repository, submission, and AI disclosure | 15% | Current deck content map, local source/dependencies/run instructions/outputs, factual disclosure | Final rendered revision, 13–15-minute face/slides/voice recording, instructor access, correct submission |

ScreenPal is recommended, not required. Any alternative recorder must satisfy the same recording conditions. The directions list video, slides, and repository while referring to AI disclosure in a written report. That placement remains unresolved; this review does not add a separate report deliverable.

The revision affects documentation only. Source code, configurations, policies, measured results, check-record JSON, submitted plan, and editable presentation remain unchanged. Documentation alignment does not establish full assignment completion, remote synchronization, or submission.

## October 11 release reconciliation

The v4 deck now uses canonical source paths, separates nine original tests from the 31-test refactor checkpoint, and contains the revised methodology, held-out analysis, and future-work notes grounded in Chapter 22. The dedicated demonstration adds six tests, bringing the current suite to 37; the deck's refactor count remains a historical checkpoint. The current deck's file identity and demo mapping are recorded in demo_checks.json and presentation_alignment.md.

Browser verification establishes the three live demo cases and the development fixture remains separately labeled. The v4 rehearsal guide includes an approximately 90-second demonstration within a 14:15 overall target. This is preparation evidence; footage, actual duration, face/voice coverage, narrated understanding, and submission remain unverified. The table's earlier future-revision statements describe the October 9 checkpoint; the current mapping supersedes them for content alignment.

The release candidate carries source, configuration, retained original evidence, the verified reproduction, tests, documentation, and package instructions. It excludes editable slides and private course preparation. ZIP extraction checks do not establish GitHub synchronization or instructor access.

Release extraction exposed timestamp reassignment as a verification boundary. A dedicated archive mode retains all scientific comparisons and records chronology as unestablished. A focused regression check preserves rejection in strict mode. The current suite contains 38 tests; the demonstration checkpoint remains 37 and the original experiment remains nine.
