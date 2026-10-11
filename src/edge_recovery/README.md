# Recovery implementation workflow

experiment.py coordinates the protocol. training.py selects a start and command, safety_filter.py executes the actual decision, and controllers.py updates the proposed command's Q value. environment.py defines physical rules and scenarios.py defines fixed starts. evaluation.py runs fixed policies; evidence.py and policy_verification.py check their records. runtime.py and paths.py handle resource accounting and file locations.

The model is simulation-only. Exact-state lookup and fixed greedy ties remain deliberate reference behavior. The filter checks specified immediate interventions; it is not a learned policy or a general safety guarantee. Module comments explain the workflow and assumptions.

Demo responsibilities are separate: demo.py loads saved policies and runs episodes or the development boundary fixture; demo_web.py serves the local browser; demo.html displays decision traces and model state. These use evaluation.py and the existing simulator without learning updates. The rule baseline has no learned-state coverage measure.
