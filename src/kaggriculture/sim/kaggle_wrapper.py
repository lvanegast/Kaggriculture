"""Wrapper and utilities for executing Kaggriculture episodes via kaggle-environments."""

from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import kaggle_environments as ke


def run_episode(
    agent1: Union[str, Callable[[Dict[str, Any]], Dict[str, Any]]],
    agent2: Union[str, Callable[[Dict[str, Any]], Dict[str, Any]]],
    seed: Optional[int] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Runs a complete 720-step episode between two agents.

    Returns dictionary with scores, winner, and steps summary.
    """
    config = {}
    if seed is not None:
        config["seed"] = seed

    env = ke.make("kaggriculture", configuration=config, debug=debug)
    env.run([agent1, agent2])

    player0_reward = env.steps[-1][0].get("reward", 0) or 0
    player1_reward = env.steps[-1][1].get("reward", 0) or 0

    status0 = env.steps[-1][0].get("status", "DONE")
    status1 = env.steps[-1][1].get("status", "DONE")

    winner = None
    if player0_reward > player1_reward:
        winner = 0
    elif player1_reward > player0_reward:
        winner = 1

    return {
        "reward_player0": player0_reward,
        "reward_player1": player1_reward,
        "status_player0": status0,
        "status_player1": status1,
        "winner": winner,
        "total_steps": len(env.steps),
        "replay": env.toJSON(),
    }
