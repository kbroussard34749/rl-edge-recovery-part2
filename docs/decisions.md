# Codebase and implementation decisions

Entries record technical choices, rationale, implementation consequences, and verification status.

## October 9, 2026 — Modular source layout

Decision: separate reusable Python modules under `src/edge_recovery/`, execution entry points under `scripts/`, tests under `tests/`, experiment configuration under `config/`, retained evidence under `results/`, and technical documentation under `docs/`.

Rationale: the original `recovery.py` combined simulation, controllers, training, evaluation, and orchestration. Separating these responsibilities makes dependencies explicit and permits focused behavior checks.

Consequence: imports, repository paths, CLI entry points, and evidence references use the modular layout. State, action, reward, filter, scenario, and learning behavior remain the reference behavior.

Status: simulator, controller, training, evaluation, and orchestration modules are implemented and verified. Root compatibility entry points use the modular implementation. Dedicated demo-module restructuring was completed and checked on October 11, 2026; its commit check-in is pending.

## October 9, 2026 — Submitted design as implementation baseline

Decision: retain the submitted Part 1 DOCX in `docs/plan/`, accompanied by a paragraph-text extraction. The DOCX is authoritative; the extraction supports text inspection.

Rationale: implementation assumptions and experimental requirements need a stable source that can be checked against code and evidence.

Consequence: `docs/experiment_protocol.md` maps design requirements to the original implementation and refactor acceptance conditions. The original document is preserved without revision.

Status: the copied DOCX matches the submitted source byte-for-byte; its SHA-256 is recorded in `docs/reference_manifest.json`.

## October 9, 2026 — Preserve original evidence and isolate reproduction

Decision: retain original experiment artifacts and write refactored reproduction outputs to a separate directory. Preserve existing Git history.

Rationale: structural changes must be evaluated against the measured reference run without replacing the evidence used in the presentation.

Consequence: compare policies, episode records, evaluation rows, traces, and summaries. Source paths, hashes, execution time, and resource metadata may differ and require explicit accounting. Matching aggregate results alone does not establish behavioral equivalence.

Status: the foundation inventory covers 199 original tracked files. All 187 original output files retain their hashes after relocation. The complete isolated reproduction matches the original scientific evidence.

## October 9, 2026 — Keep one editable presentation source

Decision: keep the editable presentation in the course presentation directory and maintain its code/evidence mapping in `docs/presentation_alignment.md`.

Rationale: duplicate editable decks can diverge from the implementation and measured evidence.

Consequence: evidence-path changes and test-count changes must be reconciled with the presentation after verification. The reference deck is identified by hash rather than copied into the codebase.

Status: the current v3 deck was inspected and left unchanged during foundation construction.

## October 9, 2026 — Simulator boundaries and equivalence checks

Decision: keep structural execution and its violation checker in environment.py, actual filtered execution and reward in safety_filter.py, and scenario construction with development-only feasibility search in scenarios.py.

Rationale: both learning conditions need the same physical execution rules. Filtering changes what executes while preserving the proposed command for later Q updates. Keeping those responsibilities explicit prevents invalid commands from being counted as prohibited executable proposals.

Consequence: immutable state, command indices, physical target order, failure health flags, budget accounting, reward weights, and audit field names retain their original meaning. The original implementation remains under `tests/reference/recovery_reference.py` as the behavioral reference.

Status: boundary tests and differential comparisons pass. All retained evaluation transitions replay identically, and original output hashes remain unchanged. The comparison verifies simulator equivalence within the exercised state space. Controller checks and the full experiment reproduction provide separate supporting evidence.

## October 9, 2026 — Separate learning from policy evaluation

Decision: controllers.py owns greedy selection, the fixed rule baseline, and proposed-command Q updates. training.py owns seeded exploration and learned-policy artifacts. evaluation.py runs fixed policies without exploration or table mutation. runtime.py isolates platform-dependent process memory reporting.

Rationale: training changes action-value estimates, whereas evaluation measures the resulting policy. Keeping these workflows separate makes the RL learning loop and the experimental boundaries explicit.

Consequence: the original random draw order, epsilon expression, sparse table insertion order, JSON format, greedy ties, and validation ranking are retained. Unseen states still select restart from zero values. No fallback controller or held-out-driven redesign is introduced. Process timing and RSS are measurements, not deterministic equivalence targets.

