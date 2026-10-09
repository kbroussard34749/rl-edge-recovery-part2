"""Model service recovery in a three-node simulated cluster.

The workflow starts with an observed state. loads() calculates resource use,
physical() checks whether each service operates, and available() applies the
web service's database dependency. transition() then models a proposed command.
The separate safety_filter.step() function decides whether to execute it and
calculates the reward from the actual outcome.

The model uses abstract resource units and instantaneous interventions. It does
not diagnose faults or control real infrastructure. These assumptions keep the
experiment small enough to inspect each recovery decision.
"""

from dataclasses import dataclass, replace
from functools import lru_cache


CAPACITY = 10
# Service indices remain web=0, database=1, batch=2 throughout the experiment.
DEMAND = ((3, 2), (4, 4), (2, 3))
# Ordering also defines command indices and the learner's eventual greedy ties.
ACTIONS = (
    "restart", "throttle_batch", "migrate_N1", "migrate_N2", "migrate_N3",
    "restore_N1", "restore_N2", "restore_N3", "wait",
)


@dataclass(frozen=True)
class State:
    """Complete observation and hashable key for exact tabular learning.

    health, cpu, and mem describe the three nodes; cpu/mem are fixed background
    demand. place and running describe the three services. left is part of the
    state because the same physical configuration has different future recovery
    opportunities near the end of the 20-command budget.
    """

    health: tuple
    cpu: tuple
    mem: tuple
    place: tuple
    running: tuple
    throttled: bool = False
    left: int = 20


@lru_cache(maxsize=None)
def loads(state: State) -> tuple:
    """Return node CPU and memory loads, including running hosted services.

    Failed nodes contribute no hosted-service demand. Overloaded healthy nodes
    still include running-service demand; losing availability does not itself
    remove a running instance. Batch throttling changes CPU only.
    """
    cpu = list(state.cpu)
    mem = list(state.mem)
    for service, node in enumerate(state.place):
        if state.running[service] and state.health[node]:
            cpu[node] += (
                1 if service == 2 and state.throttled else DEMAND[service][0]
            )
            mem[node] += DEMAND[service][1]
    return tuple(cpu), tuple(mem)


@lru_cache(maxsize=None)
def physical(state: State) -> tuple:
    """Return physical service operation before applying the web dependency."""
    cpu, mem = loads(state)
    return tuple(
        bool(
            state.running[service]
            and state.health[node]
            and cpu[node] <= CAPACITY
            and mem[node] <= CAPACITY
        )
        for service, node in enumerate(state.place)
    )


def available(state: State) -> tuple:
    """Return web/database/batch availability; web also requires database."""
    operating = physical(state)
    return operating[0] and operating[1], operating[1], operating[2]


def success(state: State) -> bool:
    """Require all services available and each healthy node within capacity."""
    cpu, mem = loads(state)
    return all(available(state)) and all(
        not state.health[node]
        or (cpu[node] <= CAPACITY and mem[node] <= CAPACITY)
        for node in range(3)
    )


@lru_cache(maxsize=None)
def transition(state: State, action: int) -> tuple:
    """Return candidate state, structural validity, prohibition, and cost.

    The candidate models execution before filtering. Validity means the command
    can execute structurally; prohibition separately checks destination capacity
    and loss of an already available critical service. Invalid commands are
    no-ops but still consume one step. The failed-node health flags never change.
    """
    operating = physical(state)
    # Target physical database failure first, then web, then batch. A web service
    # unavailable only because its database is down is not a physical failure.
    target = next((i for i in (1, 0, 2) if not operating[i]), None)
    placement = list(state.place)
    running = list(state.running)
    throttled = state.throttled
    valid = False
    cost = 0
    destination = None

    if action == 8:
        valid = True
    elif action == 1:
        valid = bool(running[2] and state.health[placement[2]] and not throttled)
        if valid:
            throttled = True
            cost = 1
    elif target is not None:
        source = placement[target]
        if action == 0:
            valid = bool(not running[target] and state.health[source])
            if valid:
                running[target] = True
                cost = 1
                destination = source
        elif 2 <= action <= 4:
            destination = action - 2
            valid = bool(
                running[target] and state.health[source]
                and state.health[destination] and destination != source
            )
            if valid:
                placement[target] = destination
                cost = 3
        elif 5 <= action <= 7:
            destination = action - 5
            valid = bool(
                (not running[target] or not state.health[source])
                and state.health[destination]
            )
            if valid:
                # Recovery data are assumed available outside a failed node.
                placement[target] = destination
                running[target] = True
                cost = 3

    # Build the proposed outcome before checking it. This lets both learned
    # controllers share the same execution model while differing in filtering.
    candidate = replace(
        state, place=tuple(placement), running=tuple(running),
        throttled=throttled, left=max(0, state.left - 1),
    )
    cpu, mem = loads(candidate)
    capacity_exceeded = (
        valid and destination is not None
        and (cpu[destination] > CAPACITY or mem[destination] > CAPACITY)
    )
    # Protect critical services that are available now. Existing fault outages
    # are measured separately; this check asks whether the command creates loss.
    before = available(state)
    after = available(candidate)
    critical_loss = valid and any(before[i] and not after[i] for i in (0, 1))
    return candidate, bool(valid), bool(capacity_exceeded or critical_loss), cost
