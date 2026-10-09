# Experiment evidence

original_run/ retains all 187 original output files byte-for-byte. Their old-to-new paths and hashes are in ../docs/relocation_checks.json. The scientific artifacts include policy JSON, training episode CSVs and curves, validation and final evaluation CSVs, decision traces, summaries, and measured runtime/memory provenance. Historical logs and demonstration exports remain original evidence.

reproductions/ holds separate executions of the modular implementation. Each new experiment must use a fresh directory. Never write analysis outputs into original_run/. New-run logs and metadata describe actual new execution; they do not replace the original study.

figures/ is reserved for presentation visuals with explicit source files and denominators. The original slide deck is outside the code repository.
