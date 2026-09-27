import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

v22_code = Path("submission_v22_apex_bio_harvester.py").read_text(encoding="utf-8")

# Update header
v24_header = '''"""Submission v24 - Apex Thunder Scale (Macro Vía C).

Macro Strategic Enhancements:
- Macro Labor Scaling Engine (12-Hand Workforce): Expands beyond the standard 10-hand
  barrier by hiring auxiliary farm hands on Days 10+ when daily cash flows exceed $1,200.
- Auxiliary Labor Allocation: Extra hands actively patrol unlocked quadrants for weed clearance
  (DIG) and livestock maintenance (COLLECT_FERTILIZER), scaling farm actions to >300 ops/day.
- Active Fertilizer Harvesting Engine & Mid-Game Pacing.
- Perfect Terminal Market Sweep & Pre-Terminal Unit Salvage.
"""'''
v24_code = v22_code.replace(v22_code[:v22_code.find("\n\nimport")], v24_header, 1)

labor_code = '''
# --- V24 Macro Labor Scaling Engine ---
def _macro_labor_scaler(obs, action, step):
    player = _seat_guard(obs)
    farm = _farm_guard(obs, player)
    money = float(_v43_get(farm, "money", 0) or 0)
    hands = list(_v43_get(farm, "hands", []) or [])
    
    # On start of day (step % 24 == 0) from Day 10 to Day 20, if cash is strong, hire auxiliary hand!
    if step in (240, 360) and len(hands) < 12 and money >= 1200.0:
        market = list(action.get("market", []))
        if len(market) < 10:
            market.append(["HIRE"])
            action["market"] = market
            
    return action

# --- V24 Auxiliary Worker Controller ---
def _auxiliary_worker_controller(obs, action, step):
    player = _seat_guard(obs)
    farm = _farm_guard(obs, player)
    tiles = farm.get("tiles", []) or []
    if not tiles:
        return action
        
    hands_pos = list(farm.get("hands", []) or [])
    # Only manage extra hands beyond the baseline 10
    if len(hands_pos) <= 10:
        return action
        
    hands_act = list(action.get("hands", []))
    # Ensure action array matches current hand count
    while len(hands_act) < len(hands_pos):
        hands_act.append(["PASS"])
        
    # Check for unweeded tiles or fertilizer tiles
    for idx in range(10, len(hands_pos)):
        pos = hands_pos[idx]
        if not isinstance(pos, (list, tuple)) or len(pos) < 2:
            continue
        x, y = int(pos[0]), int(pos[1])
        t = tiles[y][x] if 0 <= y < len(tiles) and 0 <= x < len(tiles[0]) else None
        
        # If standing on weed, dig!
        if isinstance(t, dict) and t.get("kind") == "WEED":
            hands_act[idx] = ["DIG"]
        # If standing on animal with fertilizer, collect!
        elif isinstance(t, dict) and "animal" in t and t.get("fertilizer_available"):
            hands_act[idx] = ["COLLECT_FERTILIZER"]
            t["fertilizer_available"] = False
        else:
            # Move towards center/access if far away
            if x > 4:
                hands_act[idx] = ["WEST"]
            elif y > 4:
                hands_act[idx] = ["NORTH"]
                
    action["hands"] = hands_act
    return action
'''

# Insert labor scaling code
v24_code = v24_code.replace(
    "# --- V22 Active Fertilizer Harvesting Engine ---",
    labor_code + "\n# --- V22 Active Fertilizer Harvesting Engine ---"
)

# Update agent() in v24
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
        action = _macro_labor_scaler(obs, action, step)
        action = _auxiliary_worker_controller(obs, action, step)
        action = _active_fertilizer_harvester(obs, action, step)
        action = _midgame_fertilizer_pacer(obs, action, step)
        action = _capital_guard(obs, action, step)
        action = _post_day24_fertilizer_liquidator(obs, action, step)
        action = _monetizable_terminal_units(obs, action, step)
        action = _perfect_terminal_sweep(obs, action, step)
        action = _reorder_market_demand_aware(obs, action, alpha=1.0)
        return _align_hands(action, obs)'''

v24_code = v24_code.replace(old_agent, new_agent)
Path("submission_v24_apex_thunder_scale.py").write_text(v24_code, encoding="utf-8")
print("Wrote submission_v24_apex_thunder_scale.py successfully!")
