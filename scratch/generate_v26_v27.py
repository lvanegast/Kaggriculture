import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))

with open("submission_v16_apex_titan.py", "r", encoding="utf-8") as f:
    v16_text = f.read()

# Split v16 before _terminal_zero_waste_sweep
split_marker = "def _terminal_zero_waste_sweep(obs, action, step):"
idx = v16_text.find(split_marker)
assert idx != -1, "Marker not found!"

v16_base = v16_text[:idx]

v26_tail = '''
def _post_day24_fertilizer_liquidator(obs, action, step):
    if step < 596:
        return action
    private = obs.get("private", {}) if isinstance(obs, dict) else getattr(obs, "private", {})
    shed = dict(private.get("shed", {}) if isinstance(private, dict) else {})
    fert_count = int(shed.get("FERTILIZER", 0) or 0)
    if fert_count <= 0:
        return action
    market = list(action.get("market", []))
    for o in market:
        if len(o) >= 3 and o[0] == "SELL" and o[1] == "FERTILIZER":
            fert_count -= int(o[2])
    if fert_count > 0 and len(market) < 10:
        market.append(["SELL", "FERTILIZER", min(fert_count, 3)])
        action["market"] = market
    return action

def _smart_terminal_zero_waste_sweep(obs, action, step):
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
                
        for p in _PRODUCTS_ORDER:
            rem = shed.get(p, 0)
            if rem > 0 and len(valid_market) < 10:
                valid_market.append(["SELL", p, rem])
        action["market"] = valid_market
    return action

def agent(obs, configuration=None):
    try:
        step = int(_v43_get(obs, "step", 0) or 0)
        action = _V43_POLICY(obs, configuration)
        action = _weed_repair_action(obs, action, step)
        action = _capital_guard(obs, action, step)
        action = _post_day24_fertilizer_liquidator(obs, action, step)
        action = _smart_terminal_zero_waste_sweep(obs, action, step)
        return _align_hands(action, obs)
    except Exception:
        farm = _farm_guard(obs, _seat_guard(obs))
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_v43_get(farm, "hands", []) or [])],
            "market": [],
        }

def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)
'''

with open("submission_v26_titan_liquidator.py", "w", encoding="utf-8") as f:
    f.write(v16_base + v26_tail)

print("Generated submission_v26_titan_liquidator.py successfully!")

v27_tail = '''
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

def _market_price(item: str, inventory: int) -> int:
    base, equilibrium, scale, below_func, below_target, above_func, above_target = MARKET_PARAMS[item]
    if inventory < equilibrium:
        amplitude = below_target * base / _shape(below_func, scale, scale)
        price = base + amplitude * _shape(below_func, equilibrium - inventory, scale)
    else:
        amplitude = above_target * base / _shape(above_func, scale, scale)
        price = base - amplitude * _shape(above_func, inventory - equilibrium, scale)
    return max(1, int(round(price)))

def _is_sell(order) -> bool:
    return isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == "SELL" and order[1] in MARKET_PARAMS

def _impact_score(obs, order) -> float:
    if not _is_sell(order):
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
    current_quote = float(prices.get(item, _market_price(item, current_inventory)) or 0)
    later_quote = float(_market_price(item, current_inventory + quantity))
    return float(quantity) * max(0.0, current_quote - later_quote)

def _reorder_market_slots_only(obs, action):
    market = list(action.get("market", []))
    sell_rows = [
        (_impact_score(obs, order), -index, order)
        for index, order in enumerate(market)
        if _is_sell(order)
    ]
    if len(sell_rows) < 2:
        return action
    sell_rows.sort(reverse=True)
    ranked = [row[2] for row in sell_rows]
    iterator = iter(ranked)
    action["market"] = [next(iterator) if _is_sell(order) else order for order in market]
    return action

def _post_day24_fertilizer_liquidator(obs, action, step):
    if step < 596:
        return action
    private = obs.get("private", {}) if isinstance(obs, dict) else getattr(obs, "private", {})
    shed = dict(private.get("shed", {}) if isinstance(private, dict) else {})
    fert_count = int(shed.get("FERTILIZER", 0) or 0)
    if fert_count <= 0:
        return action
    market = list(action.get("market", []))
    for o in market:
        if len(o) >= 3 and o[0] == "SELL" and o[1] == "FERTILIZER":
            fert_count -= int(o[2])
    if fert_count > 0 and len(market) < 10:
        market.append(["SELL", "FERTILIZER", min(fert_count, 3)])
        action["market"] = market
    return action

def _smart_terminal_zero_waste_sweep(obs, action, step):
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
                
        for p in _PRODUCTS_ORDER:
            rem = shed.get(p, 0)
            if rem > 0 and len(valid_market) < 10:
                valid_market.append(["SELL", p, rem])
        action["market"] = valid_market
    return action

def agent(obs, configuration=None):
    try:
        step = int(_v43_get(obs, "step", 0) or 0)
        action = _V43_POLICY(obs, configuration)
        action = _weed_repair_action(obs, action, step)
        action = _capital_guard(obs, action, step)
        action = _post_day24_fertilizer_liquidator(obs, action, step)
        if step >= 718:
            action = _smart_terminal_zero_waste_sweep(obs, action, step)
        else:
            action = _reorder_market_slots_only(obs, action)
        return _align_hands(action, obs)
    except Exception:
        farm = _farm_guard(obs, _seat_guard(obs))
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_v43_get(farm, "hands", []) or [])],
            "market": [],
        }

def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)
'''

with open("submission_v27_titan_sovereign.py", "w", encoding="utf-8") as f:
    f.write(v16_base + v27_tail)

print("Generated submission_v27_titan_sovereign.py successfully!")
