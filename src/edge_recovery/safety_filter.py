"""Turn a proposed command into an executed command and a learning outcome.

The workflow is: model the proposal, apply the fixed filter when enabled,
measure the actual next state, and return its reward and termination flag.
The returned audit fields keep the proposal separate from what executed.
A blocked command can preserve a constraint while leaving the outage unresolved.
"""

from dataclasses import replace
from functools import lru_cache

from .environment import ACTIONS, State, available, success, transition


@lru_cache(maxsize=None)
def step(state: State, action: int, filtered: bool) -> tuple:
    """Return actual next state, reward, termination flag, and audit fields.

    A prohibited executable proposal becomes wait in the filtered condition.
    The reward retains the prohibited-proposal penalty even when execution is
    blocked. The learner later updates the proposed action using this actual
    transition and reward. All conditions share structural rules and checks.
    """
    if state.left <= 0 or success(state):
        raise ValueError("Cannot step a terminal state")

    candidate, valid, prohibited, cost = transition(state, action)
    replaced = bool(filtered and prohibited)
    executed = 8 if replaced else action
    # Waiting preserves the physical state but consumes the same action budget.
    next_state = replace(state, left=state.left - 1) if replaced else candidate
    executed_cost = 0 if replaced else cost

    availability = available(next_state)
    won = success(next_state)
    # A successful recovery on the last command does not incur failure penalty.
    failed = next_state.left == 0 and not won
    critical_unavailable = int(not availability[0]) + int(not availability[1])
    batch_unavailable = int(not availability[2])
    throttled_batch = int(availability[2] and next_state.throttled)
    # Reward follows Part 1: −1−10Uc−2Ub−B−I−5P−20F. Uc and Ub measure
    # post-command outages; B penalizes operational throttled batch; I is the
    # executed intervention cost; P penalizes the prohibited proposal; F marks
    # failed budget exhaustion. These are model weights, not measured costs.
    reward = (
        -1 - 10 * critical_unavailable - 2 * batch_unavailable - throttled_batch
        - executed_cost - 5 * int(prohibited) - 20 * int(failed)
    )
    info = dict(
        proposed=ACTIONS[action], executed=ACTIONS[executed],
        replaced=int(replaced), invalid=int(not valid),
        prohibited=int(prohibited), violations=int(prohibited and not replaced),
        cost=executed_cost, critical_unavailable=critical_unavailable,
        batch_unavailable=batch_unavailable, throttled=throttled_batch,
        success=int(won),
    )
    return next_state, reward, bool(won or failed), info
