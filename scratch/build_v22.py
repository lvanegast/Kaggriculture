import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pathlib import Path

# Load base code from v21
v21_path = Path("submission_v21_apex_sovereign_prime.py")
v21_code = v21_path.read_text(encoding="utf-8")

# Update header
v22_header = '''"""Submission v22 - Apex Bio-Harvester (Macro Vía A).

Macro Strategic Enhancements:
- Active Fertilizer Harvesting Engine: Opportunistically collects fertilizer from animal
  tiles (COLLECT_FERTILIZER) whenever workers pass through or stand on livestock tiles with
  fertilizer_available == True, monetizing biological manure into high-value market goods.
- Mid-Game Fertilizer Market Pacing: Continuously sells batches of collected fertilizer
  during Days 10-24 at peak market price ($60-$90) instead of hoarding until the endgame.
- Perfect Terminal Sweep & Pre-Terminal Unit Salvage.
- Demand-Aware Market Priority Queue.
"""'''
v22_code = v21_code.replace(v21_code[:v21_code.find("\n\nimport")], v22_header, 1)

# Active Fertilizer Harvesting routine
active_fert_code = '''
# --- V22 Active Fertilizer Harvesting Engine ---
def _active_fertilizer_harvester(obs, action, step):
    player = _seat_guard(obs)
    farm = _farm_guard(obs, player)
    tiles = farm.get("tiles", []) or []
    if not tiles:
        return action
        
    positions = [farm.get("farmer", [0, 0]), *(farm.get("hands", []) or [])]
    unit_actions = [action.get("farmer", ["PASS"]), *(action.get("hands") or [])]
    
    for idx, (raw_pos, act) in enumerate(zip(positions, unit_actions)):
        if not isinstance(raw_pos, (list, tuple)) or len(raw_pos) < 2:
            continue
        x, y = int(raw_pos[0]), int(raw_pos[1])
        if 0 <= y < len(tiles) and 0 <= x < len(tiles[0]):
            tile = tiles[y][x]
            if isinstance(tile, dict) and "animal" in tile and tile.get("fertilizer_available"):
                # If unit is currently passing or on animal tile, collect fertilizer!
                if act == ["PASS"]:
                    unit_actions[idx] = ["COLLECT_FERTILIZER"]
                    tile["fertilizer_available"] = False
                    
    action["farmer"] = unit_actions[0]
    action["hands"] = unit_actions[1:]
    return action

# --- V22 Mid-Game Fertilizer Pacer ---
def _midgame_fertilizer_pacer(obs, action, step):
    # Only active during productive mid-game (Days 10-24: steps 240-595)
    if not (240 <= step <= 595 and step % 8 == 0):
        return action
    private = obs.get("private", {}) if isinstance(obs, dict) else getattr(obs, "private", {})
    shed = dict(private.get("shed", {}) if isinstance(private, dict) else {})
    fert_count = int(shed.get("FERTILIZER", 0) or 0)
    
    # Keep at least 8 fertilizer for operational crop use
    surplus_fert = max(0, fert_count - 8)
    if surplus_fert <= 0:
        return action
        
    market_obs = obs.get("market", {}) if isinstance(obs, dict) else getattr(obs, "market", {})
    prices = market_obs.get("prices", {}) if isinstance(market_obs, dict) else {}
    fert_price = prices.get("FERTILIZER", 0)
    
    if fert_price >= 40:
        market = list(action.get("market", []))
        if len(market) < 10:
            batch = min(surplus_fert, 3)
            market.append(["SELL", "FERTILIZER", batch])
            action["market"] = market
            
    return action
'''

# Insert active_fert_code right before _post_day24_fertilizer_liquidator
v22_code = v22_code.replace(
    "# --- V20 Post-Day 24 Fertilizer Liquidator ---",
    active_fert_code + "\n# --- V20 Post-Day 24 Fertilizer Liquidator ---"
)

# Update agent() in v22
old_agent = '''def agent(obs, configuration=None):
    try:
        step = int(_v43_get(obs, "step", 0) or 0)
        action = _V43_POLICY(obs, configuration)
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
        action = _capital_guard(obs, action, step)
        action = _post_day24_fertilizer_liquidator(obs, action, step)
        action = _monetizable_terminal_units(obs, action, step)
        action = _perfect_terminal_sweep(obs, action, step)
        action = _reorder_market_demand_aware(obs, action, alpha=1.0)
        return _align_hands(action, obs)'''

v22_code = v22_code.replace(old_agent, new_agent)
Path("submission_v22_apex_bio_harvester.py").write_text(v22_code, encoding="utf-8")
print("Wrote submission_v22_apex_bio_harvester.py successfully!")
