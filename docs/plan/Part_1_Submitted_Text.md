# Submitted Part 1 — text extraction

Extracted from the accompanying unchanged submitted DOCX on October 9, 2026. Paragraph text is preserved; Word layout is not reproduced. The DOCX controls if formatting or interpretation differs. Future-tense passages describe the October 4 plan, not completed evidence.

Q-Learning With a Safety Filter for Fault Recovery in a Simulated Edge Cluster



Keith G. Broussard

University of the Cumberlands

PhDAI-830-A01 Applied Machine Intelligence and Reinforcement Learning

Professor Atif Farid Mohammad

October 4, 2026



Q-Learning With a Safety Filter for Fault Recovery in a Simulated Edge Cluster

Part 1: Define the Problem

I propose a simulation to test whether tabular Q-learning with a deterministic safety filter can recover services in a small edge cluster while preventing specified harmful interventions. The agent will learn which recovery command to propose based on the current system state, considering future service availability and resource usage. Comparisons with unshielded Q-learning and a rule-based controller will test whether filtering preserves effective recovery. The project will remain in simulation and will not change the real infrastructure.

Edge services share limited resources and can have different priorities (Shi et al., 2016). A recovery action can solve one problem while creating another. Restarting can resolve a service crash, but it cannot remove persistent overload. Migration can relieve overload while placing the destination beyond capacity. Database failure also affects the dependent web service. These relationships make recovery a sequential decision problem rather than a classification task.

The objectives are to build an inspectable recovery model, compare learned decisions with practical rules, and distinguish successful service recovery from enforcement of action constraints. The project connects cumulative reward, exploration, value estimation, policy evaluation, and generalization to a manageable discrete task. Tabular learning makes the decisions easier to examine before introducing neural architectures. The study will not assume that learning is better than a rule controller.

Part 2 Review Relevant Literature

Kaelbling et al. (1996) explain how delayed rewards and state representation shape reinforcement learning. Watkins and Dayan (1992) establish tabular Q-learning under convergence conditions that do not guarantee success within a finite training budget. These foundations support estimating the future value of recovery commands while making placement, node health, resource demand, and remaining recovery time explicit.

García and Fernández (2015) distinguish safety approaches involving optimization and exploration. Alshiekh et al. (2018) demonstrate how shielding can intervene in action selection. A penalty discourages a harmful command, whereas a correctly implemented filter prevents its execution. The proposed immediate checks adapt that separation without claiming the formal guarantees of a synthesized temporal-logic shield. A blocked action followed by waiting can preserve a constraint while leaving the outage unresolved.

Mao et al. (2019) evaluate learned cluster scheduling against heuristics using simulation and real workloads. Their approach supports credible comparisons and attention to simulator limitations, although scheduling results cannot predict recovery performance. Candea et al. (2004) connect inexpensive recovery to recoverable-state assumptions. Their microreboot study supports examining intervention costs, but it does not establish the effectiveness of simulated migration or database restoration. Shi et al. (2016) supply the edge-computing context of service priority, resource sharing, and reliability.

Patterson et al. (2024) support separate tuning and testing, comparable experimental budgets, and careful reporting of uncertainty. Together, these eight sources guide a bounded application of established methods. The contribution will be a transparent comparison of recovery decisions and safety interventions within a single defined model, rather than a claim that shielded Q-learning is new or universally superior.

Part 3: Describe the RL Methodology

The proposed Python simulator will contain three nodes, each with CPU and memory capacities of 10 abstract units. Web, database, and batch instances will require (3, 2), (4, 4), and (2, 3) CPU and memory units. Each logical service will have one instance. Batch throttling will reduce its CPU demand to 1 while leaving memory demand unchanged. Web availability will require both its own operation and an operational database.

