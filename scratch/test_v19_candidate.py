import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v17_apex_colossus as s17

PRICE_FLOOR = 1
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

SHOP_PRODUCTS = {
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}

def _shape(name: str, value: float, scale: float | None = None) -> float:
    value = max(0.0, float(value))
    if name == "linear":
        return value
    if name == "sq":
        return value * value
    if name == "sqrt":
        return math.sqrt(value)
    if name == "log":
        return math.log1p(value)
    if name == "log10":
        return math.log10(1.0 + value)
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
    return max(PRICE_FLOOR, int(round(price)))

def is_sell(order) -> bool:
    return isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == "SELL" and order[1] in MARKET_PARAMS

def shop_demand_rate(obs):
    town = obs.get("town", {}) if isinstance(obs, dict) else getattr(obs, "town", {})
    unlocked = list(town.get("unlocked_shops", []) or [])
    demand = {p: 0.0 for p in MARKET_PARAMS}
    demand["MELON"] = 1.0 / 24.0
    for shop in unlocked:
        prods = SHOP_PRODUCTS.get(shop, ())
        mult = 2.0 if len(prods) == 1 else 1.0
        for p in prods:
            if p in demand:
                demand[p] += mult / 4.0
    return demand

def demand_adjusted_impact_score(obs, order, alpha=1.0) -> float:
    if not is_sell(order):
        return float("-inf")
    item = str(order[1])
    try:
        qty = max(0, int(order[2]))
    except (TypeError, ValueError):
        return 0.0
    market = obs.get("market", {}) if isinstance(obs, dict) else getattr(obs, "market", {})
    inventory = market.get("inventory", {}) if isinstance(market, dict) else {}
    prices = market.get("prices", {}) if isinstance(market, dict) else {}
    current_inventory = int(inventory.get(item, 10000) or 0)
    current_quote = float(prices.get(item, market_price(item, current_inventory)) or 0)
    later_quote = float(market_price(item, current_inventory + qty))
    base_score = float(qty) * max(0.0, current_quote - later_quote)
    if base_score <= 0.0:
        return base_score
    post_inventory = current_inventory + qty
    excess = max(0.0, float(post_inventory - 10000))
    rate = shop_demand_rate(obs).get(item, 0.0)
    recovery_days = excess / max(0.25, rate * 24.0)
    urgency = min(1.0, recovery_days / 10.0)
    return base_score * (1.0 + float(alpha) * urgency)

def reorder_market_demand_aware(obs, action, alpha=1.0):
    market = list(action.get("market", []))
    sell_rows = [
        (demand_adjusted_impact_score(obs, order, alpha), -index, order)
        for index, order in enumerate(market)
        if is_sell(order)
    ]
    if len(sell_rows) < 2:
        return action
    sell_rows.sort(reverse=True)
    ranked = [row[2] for row in sell_rows]
    others = [order for order in market if not is_sell(order)]
    action["market"] = ranked + others
    return action

def monetizable_terminal_units(obs, action, step):
    action = s17._align_hands(action, obs)
    if step not in (717, 718):
        return action
    player = s17._seat_guard(obs)
    farm = s17._farm_guard(obs, player)
    private = obs.get("private", {}) or {}
    tiles = farm.get("tiles", []) or []
    if not tiles:
        return action
    half = len(tiles) // 2
    access = {(half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half)}
    positions = [farm.get("farmer", [0, 0]), *(farm.get("hands", []) or [])]
    inventories = list(private.get("inventories", []) or [])
    inventories.extend({} for _ in range(max(0, len(positions) - len(inventories))))
    unit_actions = [action.get("farmer", ["PASS"]), *(action.get("hands") or [])]

    for index, (raw_position, inventory) in enumerate(zip(positions, inventories)):
        if not isinstance(raw_position, (list, tuple)) or len(raw_position) < 2:
            continue
        position = (int(raw_position[0]), int(raw_position[1]))
        load = sum(max(0, int(value or 0)) for value in (inventory or {}).values())
        x, y = position
        tile = tiles[y][x] if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]) else None
        distance = min(abs(x - sx) + abs(y - sy) for sx, sy in access)
        replacement = None
        if load > 0 and position in access:
            replacement = ["DROP"]
        elif step == 717 and load > 0 and distance == 1:
            for op, dx, dy in (("NORTH", 0, -1), ("SOUTH", 0, 1), ("WEST", -1, 0), ("EAST", 1, 0)):
                if (x + dx, y + dy) in access and 0 <= y + dy < len(tiles) and 0 <= x + dx < len(tiles) and tiles[y + dy][x + dx] != "LOCKED":
                    replacement = [op]
                    break
        elif (
            step == 717
            and load == 0
            and position in access
            and isinstance(tile, dict)
            and int(tile.get("yield_units", 0) or 0) > 0
        ):
            replacement = ["HARVEST"]
        if replacement is not None:
            unit_actions[index] = replacement

    action["farmer"] = unit_actions[0]
    action["hands"] = unit_actions[1:]
    return action

def agent_v19_candidate(obs, config=None):
    step = int(s17._v43_get(obs, "step", 0) or 0)
    act = s17._V43_POLICY(obs, config)
    act = s17._capital_guard(obs, act, step)
    act = monetizable_terminal_units(obs, act, step)
    act = s17._terminal_zero_waste_sweep(obs, act, step)
    act = reorder_market_demand_aware(obs, act, alpha=1.0)
    return s17._align_hands(act, obs)

if __name__ == "__main__":
    from scratch.test_v18_candidate import agent_v18_candidate
    seeds = [42, 100, 2024, 7, 999, 1234, 555, 888, 314, 2718]
    scores = []
    print("Evaluating agent_v19_candidate in self-play across 10 seeds...", flush=True)
    for s in seeds:
        env = ke.make("kaggriculture", configuration={"seed": s})
        env.run([agent_v19_candidate, agent_v19_candidate])
        s0 = env.steps[-1][0]["reward"]
        s1 = env.steps[-1][1]["reward"]
        scores.append((s0 + s1) / 2)
        print(f"Seed {s:5d}: P0=${s0:8.0f} | P1=${s1:8.0f} | Avg=${(s0+s1)/2:8.0f}", flush=True)

    print(f"\nOverall Self-Play Average: ${sum(scores)/len(scores):8.1f}", flush=True)

    print("\nRunning Head-to-Head: v19 vs v18...", flush=True)
    diffs = []
    for s in seeds:
        env = ke.make("kaggriculture", configuration={"seed": s})
        env.run([agent_v19_candidate, agent_v18_candidate])
        s0 = env.steps[-1][0]["reward"]
        s1 = env.steps[-1][1]["reward"]
        diffs.append(s0 - s1)
        print(f"Seed {s:5d}: P0(v19)=${s0:8.0f} vs P1(v18)=${s1:8.0f} | Diff={s0-s1:+6.0f}", flush=True)

    print(f"\nAverage Margin v19 over v18: ${sum(diffs)/len(diffs):+8.1f}", flush=True)
