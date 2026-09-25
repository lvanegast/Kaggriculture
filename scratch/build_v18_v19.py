import sys
from pathlib import Path

v17_path = Path("submission_v17_apex_colossus.py")
v17_content = v17_path.read_text(encoding="utf-8")

# Extract the base engine (up to line 740 where _V43_POLICY is defined)
split_marker = "_V43_POLICY = _v43_build(_V43_ROUTES, _V43_CONFIG)\n"
idx = v17_content.find(split_marker)
if idx == -1:
    raise ValueError("Split marker not found in v17!")
base_engine = v17_content[:idx + len(split_marker)]

# ==================== V18 CODE ====================
v18_tail = '''
import math

# --- V18 APEX DOMINATOR: Core Constants & Guards ---
_PRODUCTS_ORDER = ('WOOL', 'MELON', 'MILK', 'STRAWBERRY', 'FERTILIZER', 'CARROT', 'TOMATO', 'EGG', 'WHEAT')

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

def _seat_guard(obs):
    return 1 if int(_v43_get(obs, "player", 0) or 0) == 1 else 0

def _farm_guard(obs, seat):
    farms = list(_v43_get(obs, "farms", []) or [])
    return farms[seat] if seat < len(farms) else {}

def _align_hands(action, obs):
    farm = _farm_guard(obs, _seat_guard(obs))
    expected_hands = len(list(_v43_get(farm, "hands", []) or []))
    hands = list(action.get("hands", []))
    if len(hands) < expected_hands:
        hands.extend([["PASS"] for _ in range(expected_hands - len(hands))])
    elif len(hands) > expected_hands:
        hands = hands[:expected_hands]
    action["hands"] = hands
    return action

# --- V18 Capital Guard ---
def _capital_guard(obs, action, step):
    seat = _seat_guard(obs)
    farm = _farm_guard(obs, seat)
    money = float(_v43_get(farm, 'money', 0) or 0)
    # Guarantee Step 97 Cow purchase under price deflation
    if 94 <= step <= 96 and money < 405.0:
        private = obs.get('private', {}) if isinstance(obs, dict) else getattr(obs, 'private', {})
        shed = private.get('shed', {}) if isinstance(private, dict) else {}
        wheat_count = int(shed.get('WHEAT', 0) or 0)
        needed_cash = 405.0 - money
        units_to_sell = min(wheat_count, int(needed_cash // 20) + 1)
        safe_units = max(0, min(units_to_sell, wheat_count - 2))
        if safe_units > 0:
            market = list(action.get('market', []))
            market.append(['SELL', 'WHEAT', safe_units])
            action['market'] = market
    return action

# --- V18 Pre-Terminal Unit Salvage ---
def _monetizable_terminal_units(obs, action, step):
    action = _align_hands(action, obs)
    if step not in (717, 718):
        return action
    player = _seat_guard(obs)
    farm = _farm_guard(obs, player)
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

# --- V18 Terminal Zero-Waste Sweep ---
def _terminal_zero_waste_sweep(obs, action, step):
    if step >= 718:
        private = obs.get('private', {}) if isinstance(obs, dict) else getattr(obs, 'private', {})
        shed = dict(private.get('shed', {}) if isinstance(private, dict) else {})
        market = list(action.get('market', []))
        
        for o in market:
            if len(o) >= 3 and o[0] == 'SELL' and o[1] in shed:
                shed[o[1]] = max(0, shed[o[1]] - int(o[2]))
                
        for p in _PRODUCTS_ORDER:
            rem = shed.get(p, 0)
            if rem > 0 and len(market) < 10:
                market.append(['SELL', p, rem])
                
        action['market'] = market
    return action

# --- V18 Impact-Front Sequential Queue Priority ---
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

def _market_price(item: str, inventory: int) -> int:
    base, equilibrium, scale, below_func, below_target, above_func, above_target = MARKET_PARAMS[item]
    if inventory < equilibrium:
        amplitude = below_target * base / _shape(below_func, scale, scale)
        price = base + amplitude * _shape(below_func, equilibrium - inventory, scale)
    else:
        amplitude = above_target * base / _shape(above_func, scale, scale)
        price = base - amplitude * _shape(above_func, inventory - equilibrium, scale)
    return max(PRICE_FLOOR, int(round(price)))

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
    market = obs.get("market", {}) if isinstance(obs, dict) else getattr(obs, "market", {})
    inventory = market.get("inventory", {}) if isinstance(market, dict) else {}
    prices = market.get("prices", {}) if isinstance(market, dict) else {}
    current_inventory = int(inventory.get(item, 10000) or 0)
    current_quote = float(prices.get(item, _market_price(item, current_inventory)) or 0)
    later_quote = float(_market_price(item, current_inventory + quantity))
    return float(quantity) * max(0.0, current_quote - later_quote)

def _reorder_market_impact_front(obs, action):
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
    others = [order for order in market if not _is_sell(order)]
    action["market"] = ranked + others
    return action

def agent(obs, configuration=None):
    try:
        step = int(_v43_get(obs, "step", 0) or 0)
        action = _V43_POLICY(obs, configuration)
        action = _capital_guard(obs, action, step)
        action = _monetizable_terminal_units(obs, action, step)
        action = _terminal_zero_waste_sweep(obs, action, step)
        action = _reorder_market_impact_front(obs, action)
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

# ==================== V19 CODE ====================
v19_tail = '''
import math

# --- V19 APEX SOVEREIGN: Core Constants & Guards ---
_PRODUCTS_ORDER = ('WOOL', 'MELON', 'MILK', 'STRAWBERRY', 'FERTILIZER', 'CARROT', 'TOMATO', 'EGG', 'WHEAT')

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

