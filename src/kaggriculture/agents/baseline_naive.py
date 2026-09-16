"""Baseline reference agents for benchmarking."""

from __future__ import annotations
from typing import Any, Dict
from src.kaggriculture.agents.base import BaseAgent
from src.kaggriculture.sim.types import CROPS


class StarterBaselineAgent(BaseAgent):
    """Replication of the official Starter Carrot-loop baseline agent."""

    def __init__(self) -> None:
        super().__init__(name="StarterBaseline")

    def act(self, obs: Dict[str, Any], config: Any = None) -> Dict[str, Any]:
        farms = obs.get("farms", [])
        player = obs.get("player", 0)
        private = obs.get("private", {}) or {}
        if not farms or player >= len(farms):
            return {"farmer": ["PASS"], "hands": [], "market": []}

        farm = farms[player]
        fx, fy = farm.get("farmer", (0, 0))
        tiles = farm.get("tiles", [])
        tile = tiles[fy][fx] if tiles and fy < len(tiles) and fx < len(tiles[0]) else None
        day = obs.get("day", 0)
        seeds = private.get("seeds", {})
        shed = private.get("shed", {})

        market = []
        if shed.get("CARROT", 0) > 0:
            market.append(["SELL", "CARROT", shed["CARROT"]])
        if seeds.get("CARROT", 0) == 0 and farm.get("money", 0) >= CROPS["CARROT"].seed_cost:
            market.append(["BUY_SEED", "CARROT", 1])

        farmer = ["PASS"]
        if tile is None and seeds.get("CARROT", 0) > 0:
            farmer = ["PLANT", "CARROT"]
        elif isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == "CARROT":
            age = day - tile.get("planted_day", 0)
            if age >= CROPS["CARROT"].max_yield_day:
                farmer = ["HARVEST"]
            elif not tile.get("watered_today", False):
                farmer = ["WATER"]

        return {"farmer": farmer, "hands": [], "market": market}
