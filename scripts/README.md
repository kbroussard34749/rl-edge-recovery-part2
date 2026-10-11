# Execution commands

Run scripts from the repository root with Python 3.12. _bootstrap.py locates src/ without third-party installation.

- run_experiment.py --output PATH: full frozen experiment in a fresh directory; --episodes is development only.
- validate_scenarios.py: feasibility checks without training or evidence writes.
- analyze_results.py: seed-first summaries and transition replay, read-only by default. --run-dir PATH --write writes only to reproduction evidence.
- verify_policy.py: verify saved learned commands and unseen-state metrics, read-only by default.
- verify_simulator_equivalence.py: compare extracted simulator with frozen reference code and traces.
- verify_controller_equivalence.py: temporary paired training and retained-policy evaluation comparisons.

- demo_agent.py --controller filtered --scenario node_0: execute a saved final policy and print original audit fields; --seed selects 1000 through 1009.
- boundary_demo.py: print the harmful restore with and without filtering; this fixture is outside final evaluation.
- serve_demo.py: start the browser demo on this computer at port 8765; --port allows another local port.

Root compatibility commands delegate to the dedicated demo modules. Demonstration execution reads retained policies and writes no experiment evidence.

- verify_reproduction.py --run-dir PATH --output CHECK.json: strict reproduction verification in the executed checkout. For an extracted ZIP or copied checkout, add --archived-checkout; all scientific byte/source comparisons remain active, but filesystem timestamps do not establish execution order.
- package_release.py --output PATH: build a fresh source-checkout ZIP outside the repository and write its external byte-identity manifest. Existing packages are never replaced.
