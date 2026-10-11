# Presentation alignment with implementation and evidence

The current v4 deck and rehearsal guide were checked on October 11, 2026 against the demonstration cases, canonical evidence paths, historical test-count wording, and Chapter 22 narration revision. Editable slides remain in the adjacent presentation directory. This record establishes content alignment; recording completion requires separate review.

| Slides | Required section or supporting content | Current implementation and evidence |
|---|---|---|
| 1–2 | Project introduction: motivation, sequential decisions, Part 1 objectives | Submitted Part 1 problem statement; `environment.py` |
| 3, 15 | Background and project context | Part 1 literature; `references.md`; Module 7 context |
| 4–6 | Methodology: state, actions, filter, reward, Q update | `environment.py`, `safety_filter.py`, `controllers.py`; `config/` |
| 7 | Implementation: sparse table, immutable state, caching, tools, changes | `training.py`, `experiment.py`; `experiment_protocol.md` |
| 8 | Experimental validation, tuning, and design freeze | Original `tests.log`; `scenario_validation.json`, `frozen_protocol.json`, `provenance.json` |
| 9 | Results: exploratory training curves | `results/original_run/final/*/*/curve.json` |
| 10–11 | Results and analysis: success, steps, outages, return, limits | `results/original_run/evaluation.csv`, `seed_aggregates.json`, `summary.json`, `per_fault.json` |
| 12 | Agent demonstration: learned recovery, held-out failure, rule comparison, filter fixture | Retained seed-1000 policies; `traces.jsonl`; `demo.py`; `demo_web.py`; `scripts/serve_demo.py`; `scripts/boundary_demo.py` |
| 13 | Ethical and practical considerations | Immediate-filter scope, restoration assumptions, simulation and deployment limits |
| 14 | Conclusion and future work | Measured generalization failure; exact lookup and fixed ties; proposed state abstraction and richer fault scenarios |
| 16 | AI assistance disclosure | Factual account of implementation, tests, execution, analysis, and presentation assistance |

## Verified consistency

Slides 4–7 describe the frozen model and implemented Q update accurately. Slides 8–11 use the original experiment evidence. The full isolated reproduction preserves all scientific artifacts supporting those results and the saved policies used in the demonstration. The displayed held-out outcomes remain 25% recovery for each learner and 100% for the rule controller.

The implementation has one learning controller. The three nodes do not constitute three learning agents. Module 7 supplies relevant context on multi-agent applications and scalability; it does not change the submitted single-agent project into MARL.

## Current v4 reconciliation

The October 11 v4 deck uses canonical results/original_run/ and config/ source labels. Slide 8 separates the original nine tests from the 31-test refactor checkpoint. The demonstration increment now adds six checks, bringing the current suite to 37. The deck's 31-test wording is a historical refactor count; the demo check-in does not rewrite the measured study or deck.

Slide 12 shows the seed-1000 training recovery, held-out cpu_4 failure, rule comparison, and separately labeled development boundary fixture. The current browser and terminal commands reproduce these cases. Slide 12's boundary_demo.py source label remains a working compatibility command.

The v4 methodology, held-out analysis, and future-work notes include the Chapter 22 revision. Slide 15 lists Russell and Norvig (2021). The rehearsal guide allocates 14:15, including 2:20 for slide 12; this is a target, not a measured recording. File hashes are recorded in demo_checks.json. The historical v3 identity in reference_manifest.json remains unchanged.

New-run timing and memory belong to the reproduction, not the original measurements. Browser demonstration verification is documented in [demo_validation.md](demo_validation.md). The 90-second demo sequence supports the current deck without establishing presentation delivery.

## Assignment boundaries

The deck contains the eight required content sections. Presentation delivery, explanation beyond reading slides, reflective analysis in narration, and the recorded working-agent demonstration require recording review. The required video is 13–15 minutes with slides, face, and voice throughout. ScreenPal is recommended; another recorder can satisfy the same conditions.

Repository accessibility requires verification in the instructor's access context. Local completeness and successful execution do not establish that access. The directions list video, slides, and repository while placing AI disclosure “in your written report.” The placement remains unresolved; no separate report requirement is inferred. The current deck and README contain factual disclosures.
