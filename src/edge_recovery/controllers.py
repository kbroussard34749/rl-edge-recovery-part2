"""Choose recovery commands and update learned action values.

The learner estimates command values from rewards and subsequent states. The
rule controller instead uses a fixed ranking of permitted next states. Both
operate within the same physical model, which selects the affected service.
"""

from .environment import State, available, loads, transition


def greedy(values: list) -> int:
    """Select the highest-valued command, keeping the first command in a tie.

    Command zero is restart. Zero values for an unseen state therefore select
    restart. This preserves the original behavior and its transfer limitation;
    the refactor does not add a rule fallback or change held-out decisions.
    """
    return max(range(9), key=lambda action: values[action])


def rule(state: State) -> int:
    """Rank permitted next states by outages, overload, cost, and command order.

    The ranking is lexicographic: a lower critical outage count takes priority
    over every later term. The controller checks each structurally valid command
    and rejects prohibited outcomes before ranking. It learns no parameters.
    """
    candidates = []
    for action in range(9):
        next_state, valid, prohibited, cost = transition(state, action)
        if not valid or prohibited:
            continue
        availability = available(next_state)
        cpu, mem = loads(next_state)
        overloaded_nodes = sum(
            state.health[node] and (cpu[node] > 10 or mem[node] > 10)
            for node in range(3)
        )
        ranking = (
            int(not availability[0]) + int(not availability[1]),
            overloaded_nodes, int(not availability[2]), cost, action,
        )
        candidates.append((ranking, action))
    return min(candidates)[1]


def update(q: dict, state: State, action: int, reward: float,
           next_state: State, done: bool, alpha: float, gamma: float = .95):
    """Update the proposed command using the actual transition and reward.

    The sparse table stores only visited states, with nine initially zero values
    per state. Future value is discounted by gamma; alpha determines how much
    this observation changes the estimate. Terminal transitions bootstrap zero.
    A blocked proposal updates its own entry, not the wait command's entry.
    """
    values = q.setdefault(state, [0.] * 9)
    target = reward + (0 if done else gamma * max(q.get(next_state, [0.] * 9)))
    values[action] += alpha * (target - values[action])
