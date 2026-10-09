# Source-backed visuals for the project presentation

These visuals explain the implementation, present measured evidence, and support the conclusions. Quantitative charts use original scientific artifacts or verified reproduction files. Diagrams explain the model and code; they are not performance evidence. No edited deck or recording is created by this plan.

## Recommended set

| Visual | Audience question | Actual source | Potential presentation placement |
|---|---|---|---|
| Three-node cluster diagram | What is recovering, and why do actions affect later choices? | environment.py State/DEMAND/available; submitted Part 1 | Slide 2 or 4 |
| Recovery learning loop | How does the agent learn rather than follow fixed rules? | training.py; controllers.py update; safety_filter.py step | Slide 6 |
| Module workflow map | How do the code files work together? | src/edge_recovery modules and run_experiment.py | Slide 7 |
| Training/validation/test protocol | How are selection and final testing separated? | experiment.py; config/; frozen_protocol.json | Slide 8 |
| Learning return curve | Does exploratory training return change? | original_run/final/*/*/curve.json or episodes.csv | Slide 9 |
| Recovery comparison and per-fault chart | Where does learning succeed or fail against the baseline? | evaluation.csv; seed_aggregates.json; per_fault.json | Slides 10–11 |
| Agent trace storyboard | What does a working policy actually do? | traces.jsonl; saved seed-1000 policies; simulator | Slide 12 before or alongside live demo |
| Unseen-state reasoning chain | Why does held-out performance fail? | policy tables; unseen counts; greedy tie code; cpu_4 traces | Slide 14 |
| Filter boundary comparison | How does a prohibited proposal differ from execution? | boundary_demo.py development fixture and step audit fields | Slide 12, separately labeled development test |
| Part 1-to-evidence matrix | Which planned objectives are supported or unresolved? | submitted Part 1; experiment_protocol.md; summary.json | Conclusion or appendix |

For a 13–15-minute presentation, prioritize the learning loop, module workflow, per-fault results, and trace storyboard. Replace dense text with these visuals rather than adding every candidate as a new slide. Rehearsal will establish the actual duration after any revision.

## Learning loop: proposed diagram

```mermaid
flowchart LR
    S[Observe exact cluster state] --> Q[Explore or choose highest Q value]
    Q --> P[Propose one of nine commands]
    P --> M[Model structural execution]
    M --> F[Apply fixed filter when enabled]
    F --> O[Actual next state and reward]
    O --> U[Update value of proposed command]
    U --> S
    O --> T[Stop on recovery or budget exhaustion]
```

Show the Q update beside the loop. During evaluation, remove exploration and the update arrow. The rule controller has a separate fixed ranking, and the safety filter has fixed checks; neither component learns. The physical model determines the affected service. The learner selects the command within that model.

## Code workflow: proposed diagram

```mermaid
flowchart TD
    C[config/experiment.json and scenarios.json] --> E[experiment.py]
    E --> SC[scenarios.py: validate starts]
    E --> TR[training.py: repeated episodes]
    TR --> CO[controllers.py: selection and Q update]
    TR --> SF[safety_filter.py: actual outcome and reward]
    SF --> EN[environment.py: resources and availability]
    E --> EV[evaluation.py: fixed policies]
    EV --> CO
    EV --> SF
    EV --> R[results/: episodes, policies, traces]
    R --> A[evidence.py and policy_verification.py]
    A --> V[Verified results for presentation]
```

Use functions and plain-language responsibilities as labels. This is a conceptual dependency/workflow diagram, not a literal call graph of every helper.

## Quantitative evidence design

Recovery chart: grouped bars for filtered Q, unshielded Q, and rule, with training and held-out splits. Learner rates are summarized within each of ten seeds; held-out denominators are eight configurations per seed. Rule evaluation uses each configuration once. Show 2/8 versus 8/8, not only percentages. The hand-designed configurations are not a sampled population.

Per-fault chart: four grouped categories, crash/CPU/memory/node, with the same three controllers and a zero-to-100% axis. Each held-out fault contains two configurations per seed. This makes the crash-only learned recovery visible. Seed SD zero is descriptive, not a confidence interval.

Training curve: use the same 1,000-episode bins as the existing slide if replacing it. Summarize each seed before averaging across seeds and label exploratory return. If the two curves overlap, say so and use different line styles. Do not claim convergence or held-out improvement from this curve.

Metric comparison: keep steps, return, and critical outage in separate panels or a concise table because their units differ. Critical outage means post-command service-decision intervals, not seconds. Include failures in all-episode step averages. A chart of zero executed violations must disclose that all controllers also have zero prohibited proposals in final evaluation.

## Actual trace examples

| Case | Verified commands | Steps | Return | Interpretation |
|---|---|---|---|---|
| Filtered node_0, seed 1000 | restore_N3, restore_N2, restore_N2 | 3 | −26 | Learned training recovery; rewards −16, −6, −4 |
| Filtered cpu_4, seed 1000 | restart repeated to exhaustion | 20 | −480 | Unseen-state tie selects a structurally ineffective command |
| Rule cpu_4 | migrate_N1 | 1 | −4 | Fixed rule ranking recovers this held-out start |

The storyboard can show the initial layout and each recorded resulting layout, availability, command, and reward. node_0 is training evidence, not proof of transfer. cpu_4 is one failure example, not the aggregate held-out return (−360.5). The development filter fixture is outside final evaluation.

## Reasoning and conclusion

Use the chain: held-out exact state is absent from the Q-table → all nine values default to zero → fixed tie chooses restart → persistent overload remains → budget is exhausted. Every link is supported by policy lookup, controllers.py, and saved traces. This is the implemented explanation; state abstraction or a fallback remains proposed future work.

The Part 1 matrix can mark: inspectable model and specified constraint checks supported; training recovery supported; 90% held-out planning target not achieved; filter advantage not established; production integration not tested. Keep measured findings separate from proposed improvements.

## Integration limits

The current v3 remains the editable presentation source. Its source labels still use historical outputs/ paths; docs/presentation_alignment.md maps those to results/original_run/. New diagrams or charts require a separately versioned deck and visual inspection. Code/figure improvements do not establish face/voice recording coverage, presentation duration, instructor access, or submission.
