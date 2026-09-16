"""Unit tests for domain types and simulation helpers."""

import pytest
from src.kaggriculture.sim.types import CROPS, Direction, parse_observation, ParsedGameState


def test_crops_catalog():
    assert "CARROT" in CROPS
    assert "TOMATO" in CROPS
    assert "WHEAT" in CROPS
    assert CROPS["CARROT"].seed_cost == 20
    assert CROPS["CARROT"].max_yield_day == 3


def test_direction_calculation():
    state = ParsedGameState(
        step=0, day=0, hour=0, player_id=0, my_money=3000,
        my_farmer_pos=(4, 4), my_hand_positions=[], my_seeds={},
        my_shed={}, unlocked_quadrants=[0], board_size=10,
        tiles=[], market_prices={}, raw_obs={},
    )
    assert state.get_step_direction((4, 4), (4, 3)) == Direction.NORTH.value
    assert state.get_step_direction((4, 4), (4, 5)) == Direction.SOUTH.value
    assert state.get_step_direction((4, 4), (3, 4)) == Direction.WEST.value
    assert state.get_step_direction((4, 4), (5, 4)) == Direction.EAST.value
    assert state.get_step_direction((4, 4), (4, 4)) == Direction.PASS.value


def test_parse_observation():
    mock_obs = {
        "step": 12,
        "day": 0,
        "hour": 12,
        "player": 0,
        "farms": [
            {
                "money": 3000,
                "farmer": [4, 4],
                "hands": [],
                "unlocked_quadrants": ["NW"],
                "tiles": [[None]*10 for _ in range(10)],
            },
            {
                "money": 3000,
                "farmer": [4, 4],
                "hands": [],
                "unlocked_quadrants": ["NW"],
                "tiles": [[None]*10 for _ in range(10)],
            }
        ],
        "private": {
            "seeds": {"CARROT": 2},
            "shed": {"CARROT": 5},
            "inventories": [{}]
        },
        "market": {"prices": {"CARROT": 35.0}}
    }
    parsed = parse_observation(mock_obs)
    assert parsed.step == 12
    assert parsed.my_money == 3000
    assert parsed.my_farmer_pos == (4, 4)
    assert parsed.my_seeds["CARROT"] == 2
    assert parsed.my_shed["CARROT"] == 5
    assert not parsed.is_endgame
