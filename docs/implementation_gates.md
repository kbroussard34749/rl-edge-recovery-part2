# Implementation stages and verification evidence

The implementation was reorganized through separate, verifiable increments on October 9, 2026. The original experiment predates this refactor and remains the behavioral reference at commit `5b5a255`. The sequence below records completed technical stages; it does not imply that later checks preceded the original experiment.

| Stage | Acceptance criterion | Verified result | Commit |
|---|---|---|---|
| Foundation | Preserve the submitted design and identify reference artifacts | Submitted DOCX copied without changes; 199 original tracked files inventoried | `be7a681` |
| Simulator | Preserve physical execution, filtering, reward, and scenarios | 17 tests at this stage; 217 physical states compared; 2,832 recorded decisions replayed | `c4c50f0` |
| Controllers | Preserve Q updates, random draws, policy selection, and evaluation | 25 tests at this stage; eight paired development cases; 420 evaluation rows and 2,832 traces matched | `bcdfdf7` |
| Orchestration | Separate tuning from held-out testing and prevent evidence overwrite | 31 tests; freeze-before-testing control-flow check; five analysis records reproduced | `3e56ca0` |
| Evidence relocation | Retain original bytes under canonical paths | All 187 output files and both design files match reference hashes | `ac23ec6` |
| Full reproduction | Execute the complete design and compare deterministic artifacts | 42 model runs; 800,000 training episodes; 2,000 pilot episodes; 136 exact artifact matches and two matching design snapshots | `b217e25` |
| Git serialization | Preserve CSV line endings across checkouts | CSV normalization disabled; 323 original/reproduced artifact blobs checked against worktree bytes | `fe74d87` |

The test counts describe successive stages, not independent replications. The original study used nine tests. The refactor checkpoint contains 31 tests. The October 11 demonstration increment adds six checks, bringing the current suite to 37.

## Verification boundaries

Simulator comparisons cover structural execution, rewards, audit fields, and terminal accounting within the exercised state space. Controller comparisons use eight temporary 601-episode cases per implementation, totaling 4,808 development episodes each. These checks preserve the random sequence and serialized policy behavior but do not replace the full-budget experiment.

The full reproduction uses Python 3.12.14 and the package source identified in `run_identity.json`. Policies, episode histories, curves, validation, final evaluation, and analysis match the original evidence. Execution time and cumulative process memory are reported separately because they depend on runtime conditions.

## Current scope

The source modules, configuration, analysis, and isolated reproduction are complete. Root compatibility commands support the local agent demonstration. Dedicated demo-module restructuring is implemented and verified in the October 11 check-in below, awaiting commit approval. A refreshed distribution package, remote synchronization, instructor access, and recording validation remain outside the completed stages above. Repository checks do not establish presentation delivery or submission.

The supporting records are [simulator validation](simulator_validation.md), [controller validation](controller_validation.md), [full reproduction validation](full_reproduction_validation.md), and their machine-readable check files.

## Demonstration gate check-in — October 11, 2026

Keith requested continuation of the remaining gates on October 11. This authorizes preparation and verification of the demonstration increment. Per AGENTS.md, commit approval and approval to advance to release remain separate checkpoints.

Prepared: reusable demo and browser modules, dedicated terminal/browser/fixture scripts, compatible root commands, HTML package data, six focused demo tests, current v4 evidence mapping, and a concise recording sequence. The scientific learning and simulator modules, configurations, retained results, and presentation file are unchanged by this increment.

Verified: 37 tests pass. Demo evaluation matches 420 retained episode records and 2,832 decision traces. The boundary fixture's serialized output matches the original export. HTTP checks cover loopback binding, scenario listing, valid episodes, invalid inputs, and unknown routes. Browser inspection confirms filtered node_0 recovery in three steps, filtered cpu_4 failure at step 20, and rule cpu_4 recovery in one step. All 187 original outputs retain reference hashes, and the read-only full-reproduction verifier passes with 136 exact scientific-artifact matches.

Evidence: [demo validation](demo_validation.md) and demo_checks.json. Historical approvals and the original six-gate sequence remain available in [the preserved gate history](gate_history_before_demo.md).

Proposed commit: `Extract and verify the simulation demonstration`.

Approval received October 11, 2026 for the exact 20-file demonstration commit and advancement to release-package preparation. This approval does not include replacing the existing ZIP, pushing GitHub, or changing instructor access.

Status at commit preparation: verified and approved for commit. The approved file scope is recorded in demo_validation.md. Earlier unrelated documentation revisions remain outside this demonstration commit. No release package replacement, push, instructor invitation, recording, or submission is included.

Next proposed increment, after approval: prepare a new candidate distribution package and verify its extracted contents and commands. ZIP replacement and GitHub synchronization require explicit approval for those actions; instructor access remains on hold.
