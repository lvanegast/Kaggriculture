"""Domain types, constants, and helper schemas for Kaggriculture."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class Direction(str, Enum):
    NORTH = "NORTH"
    SOUTH = "SOUTH"
    EAST = "EAST"
    WEST = "WEST"
    PASS = "PASS"


@dataclass(frozen=True)
class CropInfo:
    name: str
    seed_cost: int
    first_yield_day: int
    max_yield_day: int
    interval: int
    max_yield: int
    ongoing: bool
    base_price: float


CROPS: Dict[str, CropInfo] = {
    "WHEAT": CropInfo("WHEAT", seed_cost=10, first_yield_day=2, max_yield_day=4, interval=0, max_yield=6, ongoing=False, base_price=25.0),
    "CARROT": CropInfo("CARROT", seed_cost=20, first_yield_day=2, max_yield_day=3, interval=0, max_yield=4, ongoing=False, base_price=35.0),
    "TOMATO": CropInfo("TOMATO", seed_cost=50, first_yield_day=8, max_yield_day=8, interval=1, max_yield=4, ongoing=True, base_price=60.0),
    "STRAWBERRY": CropInfo("STRAWBERRY", seed_cost=100, first_yield_day=10, max_yield_day=10, interval=2, max_yield=4, ongoing=True, base_price=120.0),
    "MELON": CropInfo("MELON", seed_cost=80, first_yield_day=10, max_yield_day=12, interval=0, max_yield=6, ongoing=False, base_price=250.0),
}


@dataclass
class TileState:
    x: int
    y: int
    unlocked: bool = True
    kind: Optional[str] = None  # None, "PLANT", "WEED", "COOP", "PASTURE"
    crop: Optional[str] = None
    planted_day: int = 0
    watered_today: bool = False
    fertilized: bool = False
    has_weed: bool = False


@dataclass
class ParsedGameState:
    step: int
    day: int
    hour: int
    player_id: int
    my_money: int
    my_farmer_pos: Tuple[int, int]
    my_hand_positions: List[Tuple[int, int]]
    my_seeds: Dict[str, int]
    my_shed: Dict[str, int]
    unlocked_quadrants: List[int]
    board_size: int
    tiles: List[List[Optional[Dict[str, Any]]]]
    market_prices: Dict[str, float]
    raw_obs: Dict[str, Any]

    @property
    def is_endgame(self) -> bool:
        """Season ends at turn 720 (day 29, hour 23). After day 27, focus on liquidation."""
        return self.day >= 27

    def manhattan_distance(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> int:
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    def get_step_direction(self, current: Tuple[int, int], target: Tuple[int, int]) -> str:
        """Determines the immediate direction step toward the target."""
        cx, cy = current
        tx, ty = target
        if cx < tx:
            return Direction.EAST.value
        elif cx > tx:
            return Direction.WEST.value
        elif cy < ty:
            return Direction.SOUTH.value
        elif cy > ty:
            return Direction.NORTH.value
        return Direction.PASS.value


def parse_observation(obs: Dict[str, Any]) -> ParsedGameState:
    """Parses raw Kaggle observation dictionary into a typed ParsedGameState."""
    player = obs.get("player", 0)
    farms = obs.get("farms", [])
    private = obs.get("private", {}) or {}

    farm = farms[player] if farms and player < len(farms) else {}
    fx, fy = farm.get("farmer", (0, 0))
    hands = [tuple(h) for h in farm.get("hands", [])]
    money = farm.get("money", 0)
    unlocked_quadrants = farm.get("unlocked_quadrants", [0])
    tiles = farm.get("tiles", [])
    board_size = len(tiles) if tiles else 10

    seeds = private.get("seeds", {})
    shed = private.get("shed", {})

    market_raw = obs.get("market", {})
    market_prices = {}
    for item, m_data in market_raw.items():
        if isinstance(m_data, dict) and "price" in m_data:
            market_prices[item] = float(m_data["price"])
        elif isinstance(m_data, (int, float)):
            market_prices[item] = float(m_data)
        elif item in CROPS:
            market_prices[item] = CROPS[item].base_price

    return ParsedGameState(
        step=obs.get("step", 0),
        day=obs.get("day", 0),
        hour=obs.get("hour", 0),
        player_id=player,
        my_money=money,
        my_farmer_pos=(fx, fy),
        my_hand_positions=hands,
        my_seeds=seeds,
        my_shed=shed,
        unlocked_quadrants=unlocked_quadrants,
        board_size=board_size,
        tiles=tiles,
        market_prices=market_prices,
        raw_obs=obs,
    )
