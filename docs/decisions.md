# Codebase and implementation decisions

Entries record technical choices, rationale, implementation consequences, and verification status.

## October 9, 2026 — Modular source layout

Decision: separate reusable Python modules under `src/edge_recovery/`, execution entry points under `scripts/`, tests under `tests/`, experiment configuration under `config/`, retained evidence under `results/`, and technical documentation under `docs/`.

Rationale: the current `recovery.py` combines simulation, controllers, training, evaluation, and orchestration. Separating these responsibilities makes dependencies explicit and permits focused behavior checks.

Consequence: imports, repository paths, CLI entry points, and evidence references will change. State, action, reward, filter, scenario, and learning behavior remain the reference behavior.

Status: environment, safety filter, reward, and scenario modules are extracted and verified. Controller, training, and evaluation extraction checks now pass. Entry-point migration and full orchestration are pending.

## October 9, 2026 — Submitted design as implementation baseline

Decision: retain the submitted Part 1 DOCX in `docs/plan/`, accompanied by a paragraph-text extraction. The DOCX is authoritative; the extraction supports text inspection.

Rationale: implementation assumptions and experimental requirements need a stable source that can be checked against code and evidence.

Consequence: `docs/experiment_protocol.md` maps design requirements to the original implementation and refactor acceptance conditions. The original document is preserved without revision.

Status: the copied DOCX matches the submitted source byte-for-byte; its SHA-256 is recorded in `docs/reference_manifest.json`.

## October 9, 2026 — Preserve original evidence and isolate reproduction

Decision: retain original experiment artifacts and write refactored reproduction outputs to a separate directory. Preserve existing Git history.

Rationale: structural changes must be evaluated against the measured reference run without replacing the evidence used in the presentation.

Consequence: compare policies, episode records, evaluation rows, traces, and summaries. Source paths, hashes, execution time, and resource metadata may differ and require explicit accounting. Matching aggregate results alone does not establish behavioral equivalence.

Status: all 199 original tracked files were inventoried. The foundation check found only the intended README change. Evidence relocation and full reproduction are pending.

## October 9, 2026 — Keep one editable presentation source

Decision: keep the editable presentation in the course presentation directory and maintain its code/evidence mapping in `docs/presentation_alignment.md`.

Rationale: duplicate editable decks can diverge from the implementation and measured evidence.

Consequence: evidence-path changes and test-count changes must be reconciled with the presentation after verification. The reference deck is identified by hash rather than copied into the codebase.

Status: the current v3 deck was inspected and left unchanged during foundation construction.

## October 9, 2026 — Simulator boundaries and equivalence checks

Decision: keep structural execution and its violation checker in environment.py, actual filtered execution and reward in safety_filter.py, and scenario construction with development-only feasibility search in scenarios.py.

Rationale: both learning conditions need the same physical execution rules. Filtering changes what executes while preserving the proposed command for later Q updates. Keeping those responsibilities explicit prevents invalid commands from being counted as prohibited executable proposals.

Consequence: immutable state, command indices, physical target order, failure health flags, budget accounting, reward weights, and audit field names retain their original meaning. The original implementation stays available as the behavioral reference during extraction.

Status: boundary tests and differential comparisons pass. All retained evaluation transitions replay identically, and original output hashes remain unchanged. This verifies the simulator extraction within the exercised state space; controller equivalence and full experiment reproduction remain pending.

## October 9, 2026 — Separate learning from policy evaluation

Decision: controllers.py owns greedy selection, the fixed rule baseline, and proposed-command Q updates. training.py owns seeded exploration and learned-policy artifacts. evaluation.py runs fixed policies without exploration or table mutation. runtime.py isolates platform-dependent process memory reporting.

Rationale: training changes action-value estimates, whereas evaluation measures the resulting policy. Keeping these workflows separate makes the RL learning loop and the experimental boundaries explicit.

Consequence: the original random draw order, epsilon expression, sparse table insertion order, JSON format, greedy ties, and validation ranking are retained. Unseen states still select restart from zero values. No fallback controller or held-out-driven redesign is introduced. Process timing and RSS are measurements, not deterministic equivalence targets.

Status: eight development cases produce byte-identical episode, curve, and policy artifacts. All 20 saved final policies reproduce the retained 420 evaluation rows and 2,832 traces without table updates. Full-budget experiment orchestration and reproduction remain pending.

## October 9, 2026 — Isolated experiment execution and evidence analysis

Decision: require a fresh output directory, validate source configuration against the frozen design, and save the validation-based selection before final held-out evaluation. Analysis and policy checks read original evidence without writing to it.

Rationale: rerunning an experiment must not replace the evidence used in the presentation. Explicit configuration checks prevent an edited manifest or unsupported model constant from silently changing the experiment.

Consequence: existing output destinations are rejected, including nested paths inside the original run. Each new run retains configuration snapshots and a source-hash identity record. Development budgets are identified separately from full reproduction. Episode and trace summaries retain their original serialization.

Status: 31 tests pass. Read-only modular analysis and policy verification reproduce all five original JSON check/summary records. Full-budget execution is pending evidence relocation.
