import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

v22_code = Path("submission_v22_apex_bio_harvester.py").read_text(encoding="utf-8")

# Update header
v23_header = '''"""Submission v23 - Apex Arbitrageur (Macro Vía B).

Macro Strategic Enhancements:
- Universal Town Arbitrage Engine: Continuously anticipates town shop consumption ticks
  (Smoothie Shop, Farmers Market, Brunch Spot, Bakery, Yarn Store). Executes high-margin
  one-tick arbitrage by buying under-priced town staples immediately before town demand
  and liquidating on the subsequent tick at peak price.
- Active Fertilizer Harvesting Engine: Opportunistically collects fertilizer from animal
  tiles (COLLECT_FERTILIZER), monetizing manure into premium cash flow.
- Mid-Game Fertilizer Market Pacing (Days 10-24 at $60-$90/unit).
- Perfect Terminal Market Sweep & Pre-Terminal Unit Salvage.
"""'''
v23_code = v22_code.replace(v22_code[:v22_code.find("\n\nimport")], v23_header, 1)

arbitrage_code = '''
# --- V23 Universal Town Arbitrage Engine ---
_ARBITRAGE_PRODUCTS = {
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("STRAWBERRY", "TOMATO", "CARROT", "WHEAT"),
    "BRUNCH_SPOT": ("STRAWBERRY", "EGG", "WHEAT"),
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "YARN_STORE": ("WOOL",),
}

_ARBITRAGE_STATE = {"holding": None, "buy_step": -1, "qty": 0}

def _universal_town_arbitrageur(obs, action, step):
    global _ARBITRAGE_STATE
    player = _seat_guard(obs)
    farm = _farm_guard(obs, player)
    money = float(_v43_get(farm, "money", 0) or 0)
    town = obs.get("town", {}) if isinstance(obs, dict) else getattr(obs, "town", {})
    unlocked = list(town.get("unlocked_shops", []) or [])
    market_obs = obs.get("market", {}) if isinstance(obs, dict) else getattr(obs, "market", {})
    inventory = market_obs.get("inventory", {}) if isinstance(market_obs, dict) else {}
    prices = market_obs.get("prices", {}) if isinstance(market_obs, dict) else {}
    
    market = list(action.get("market", []))
    
    # Reset at game start
    if step == 0:
        _ARBITRAGE_STATE = {"holding": None, "buy_step": -1, "qty": 0}
        
    # Phase 2: Liquidate existing arbitrage holding on next tick
    holding = _ARBITRAGE_STATE.get("holding")
    if holding is not None and step == _ARBITRAGE_STATE.get("buy_step", -1) + 1:
        qty = _ARBITRAGE_STATE.get("qty", 0)
        private = obs.get("private", {}) if isinstance(obs, dict) else getattr(obs, "private", {})
        shed = private.get("shed", {}) if isinstance(private, dict) else {}
        actual_in_shed = int(shed.get(holding, 0) or 0)
        sell_qty = min(qty, actual_in_shed)
        if sell_qty > 0 and len(market) < 10:
            market.append(["SELL", holding, sell_qty])
            action["market"] = market
        _ARBITRAGE_STATE = {"holding": None, "buy_step": -1, "qty": 0}
        return action

    # Phase 1: Enter arbitrage 1 tick before town consumption (step % 4 == 3)
    if (step + 1) % 4 == 0 and 120 <= step <= 670 and money > 3500.0 and len(market) < 9:
        # Find candidates consumed by active town shops
        candidates = set()
        for shop in unlocked:
            for item in _ARBITRAGE_PRODUCTS.get(shop, ()):
                if item != "WHEAT":  # protect wheat feed
                    candidates.add(item)
                    
        # Score candidates by unit margin
        best_item = None
        best_score = 0
        for item in candidates:
            inv = int(inventory.get(item, 10000) or 10000)
            p = int(prices.get(item, 100) or 100)
            if inv < 10000:  # already scarce, demand will push price even higher
                score = p
                if score > best_score:
                    best_score = score
                    best_item = item
                    
        if best_item and best_score > 50:
            qty = 2
            market.append(["BUY_PRODUCT", best_item, qty])
            action["market"] = market
            _ARBITRAGE_STATE = {"holding": best_item, "buy_step": step, "qty": qty}
            
    return action
'''

# Insert arbitrage code
v23_code = v23_code.replace(
    "# --- V22 Active Fertilizer Harvesting Engine ---",
    arbitrage_code + "\n# --- V22 Active Fertilizer Harvesting Engine ---"
)

# Update agent() in v23
old_agent = '''def agent(obs, configuration=None):
    try:
        step = int(_v43_get(obs, "step", 0) or 0)
        action = _V43_POLICY(obs, configuration)
        action = _active_fertilizer_harvester(obs, action, step)
        action = _midgame_fertilizer_pacer(obs, action, step)
        action = _capital_guard(obs, action, step)
        action = _post_day24_fertilizer_liquidator(obs, action, step)
        action = _monetizable_terminal_units(obs, action, step)
        action = _perfect_terminal_sweep(obs, action, step)
        action = _reorder_market_demand_aware(obs, action, alpha=1.0)
        return _align_hands(action, obs)'''

new_agent = '''def agent(obs, configuration=None):
    try:
        step = int(_v43_get(obs, "step", 0) or 0)
        action = _V43_POLICY(obs, configuration)
        action = _active_fertilizer_harvester(obs, action, step)
        action = _midgame_fertilizer_pacer(obs, action, step)
        action = _universal_town_arbitrageur(obs, action, step)
        action = _capital_guard(obs, action, step)
        action = _post_day24_fertilizer_liquidator(obs, action, step)
        action = _monetizable_terminal_units(obs, action, step)
        action = _perfect_terminal_sweep(obs, action, step)
        action = _reorder_market_demand_aware(obs, action, alpha=1.0)
        return _align_hands(action, obs)'''

v23_code = v23_code.replace(old_agent, new_agent)
Path("submission_v23_apex_arbitrageur.py").write_text(v23_code, encoding="utf-8")
print("Wrote submission_v23_apex_arbitrageur.py successfully!")