def _seat_guard(obs):
    return 1 if int(_v43_get(obs, "player", 0) or 0) == 1 else 0

def _farm_guard(obs, seat):
    farms = list(_v43_get(obs, "farms", []) or [])
    return farms[seat] if seat < len(farms) else {}

def _align_hands(action, obs):
    farm = _farm_guard(obs, _seat_guard(obs))
    expected_hands = len(list(_v43_get(farm, "hands", []) or []))
    hands = list(action.get("hands", []))
    if len(hands) < expected_hands:
        hands.extend([["PASS"] for _ in range(expected_hands - len(hands))])
    elif len(hands) > expected_hands:
        hands = hands[:expected_hands]
    action["hands"] = hands
    return action

# --- V19 Capital Guard ---
def _capital_guard(obs, action, step):
    seat = _seat_guard(obs)
    farm = _farm_guard(obs, seat)
    money = float(_v43_get(farm, 'money', 0) or 0)
    # Guarantee Step 97 Cow purchase under price deflation
    if 94 <= step <= 96 and money < 405.0:
        private = obs.get('private', {}) if isinstance(obs, dict) else getattr(obs, 'private', {})
        shed = private.get('shed', {}) if isinstance(private, dict) else {}
        wheat_count = int(shed.get('WHEAT', 0) or 0)
        needed_cash = 405.0 - money
        units_to_sell = min(wheat_count, int(needed_cash // 20) + 1)
        safe_units = max(0, min(units_to_sell, wheat_count - 2))
        if safe_units > 0:
            market = list(action.get('market', []))
            market.append(['SELL', 'WHEAT', safe_units])
            action['market'] = market
    return action

# --- V19 Pre-Terminal Unit Salvage ---
def _monetizable_terminal_units(obs, action, step):
    action = _align_hands(action, obs)
    if step not in (717, 718):
        return action
    player = _seat_guard(obs)
    farm = _farm_guard(obs, player)
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

# --- V19 Terminal Zero-Waste Sweep ---
def _terminal_zero_waste_sweep(obs, action, step):
    if step >= 718:
        private = obs.get('private', {}) if isinstance(obs, dict) else getattr(obs, 'private', {})
        shed = dict(private.get('shed', {}) if isinstance(private, dict) else {})
        market = list(action.get('market', []))
        
        for o in market:
            if len(o) >= 3 and o[0] == 'SELL' and o[1] in shed:
                shed[o[1]] = max(0, shed[o[1]] - int(o[2]))
                
        for p in _PRODUCTS_ORDER:
            rem = shed.get(p, 0)
            if rem > 0 and len(market) < 10:
                market.append(['SELL', p, rem])
                
        action['market'] = market
    return action

# --- V19 Demand-Adjusted Urgency Market Priority ---
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

def _market_price(item: str, inventory: int) -> int:
    base, equilibrium, scale, below_func, below_target, above_func, above_target = MARKET_PARAMS[item]
    if inventory < equilibrium:
        amplitude = below_target * base / _shape(below_func, scale, scale)
        price = base + amplitude * _shape(below_func, equilibrium - inventory, scale)
    else:
        amplitude = above_target * base / _shape(above_func, scale, scale)
        price = base - amplitude * _shape(above_func, inventory - equilibrium, scale)
    return max(PRICE_FLOOR, int(round(price)))

def _is_sell(order) -> bool:
    return isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == "SELL" and order[1] in MARKET_PARAMS

def _shop_demand_rate(obs):
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

def _demand_adjusted_impact_score(obs, order, alpha=1.0) -> float:
    if not _is_sell(order):
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
    current_quote = float(prices.get(item, _market_price(item, current_inventory)) or 0)
    later_quote = float(_market_price(item, current_inventory + qty))
    base_score = float(qty) * max(0.0, current_quote - later_quote)
    if base_score <= 0.0:
        return base_score
    post_inventory = current_inventory + qty
    excess = max(0.0, float(post_inventory - 10000))
    rate = _shop_demand_rate(obs).get(item, 0.0)
    recovery_days = excess / max(0.25, rate * 24.0)
    urgency = min(1.0, recovery_days / 10.0)
    return base_score * (1.0 + float(alpha) * urgency)

def _reorder_market_demand_aware(obs, action, alpha=1.0):
    market = list(action.get("market", []))
    sell_rows = [
        (_demand_adjusted_impact_score(obs, order, alpha), -index, order)
        for index, order in enumerate(market)
        if _is_sell(order)
    ]
    if len(sell_rows) < 2:
        return action
    sell_rows.sort(reverse=True)
    ranked = [row[2] for row in sell_rows]
    others = [order for order in market if not _is_sell(order)]
    action["market"] = ranked + others
    return action

def agent(obs, configuration=None):
    try:
        step = int(_v43_get(obs, "step", 0) or 0)
        action = _V43_POLICY(obs, configuration)
        action = _capital_guard(obs, action, step)
        action = _monetizable_terminal_units(obs, action, step)
        action = _terminal_zero_waste_sweep(obs, action, step)
        action = _reorder_market_demand_aware(obs, action, alpha=1.0)
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

v18_file = Path("submission_v18_apex_dominator.py")
v18_file.write_text(base_engine + v18_tail, encoding="utf-8")
print(f"Generated {v18_file} ({v18_file.stat().st_size} bytes)")

v19_file = Path("submission_v19_apex_sovereign.py")
v19_file.write_text(base_engine + v19_tail, encoding="utf-8")
print(f"Generated {v19_file} ({v19_file.stat().st_size} bytes)")
