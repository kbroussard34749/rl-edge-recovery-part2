"""Frozen scenario construction and development-only feasibility checks.

manifest() first builds a healthy configuration, injects one fault, and assigns
the fixed split. Each fault type has three training starts, one validation start,
and two held-out starts. feasible() checks that the model permits recovery.
Search solutions are never supplied to the learner as labels or actions.
"""

from collections import deque
from dataclasses import asdict, replace

from .environment import State, success
from .safety_filter import step


def state_from(data: dict) -> State:
    """Restore immutable tuple fields from a JSON-compatible state mapping."""
    return State(**{
        key: tuple(value) if isinstance(value, list) else value
        for key, value in data.items()
    })


def manifest() -> list:
    """Construct the original 24 starts without sampling or changing splits."""
    scenarios = []
    for fault in ("crash", "cpu", "memory", "node"):
        for variant in range(6):
            host = variant % 3
            cpu = [0] * 3
            mem = [0] * 3
            # The higher-numbered starts introduce background demand on other
            # nodes, making their exact states distinct from training starts.
            cpu[(host + 1) % 3] = variant // 3
            mem[(host + 2) % 3] = variant // 3
            before = State(
                (True,) * 3, tuple(cpu), tuple(mem), (host,) * 3, (True,) * 3,
            )
            after = before
            if fault == "crash":
                running = [True] * 3
                running[variant % 3] = False
                after = replace(before, running=tuple(running))
            elif fault == "cpu":
                cpu[host] = 2 + variant % 3
                after = replace(before, cpu=tuple(cpu))
            elif fault == "memory":
                mem[host] = 2 + variant % 3
                after = replace(before, mem=tuple(mem))
            else:
                health = [True] * 3
                health[host] = False
                after = replace(before, health=tuple(health))

            split = (
                "train" if variant < 3 else "validation" if variant == 3 else "test"
            )
            scenarios.append(dict(
                id=f"{fault}_{variant}", fault=fault, split=split,
                before=asdict(before), initial=asdict(after),
            ))
    return scenarios


def feasible(initial: State) -> dict:
    """Breadth-first search for a permitted recovery within 20 commands.

    This development check normalizes remaining budget only in its visited key,
    so physically identical no-op paths do not inflate the search. Queue states
    retain their actual budget. A shortest visit leaves the most recovery time.
    This normalized key is not the learner's exact state representation.
    """
    queue = deque([(initial, 0)])
    seen = {replace(initial, left=20)}
    edges = 0
    shortest = None
    while queue:
        state, depth = queue.popleft()
        if success(state):
            if shortest is None:
                shortest = depth
            continue
        if depth >= 20:
            continue
        for action in range(9):
            next_state, _, _, info = step(state, action, True)
            edges += 1
            if info["violations"]:
                raise AssertionError("Filtered action violation")
            key = replace(next_state, left=20)
            if key not in seen:
                seen.add(key)
                queue.append((next_state, depth + 1))
    return dict(
        feasible=shortest is not None, shortest_steps=shortest,
        reachable_physical_states=len(seen), checked_edges=edges,
    )
