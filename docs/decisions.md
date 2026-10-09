# Codebase and implementation decisions

Entries record technical choices, rationale, implementation consequences, and verification status.

## October 9, 2026 — Modular source layout

Decision: separate reusable Python modules under `src/edge_recovery/`, execution entry points under `scripts/`, tests under `tests/`, experiment configuration under `config/`, retained evidence under `results/`, and technical documentation under `docs/`.

Rationale: the current `recovery.py` combines simulation, controllers, training, evaluation, and orchestration. Separating these responsibilities makes dependencies explicit and permits focused behavior checks.

Consequence: imports, repository paths, CLI entry points, and evidence references will change. State, action, reward, filter, scenario, and learning behavior remain the reference behavior.

Status: package foundation exists. Module extraction and entry-point migration are pending.

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
