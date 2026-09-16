"""Greedy Priority Scheduler Agent (FarmBrain).

Optimized for:
1. High-yield compact cluster farming around the central shed access tile (4, 4).
2. Minimal travel overhead (Manhattan distance <= 2).
3. Zero-loss backpack liquidation: automatic DROP whenever standing on or returning to (4, 4).
4. Market discipline: automatic selling of shed produce and continuous seed restocking.
5. End-of-season liquidation: halts planting after day 26; harvests and liquidates 100% of crops before turn 720.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from src.kaggriculture.agents.base import BaseAgent
from src.kaggriculture.sim.types import CROPS, parse_observation, ParsedGameState


class FarmBrainAgent(BaseAgent):
    """Competitive heuristic agent with spatial cluster farming."""

    def __init__(self, name: str = "FarmBrainGreedy") -> None:
        super().__init__(name=name)
        # Optimal 4-tile cluster directly adjacent/attached to the shed access point (4, 4)
        self.cluster: List[Tuple[int, int]] = [(4, 4), (3, 4), (4, 3), (3, 3)]
        self.shed_access: Tuple[int, int] = (4, 4)

    def act(self, obs: Dict[str, Any], config: Any = None) -> Dict[str, Any]:
        try:
            farms = obs.get("farms", [])
            player = obs.get("player", 0)
            private = obs.get("private", {}) or {}
            if not farms or player >= len(farms):
                return {"farmer": ["PASS"], "hands": [], "market": []}

            farm = farms[player]
            fx, fy = farm.get("farmer", (4, 4))
            tiles = farm.get("tiles", [])
            day = obs.get("day", 0)
            seeds = private.get("seeds", {})
            shed = private.get("shed", {})
            inventories = private.get("inventories", [])
            inv = inventories[0] if inventories else {}

            market_orders: List[List[Any]] = []

            # 1. Market Phase: Liquidate Shed Produce
            for item, qty in shed.items():
                if qty > 0:
                    market_orders.append(["SELL", item, qty])

            # 2. Market Phase: Keep Carrot Seeds Stocked (Target: 4-5 seeds)
            carrot_seeds = seeds.get("CARROT", 0)
            if day <= 26 and carrot_seeds < 4 and farm.get("money", 0) >= CROPS["CARROT"].seed_cost:
                needed_seeds = min(4 - carrot_seeds, int(farm["money"] // CROPS["CARROT"].seed_cost))
                if needed_seeds > 0:
                    market_orders.append(["BUY_SEED", "CARROT", needed_seeds])

            # Cap market orders to allowed maximum
            market_orders = market_orders[:10]

            farmer_act = ["PASS"]
            carrying_items = any(qty > 0 for qty in inv.values())

            # 3. Shed Drop: If at shed access (4, 4) and carrying harvested goods, DROP to shed
            if (fx, fy) == self.shed_access and carrying_items:
                farmer_act = ["DROP"]
                return {"farmer": farmer_act, "hands": [], "market": market_orders}

            # 4. Immediate Action on Current Tile
            if fy < len(tiles) and fx < len(tiles[0]):
                current_tile = tiles[fy][fx]
                if isinstance(current_tile, dict):
                    kind = current_tile.get("kind")
                    if kind == "PLANT":
                        crop = current_tile.get("crop", "CARROT")
                        age = day - current_tile.get("planted_day", 0)
                        yield_units = current_tile.get("yield_units", 0)
                        max_yield_day = CROPS.get(crop, CROPS["CARROT"]).max_yield_day

                        if age >= max_yield_day and yield_units > 0:
                            farmer_act = ["HARVEST"]
                            return {"farmer": farmer_act, "hands": [], "market": market_orders}
                        elif not current_tile.get("watered_today", False) and day <= 28:
                            farmer_act = ["WATER"]
                            return {"farmer": farmer_act, "hands": [], "market": market_orders}
                    elif kind == "WEED":
                        farmer_act = ["DIG"]
                        return {"farmer": farmer_act, "hands": [], "market": market_orders}
                elif current_tile is None and carrot_seeds > 0 and day <= 26 and (fx, fy) in self.cluster:
                    farmer_act = ["PLANT", "CARROT"]
                    return {"farmer": farmer_act, "hands": [], "market": market_orders}

            # 5. Cluster Work Scheduling
            needed_tasks: List[Tuple[Tuple[int, int], int]] = []
            for cx, cy in self.cluster:
                if cy >= len(tiles) or cx >= len(tiles[0]):
                    continue
                t = tiles[cy][cx]
                if isinstance(t, dict):
                    kind = t.get("kind")
                    if kind == "PLANT":
                        crop = t.get("crop", "CARROT")
                        age = day - t.get("planted_day", 0)
                        yield_units = t.get("yield_units", 0)
                        max_yield_day = CROPS.get(crop, CROPS["CARROT"]).max_yield_day
                        if age >= max_yield_day and yield_units > 0:
                            needed_tasks.append(((cx, cy), 1))  # Priority 1: Harvest
                        elif not t.get("watered_today", False) and day <= 28:
                            needed_tasks.append(((cx, cy), 2))  # Priority 2: Water
                    elif kind == "WEED":
                        needed_tasks.append(((cx, cy), 3))  # Priority 3: Weed
                elif t is None and carrot_seeds > 0 and day <= 26:
                    needed_tasks.append(((cx, cy), 4))  # Priority 4: Plant

            # 6. Navigation
            if needed_tasks:
                needed_tasks.sort(
                    key=lambda item: (item[1], abs(fx - item[0][0]) + abs(fy - item[0][1]))
                )
                tx, ty = needed_tasks[0][0]
                farmer_act = [self._step_direction((fx, fy), (tx, ty))]
            elif carrying_items:
                # No tasks remain; return to shed access to offload
                tx, ty = self.shed_access
                farmer_act = [self._step_direction((fx, fy), (tx, ty))]

            return {"farmer": farmer_act, "hands": [], "market": market_orders}

        except Exception:
            # Fallback safe action
            return {"farmer": ["PASS"], "hands": [], "market": []}

    def _step_direction(self, current: Tuple[int, int], target: Tuple[int, int]) -> str:
        cx, cy = current
        tx, ty = target
        if cx < tx:
            return "EAST"
        elif cx > tx:
            return "WEST"
        elif cy < ty:
            return "SOUTH"
        elif cy > ty:
            return "NORTH"
        return "PASS"
