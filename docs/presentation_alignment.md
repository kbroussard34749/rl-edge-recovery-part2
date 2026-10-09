# Alignment with Keith's edited v3 presentation

Reference: RL_Project_Part_2_Keith_Broussard_Draft_v3.pptx, inspected October 9, 2026. Its hash is in reference_manifest.json. The deck remains in the adjacent course presentation folder and was not modified or duplicated. The table describes the current deck, not a new presentation requirement.

| Slides | Content | Original evidence / implementation | Planned module or artifact |
|---|---|---|---|
| 1–2 | Project introduction and sequential recovery motivation | Submitted Part 1 problem and objectives | docs/plan/; environment.py |
| 3, 15 | Background, Q-learning, shielding, empirical design, course context | Part 1 literature and Research_References.md | docs/references.md |
| 4–6 | State, resources, commands, filter, reward, Q update | recovery.py; config.json; scenario manifest | environment.py, safety_filter.py, controllers.py |
| 7 | Immutable state, sparse table, caching, CSV/JSON, retained budget | Source and original run files | Modular source; experiment_protocol.md |
| 8 | 24 starts, nine original tests, seeds and budget | tests/test_recovery.py; scenario_validation.json; frozen_protocol.json; provenance.json | Focused test modules and isolated reproduction |
| 9 | Training return curves | outputs/final/*/*/curve.json | results/original_run/final/*/*/curve.json |
| 10–11 | Training/held-out success and held-out metric table | outputs/evaluation.csv; seed_aggregates.json | Preserved files under results/original_run/ |
| 12 | Learned node_0 recovery, cpu_4 learner failure, rule comparison, boundary fixture | Saved seed-1000 policies; real simulator; boundary_demo.py | demo entry points and demo_runbook.md |
| 13 | Immediate-check limits and practical assumptions | Part 1 model assumptions and actual filter scope | Module comments and runbook limitations |
| 14 | 25% held-out learning, 100% rule, exact lookup limits, future work | summary, unseen-state evidence, per-fault results | Preserved evidence and analysis |
| 16 | Actual Codex assistance disclosure | Implementation, tests, runs, checks and presentation preparation | Factual README disclosure |

## Alignment checks reserved for later gates

- Slide 8 currently says nine tests. If tests are split or meaningful new checks are added, reconcile the count explicitly instead of silently claiming it still matches.
- Slides 9–11 use original outputs/ paths. After relocation, provide a path map and obtain approval before changing Keith's deck or narration.
- Methodological checks, plots, results and demo must still describe the same frozen model and measured outcomes.
- No recording duration, face/voice coverage, understanding, personal reflection, instructor access or submission is established by this refactor.

## Simulator increment verification

The modular simulator preserves slides 4–6: node resources, dependency, state, action order, fixed filter, reward, and termination. Test discovery currently runs 17 tests: nine original reference tests and eight modular boundary tests. These are implementation checks after the original run, not a revision of its historical nine-test result. The deck is unchanged; final test-count wording will be reconciled after the test migration is complete.

## Controller-layer verification

The extracted modules retain the learning and evaluation behavior described in slides 6–11. Comments make the proposed-action Q update, exploration schedule, frozen-policy evaluation, and unseen-state restart tie explicit. Re-evaluating the 20 saved policies matches the original result rows and traces. The current test suite contains 25 tests across original and modular checks; these later extraction checks remain distinct from the original nine-test result. No slide or narration file was edited.

## Evidence path relocation

Every old outputs/ path maps to results/original_run/ with the remainder unchanged. The original config.json maps to config/experiment.json; scenarios.json maps to config/scenarios.json. Original slide source labels remain historical paths until a later presentation revision. The edited v3 was not changed. Compatibility demo commands now read relocated policies through the modular implementation.

## Full reproduction alignment

The completed isolated reproduction matches all scientific evidence supporting slides 8–11 and the saved policies used by slide 12. The original presentation figures remain valid for the retained original run. Thirty-one current implementation tests are additional refactor checks, separate from the nine tests reported for the original study. Timing and memory for a new execution must not be substituted into the presentation as original measurements. visual_plan.md supplies source-backed candidate diagrams/charts and placement options; the edited v3 remains unchanged.
