"""Unit tests for agent behavior and safety."""

import pytest
from src.kaggriculture.agents.greedy_scheduler import FarmBrainAgent
from src.kaggriculture.agents.baseline_naive import StarterBaselineAgent


def test_agent_initialization():
    agent = FarmBrainAgent()
    assert agent.name == "FarmBrainGreedy"
    baseline = StarterBaselineAgent()
    assert baseline.name == "StarterBaseline"


def test_agent_handles_empty_obs_safely():
    agent = FarmBrainAgent()
    action = agent.act({})
    assert "farmer" in action
    assert "market" in action
    assert action["farmer"] == ["PASS"]


def test_agent_generates_legal_actions():
    agent = FarmBrainAgent()
    obs = {
        "step": 0,
        "day": 0,
        "hour": 0,
        "player": 0,
        "farms": [
            {
                "money": 3000,
                "farmer": [4, 4],
                "hands": [],
                "tiles": [[None]*10 for _ in range(10)],
            }
        ],
        "private": {
            "seeds": {"CARROT": 0},
            "shed": {},
            "inventories": [{}]
        },
        "market": {}
    }
    action = agent.act(obs)
    assert isinstance(action, dict)
    assert isinstance(action["farmer"], list)
    assert isinstance(action["market"], list)
    # Day 0 with 0 seeds and 3000 money should trigger BUY_SEED
    assert any(order[0] == "BUY_SEED" for order in action["market"])
