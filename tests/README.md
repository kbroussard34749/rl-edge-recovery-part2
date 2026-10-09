# Implementation checks

Run python3 -m unittest discover -s tests -v from the repository root. Tests cover physical boundaries, dependency behavior, action filtering, reward/terminal accounting, Q updates, unseen-state ties, split selection, original-evidence write protection, and selection before held-out evaluation.

reference/recovery_reference.py preserves the original implementation byte-for-byte for comparison scripts. It is not the active implementation. test_recovery.py retains the original nine test cases and now exercises the modular compatibility API. Additional focused tests exercise extracted modules directly. Counts and outcomes for each increment are recorded separately from the original study's nine-test result.
