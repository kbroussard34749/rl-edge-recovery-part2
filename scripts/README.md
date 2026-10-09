# Execution commands

Run scripts from the repository root with Python 3.12. _bootstrap.py locates src/ without third-party installation.

- run_experiment.py --output PATH: full frozen experiment in a fresh directory; --episodes is development only.
- validate_scenarios.py: feasibility checks without training or evidence writes.
- analyze_results.py: seed-first summaries and transition replay, read-only by default. --run-dir PATH --write writes only to reproduction evidence.
- verify_policy.py: verify saved learned commands and unseen-state metrics, read-only by default.
- verify_simulator_equivalence.py: compare extracted simulator with frozen reference code and traces.
- verify_controller_equivalence.py: temporary paired training and retained-policy evaluation comparisons.

Root compatibility commands remain available for the existing local demonstration. Dedicated demo entry-point migration is a later increment.
