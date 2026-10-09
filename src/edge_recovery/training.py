"""Train a sparse Q-table through repeated simulated recovery episodes.

The workflow samples a training start, explores or exploits a command, executes
it through the fixed simulator, and updates its value from the actual outcome.
Only training starts supply experience. Validation and testing occur separately.
Episode summaries, curves, and portable JSON policies preserve the run evidence.
"""

import csv
from dataclasses import asdict
from pathlib import Path
import json
import random
import time

from .controllers import greedy, update
from .runtime import peak_rss_bytes
from .safety_filter import step
from .scenarios import state_from


def train(scenarios: list, alpha: float, seed: int, filtered: bool,
          episodes: int, folder: Path) -> tuple:
    """Return the trained table and metadata; write only to the chosen folder.

    The full planned budget is 20,000 episodes. A smaller budget is a development
    run, with exploration decay scaled to that budget; it is not the final study.
    The caller chooses a separate location to protect retained experiment files.
    """
    rng = random.Random(seed)
    q = {}
    start = time.perf_counter()
    curves = []
    rows = []
    initial = [state_from(x["initial"]) for x in scenarios if x["split"] == "train"]

    for episode in range(episodes):
        state = rng.choice(initial)
        total = 0
        violations = 0
        # At the planned budget this reaches .1 after 16,000 episodes. Keep the
        # expression and random draw order unchanged for reproducible behavior.
        epsilon = 1 - .9 * min(episode / (.8 * episodes), 1)
        for decision in range(20):
            values = q.setdefault(state, [0.] * 9)
            action = rng.randrange(9) if rng.random() < epsilon else greedy(values)
            next_state, reward, done, info = step(state, action, filtered)
            update(q, state, action, reward, next_state, done, alpha)
            total += reward
            violations += info["violations"]
            state = next_state
            if done:
                break
        rows.append((episode + 1, total, info["success"], decision + 1, violations))
        if (episode + 1) % 200 == 0 or episode + 1 == episodes:
            # These summarize exploratory training, not greedy policy testing.
            recent = rows[-200:]
            curves.append(dict(
                episode=episode + 1,
                return_mean=sum(x[1] for x in recent) / len(recent),
                success_mean=sum(x[2] for x in recent) / len(recent),
                epsilon=epsilon,
            ))

    folder.mkdir(parents=True, exist_ok=True)
    with (folder / "episodes.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["episode", "return", "success", "steps", "executed_violations"])
        writer.writerows(rows)
    (folder / "curve.json").write_text(json.dumps(curves, indent=2))
    # Preserve state insertion order and the original JSON policy format. This
    # makes artifact comparisons possible without relying on pickle objects.
    (folder / "policy.json").write_text(json.dumps([
        dict(state=asdict(state), values=values) for state, values in q.items()
    ]))
    metadata = dict(
        seed=seed, alpha=alpha, filtered=filtered, episodes=episodes,
        seconds=time.perf_counter() - start, q_states=len(q),
        nonzero_pairs=sum(value != 0 for values in q.values() for value in values),
        process_peak_rss_bytes=peak_rss_bytes(),
    )
    (folder / "training.json").write_text(json.dumps(metadata, indent=2))
    return q, metadata
