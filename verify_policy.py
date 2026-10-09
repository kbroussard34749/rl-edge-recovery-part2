"""Read-only compatibility command for retained policy verification."""

import json
import recovery
from edge_recovery.policy_verification import verify_policy

if __name__ == "__main__":
    print(json.dumps(verify_policy(recovery.ORIGINAL_RUN), indent=2))
