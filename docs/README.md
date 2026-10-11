# Technical documentation

The documentation connects the submitted design to implemented behavior, measured outcomes, and presentation requirements. The original plan and machine-generated check records remain source evidence. Revised prose describes current implementation status and identifies the scope of historical checks.

| Record | Purpose |
|---|---|
| [Submitted plan](plan/Part_1_Submitted_Text.md) and accompanying DOCX | Unchanged Part 1 design baseline; the DOCX controls formatting and source wording |
| [Experiment protocol](experiment_protocol.md) | Model, learning design, experimental sequence, deviations, and evidence paths |
| [Implementation decisions](decisions.md) | Technical choices, rationale, consequences, and verification status |
| [Implementation stages](implementation_gates.md) | Completed increments and acceptance evidence |
| [Simulator validation](simulator_validation.md) | Physical, filter, reward, scenario, and terminal comparisons |
| [Controller validation](controller_validation.md) | Q update, policy selection, short paired training, and evaluation comparisons |
| [Full reproduction validation](full_reproduction_validation.md) | Complete workload, exact artifact comparisons, runtime differences, and limitations |
| [Demo validation](demo_validation.md) | Verified demonstration cases, commands, and recording sequence |
| [Release validation](release_validation.md) | Candidate-package scope, extracted checks, and approval boundary |
| [Presentation alignment](presentation_alignment.md) | Eight-section mapping, slide evidence, and reconciliation items |
| [Visual plan](visual_plan.md) | Proposed diagrams, measured charts, trace examples, and interpretation limits |
| [References](references.md) | Selected bibliography and bounded source-inspection scope |
| [Documentation review](documentation_review.md) | Academic style, code/results consistency, and direction/rubric alignment |

Machine-readable records include `reference_manifest.json`, `relocation_checks.json`, `simulator_checks.json`, `controller_checks.json`, and `full_reproduction_checks.json`. Foundation, orchestration, and completion JSON files retain their checkpoint-specific status; a historical false or pending field does not describe the completed repository as a whole.

The original study used nine tests. Refactor stages reached 17, 25, and 31 tests; the October 11 demonstration suite adds six checks, bringing that checkpoint to 37. Release verification adds one archive-chronology check, bringing the current total to 38. These are successive implementation checks, not independent experimental replications. Current technical completion is supported by the full-reproduction record. Recording quality, instructor access, remote synchronization, package delivery, and submission require separate evidence.