One service crash, CPU overload, memory overload, or node failure will initiate each episode. Diagnosis and exact resource measurements will be supplied. Background demand will remain fixed afterward, and actions will be instantaneous. Services on overloaded nodes will be non-operational; failed nodes will remain failed. Restoration will assume data are recoverable outside the failed node. The model therefore excludes diagnosis, concurrent faults, transfer delays, transient migration overhead, and database consistency.

State will contain node health, background resource demand, service placement, and running status, batch throttling, and the remaining 20-action budget. Loads and availability will be derived from these values. Under the proposed deterministic transitions, this representation should contain the information used by the controller, the reward, and the filter; implementation checks will assess this assumption (Kaelbling et al., 1996). A shared helper will target the physically non-operational database first, then the web, and finally the batch.

Nine commands will cover five categories: restart, batch throttling, migration to each of three nodes, restoration to each node, and wait. Migration moves a running instance; restoration reactivates a crashed or lost instance; restart reactivates a crashed instance on its healthy host. Destination-specific commands allow the agent to try another node when a placement is blocked. Invalid commands become logged no-ops. Every command consumes one step.

The filter will reject executable proposals that exceed destination capacity or make a critical available service unavailable, substituting a wait. Unshielded learning will execute those proposals. All controllers will share structural rules and a violation checker. Logs will distinguish proposed, executed, replaced, and invalid commands. Adapting the integration discussion in Alshiekh et al. (2018), the learner will update the value of the proposed command using the actual resulting transition and reward. Waiting can preserve a constraint while failing recovery; external faults may still create unsafe states.

The provisional reward is r = −1 − 10Uc − 2Ub − B − I − 5P − 20F. Uc counts unavailable critical services; Ub indicates unavailable batch; B indicates operational throttled batch; P indicates a prohibited proposal; F indicates unsuccessful budget exhaustion. Executed cost I is 1 for restart or throttling, 3 for migration or restoration, and 0 otherwise. These weights are modeling choices. Success requires all services to be operational and healthy nodes to be within capacity. Success or budget exhaustion terminates recovery.

Following Watkins and Dayan (1992), Q-learning will use Q(s, a) ← Q(s, a) + α[r + γ max Q(s′,b) − Q(s, a)]. The maximum ranges over nine commands; terminal transitions use zero bootstrap. The filter will remain fixed. Q values will start at zero, γ at 0.95, and α candidates at 0.1 and 0.3. Exploration ε will decrease from 1.0 to 0.1 over 16,000 of 20,000 episodes, then remain 0.1. Exploration will sample all commands; greedy testing will use fixed tie-breaking and zero values for unseen states. Python and NumPy will support a sparse Q table, pandas will organize results, and Matplotlib will produce plots. No deep-learning framework is necessary for this discrete model.

Part 4: Present the Experimental Design

Twenty-four starting configurations, six per fault type, will be split into 12 training, four validation, and eight held-out test configurations. Each split will retain all four fault types. A development-only exhaustive search will verify a permitted recovery path within 20 steps for every retained configuration. Boundary tests will cover capacity, service dependencies, failed-node restoration, blocked proposals, and final-step termination. Search solutions will not become training labels.

Each learning condition will receive five tuning seeds per α candidate and ten fresh final-training seeds. Validation will prioritize recovery success, critical-service unavailability, and then return. Settings will be frozen before held-out testing. The maximum workload is 800,000 episodes and 16 million decision transitions. A runtime and memory pilot will determine whether equal budget reductions are necessary. The rule controller will rank permitted next states by critical outages, overload, batch outages, intervention cost, and fixed tie-breaking.

Every final policy will be tested on the same eight held-out configurations. Training configurations will also receive greedy evaluation as a separate diagnostic of learned behavior. The deterministic rule controller will be evaluated once per configuration; repeated identical episodes will not supply independent evidence. Learning results will be summarized within each training seed and then across seeds, with per-fault comparisons and visible failure cases.