Status: eight development cases produce byte-identical episode, curve, and policy artifacts. All 20 saved final policies reproduce the retained 420 evaluation rows and 2,832 traces without table updates. The full-budget experiment is separately verified in `full_reproduction_checks.json`.

## October 9, 2026 — Isolated experiment execution and evidence analysis

Decision: require a fresh output directory, validate source configuration against the frozen design, and save the validation-based selection before final held-out evaluation. Analysis and policy checks read original evidence without writing to it.

Rationale: rerunning an experiment must not replace the evidence used in the presentation. Explicit configuration checks prevent an edited manifest or unsupported model constant from silently changing the experiment.

Consequence: existing output destinations are rejected, including nested paths inside the original run. Each new run retains configuration snapshots and a source-hash identity record. Development budgets are identified separately from full reproduction. Episode and trace summaries retain their original serialization.

Status: 31 tests pass. Read-only modular analysis and policy verification reproduce all five original JSON check/summary records. Full-budget execution is now verified after evidence relocation.

## October 9, 2026 — Canonical evidence paths and compatibility entry points

Decision: relocate original outputs to results/original_run/, place design files in config/, preserve the original implementation in tests/reference/, and make root commands thin compatibility entry points to modular code.

Rationale: one canonical original-evidence directory prevents competing result copies. Comparison scripts need a frozen source reference that does not accidentally resolve to the new implementation.

Consequence: every moved original artifact retains its hash. Compatibility demo commands read relocated policies; experiment commands require new output destinations. The source package and CLI scripts use explicit checkout paths. pyproject.toml describes a dependency-free Python 3.12 package; source commands do not require installation.

Status: all 187 original output files and both design files match their original hashes after relocation. All 31 tests and both extraction-comparison scripts pass with the new paths. Full reproduction now matches the original scientific evidence.

## October 9, 2026 — Verify the complete experiment against retained artifacts

Decision: reproduce the full frozen experiment under Python 3.12.14 and compare policies, episode histories, curves, selection, final evaluation, and analysis rather than only aggregate success rates.

Rationale: a refactor can preserve headline outcomes while changing random draw order, updates, or intermediate behavior. Complete deterministic-artifact comparison provides stronger evidence of preserved implementation behavior.

Consequence: 136 scientific files and both design snapshots must match exactly. Training, pilot and provenance records are compared on scientific fields; execution time and cumulative process RSS remain separately reported measurements. Run identity hashes refer to the executed package source. Package-level comments describe responsibilities rather than temporary build status.

Status: all 42 model runs reproduce; the 800,000-episode training budget and 2,000 pilot episodes are complete. Both learners select alpha .1. All 420 final evaluation rows and 2,832 traces match. Original output hashes remain unchanged. Reproduction time and memory differences are recorded without implying performance improvement.

## October 9, 2026 — Preserve CSV line endings in Git

Decision: disable Git text normalization for CSV artifacts and treat carriage returns as valid line-ending characters in whitespace checks.

Rationale: the original and reproduced CSV writers use CRLF terminators. Normalizing those files during checkout would change the bytes used for artifact identity checks.

Consequence: .gitattributes preserves the measured serialization without rewriting either evidence set. Other whitespace checks remain enabled.

Status: committed artifact bytes are checked against worktree hashes; the full reproduction and original evidence remain unchanged.

## October 11, 2026 — Dedicated simulation demonstration

Decision: place retained-policy episode execution and the boundary fixture in demo.py, local HTTP delivery in demo_web.py, and browser markup in demo.html. Dedicated scripts provide terminal, fixture, and browser commands; root commands remain compatible.

Rationale: the demo should execute the measured simulator without duplicating recovery logic or relying on the compatibility namespace. Distinguishing learned-state coverage from rule behavior prevents the browser from implying that the baseline was trained.

Consequence: episodes read final policies for seeds 1000–1009 and execute fixed-policy evaluation. Display-only loads, availability, and coverage fields augment trace copies. Terminal commands retain original audit fields. The server binds to 127.0.0.1; no infrastructure controls are present. The fixture remains separate from benchmark results.

Status: 37 tests pass, including six demonstration checks. All 420 retained final episodes and 2,832 decision traces match; the fixture text matches its retained export. The original 187 outputs and full-reproduction scientific records remain unchanged. Browser inspection confirms training recovery, held-out budget exhaustion, and rule recovery. Recording delivery remains unverified.
