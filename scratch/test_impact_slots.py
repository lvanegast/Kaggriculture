import sys
from pathlib import Path
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))

import kaggle_environments as ke
import submission_v16_apex_titan as v16
from scratch.test_v26_concept import v26_agent

MARKET_PARAMS = {
    "WHEAT": (25, 10000, 400, "sqrt", 0.8, "log", 0.2),
    "CARROT": (35, 10000, 450, "hinge", 1.0, "sqrt", 0.7),
    "TOMATO": (60, 10000, 200, "hinge", 0.4, "sqrt", 0.6),
    "STRAWBERRY": (120, 10000, 100, "sqrt", 0.7, "linear", 1.6),
    "MELON": (250, 10000, 300, "log", 0.2, "sq", 3.6),
    "EGG": (50, 10000, 332, "hinge", 0.4, "log", 0.2),
    "MILK": (160, 10000, 122, "sqrt", 0.6, "linear", 1.6),
    "WOOL": (200, 10000, 105, "log", 0.2, "sq", 3.2),
    "FERTILIZER": (100, 10000, 200, "linear", 0.4, "linear", 0.4),
}

def _shape(name: str, value: float, scale: float | None = None) -> float:
    value = max(0.0, float(value))
    if name == "linear":
        return value
    if name == "sq":
        return value * value
    if name == "sqrt":
        import math; return math.sqrt(value)
    if name == "log":
        import math; return math.log1p(value)
    if name == "hinge":
        if scale is None or scale <= 0:
            return value
        normalized = value / scale
        return normalized + 8.0 * max(0.0, normalized - 1.0) ** 2
    return value

def market_price(item: str, inventory: int) -> int:
    base, equilibrium, scale, below_func, below_target, above_func, above_target = MARKET_PARAMS[item]
    if inventory < equilibrium:
        amplitude = below_target * base / _shape(below_func, scale, scale)
        price = base + amplitude * _shape(below_func, equilibrium - inventory, scale)
    else:
        amplitude = above_target * base / _shape(above_func, scale, scale)
        price = base - amplitude * _shape(above_func, inventory - equilibrium, scale)
    return max(1, int(round(price)))

def is_sell(order) -> bool:
    return isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == "SELL" and order[1] in MARKET_PARAMS

def impact_score(obs, order) -> float:
    if not is_sell(order):
        return float("-inf")
    item = str(order[1])
    try:
        quantity = max(0, int(order[2]))
    except (TypeError, ValueError):
        return 0.0
    market = obs.get("market", {}) or {}
    inventory = market.get("inventory", {}) or {}
    prices = market.get("prices", {}) or {}
    current_inventory = int(inventory.get(item, 10000) or 0)
    current_quote = float(prices.get(item, market_price(item, current_inventory)) or 0)
    later_quote = float(market_price(item, current_inventory + quantity))
    return float(quantity) * max(0.0, current_quote - later_quote)

def reorder_market_slots_only(obs, action):
    market = list(action.get("market", []))
    sell_rows = [
        (impact_score(obs, order), -index, order)
        for index, order in enumerate(market)
        if is_sell(order)
    ]
    if len(sell_rows) < 2:
        return action
    sell_rows.sort(reverse=True)
    ranked = [row[2] for row in sell_rows]
    iterator = iter(ranked)
    action["market"] = [next(iterator) if is_sell(order) else order for order in market]
    return action

def v27_impact_slots_agent(obs, configuration=None):
    try:
        step = int(v16._v43_get(obs, "step", 0) or 0)
        action = v16._V43_POLICY(obs, configuration)
        action = v16._weed_repair_action(obs, action, step)
        action = v16._capital_guard(obs, action, step)
        
        # Post-day 24 fertilizer liquidator (append only)
        if step >= 596:
            private = obs.get("private", {}) if isinstance(obs, dict) else getattr(obs, "private", {})
            shed = dict(private.get("shed", {}) if isinstance(private, dict) else {})
            fert_count = int(shed.get("FERTILIZER", 0) or 0)
            if fert_count > 0:
                market = list(action.get("market", []))
                for o in market:
                    if len(o) >= 3 and o[0] == "SELL" and o[1] == "FERTILIZER":
                        fert_count -= int(o[2])
                if fert_count > 0 and len(market) < 10:
                    market.append(["SELL", "FERTILIZER", min(fert_count, 3)])
                    action["market"] = market

        # Smart Terminal Sweep: cleans ghost sells of 0-inventory items, fills with real shed items
        if step >= 718:
            private = obs.get("private", {}) if isinstance(obs, dict) else getattr(obs, "private", {})
            shed = dict(private.get("shed", {}) if isinstance(private, dict) else {})
            market = list(action.get("market", []))
            
            valid_market = []
            for o in market:
                if len(o) >= 3 and o[0] == "SELL":
                    item = o[1]
                    if shed.get(item, 0) > 0:
                        valid_market.append(o)
                        shed[item] = max(0, shed[item] - int(o[2]))
                else:
                    valid_market.append(o)
                    
            for p in v16._PRODUCTS_ORDER:
                rem = shed.get(p, 0)
                if rem > 0 and len(valid_market) < 10:
                    valid_market.append(["SELL", p, rem])
            action["market"] = valid_market
        else:
            action = reorder_market_slots_only(obs, action)

        return v16._align_hands(action, obs)
    except Exception:
        farm = v16._farm_guard(obs, v16._seat_guard(obs))
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (v16._v43_get(farm, "hands", []) or [])],
            "market": [],
        }

from src.kaggriculture.sim.kaggle_wrapper import run_episode

seeds = [42, 100, 2024, 7, 999]
for s in seeds:
    res = run_episode(v27_impact_slots_agent, 'submission_v16_apex_titan.py', seed=s)
    diff = res['reward_player0'] - res['reward_player1']
    print(f"Seed {s}: v27_slots={res['reward_player0']:.1f} vs v16={res['reward_player1']:.1f} (Diff: {diff:+.1f})")