Evaluation will measure recovery success, successful-recovery steps with denominators, all-episode steps, critical and batch unavailability, throttling, cumulative reward, intervention cost, prohibited proposals, executed violations, and filter intervention rate. Training curves, runtime, peak memory usage, state coverage, and unseen-state frequency will be used to assess stability and feasibility. Trends will describe learning behavior without claiming convergence. Differences in success and critical-service unavailability will be compared between shielded learning and both baselines. Exact tabular states may transfer poorly to held-out configurations; seed variability and that limitation will remain visible (Patterson et al., 2024).

Part 5 Timeline and Expected Outcomes

The proposed schedule allocates days 1–2 to model, transition, and scenario validation; days 3–4 to baseline checks and the runtime pilot; days 5–7 to validation-based tuning and design freeze; and days 8–10 to final comparisons, failure analysis, and report review. These are relative workdays, pending confirmation of the Part 2 schedule. Each phase will produce reviewable evidence before the next phase begins. Deliverables will include source, a fixed scenario manifest, configurations, logs, comparison plots, and documented limitations.

The agent is expected to learn recovery sequences that account for availability and resource costs. Correct filtering should yield zero executed prohibited actions under the specified checks. Fewer executed violations than unshielded learning is a testable expectation, although equality is possible. Recovery effectiveness requires separate evidence. A 90% held-out recovery rate is a planning target, not a promised result. Results supporting the goals would combine reliable recovery with fewer harmful interventions and acceptable outage, and intervention costs relative to the baselines.

The rule controller may outperform learning, and unseen states may limit tabular recovery. Such findings would guide model revision. Zero violations alone will not establish effective recovery, production safety, or generalization. Experiments are planned for Part 2.

AI Use Disclosure

OpenAI Codex assisted with literature searching, source appraisal, outlining, design refinement, and drafting from saved materials, including prior AI-generated brainstorming. My recorded scope choices and recovery reasoning informed the plan. Generated proposals and citations require my review. This disclosure does not claim independent verification of every source or completed experiments.

References

Alshiekh, M., Bloem, R., Ehlers, R., Könighofer, B., Niekum, S., & Topcu, U. (2018). Safe reinforcement learning via shielding. Proceedings of the AAAI Conference on Artificial Intelligence, 32(1), 2669–2678. https://doi.org/10.1609/aaai.v32i1.11797

Candea, G., Kawamoto, S., Fujiki, Y., Friedman, G., & Fox, A. (2004). Microreboot—A technique for cheap recovery. In Proceedings of the 6th symposium on operating systems design and implementation (OSDI ’04) (pp. 31–44). USENIX Association. https://www.usenix.org/conference/osdi-04/microreboot%E2%80%94-technique-cheap-recovery

García, J., & Fernández, F. (2015). A comprehensive survey on safe reinforcement learning. Journal of Machine Learning Research, 16(42), 1437–1480. https://jmlr.org/papers/v16/garcia15a.html

Kaelbling, L. P., Littman, M. L., & Moore, A. W. (1996). Reinforcement learning: A survey. Journal of Artificial Intelligence Research, 4, 237–285. https://doi.org/10.1613/jair.301

Mao, H., Schwarzkopf, M., Venkatakrishnan, S. B., Meng, Z., & Alizadeh, M. (2019). Learning scheduling algorithms for data processing clusters. In Proceedings of the ACM Special Interest Group on Data Communication (pp. 270–288). Association for Computing Machinery. https://doi.org/10.1145/3341302.3342080

Patterson, A., Neumann, S., White, M., & White, A. (2024). Empirical design in reinforcement learning. Journal of Machine Learning Research, 25(318), 1–63. https://jmlr.org/papers/v25/23-0183.html

Shi, W., Cao, J., Zhang, Q., Li, Y., & Xu, L. (2016). Edge computing: Vision and challenges. IEEE Internet of Things Journal, 3(5), 637–646. https://doi.org/10.1109/JIOT.2016.2579198

Watkins, C. J. C. H., & Dayan, P. (1992). Q-learning. Machine Learning, 8(3–4), 279–292. https://doi.org/10.1007/BF00992698
