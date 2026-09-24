import os

with open("submission_v16_apex_titan.py", "r", encoding="utf-8") as f:
    text = f.read()

# Replace _weed_repair_action with clean opportunistic DIG and remove the dummy _WEED_STATE
target_weed = '''# --- V115 Closed-Loop Weed Repair Guard ---
_WEED_STATE = {0: {}, 1: {}}
_WEED_REPLAY_STEPS = 8

def _seat_guard(obs):
    return 1 if int(_v43_get(obs, "player", 0) or 0) == 1 else 0

def _farm_guard(obs, seat):
    farms = list(_v43_get(obs, "farms", []) or [])
    return farms[seat] if seat < len(farms) else {}

def _tracked_weeds(obs, step):
    seat = _seat_guard(obs)
    tracked = _WEED_STATE.setdefault(seat, {})
    if step == 0:
        tracked.clear()
    farm = _farm_guard(obs, seat)
    current = set()
    for row_idx, row in enumerate(list(_v43_get(farm, "tiles", []) or [])):
        for col_idx, tile in enumerate(list(row or [])):
            if isinstance(tile, dict) and bool(tile.get("weed")):
                coord = (row_idx, col_idx)
                current.add(coord)
                tracked.setdefault(coord, step)
    for coord in [c for c, s in list(tracked.items()) if c not in current and step - s >= _WEED_REPLAY_STEPS]:
        tracked.pop(coord, None)
    return tracked

def _weed_repair_action(obs, action, step):
    tracked = _tracked_weeds(obs, step)
    if not tracked:
        return action
    farmer = list(action.get("farmer", ["PASS"]))
    hands = [list(h) for h in action.get("hands", [])]
    
    for (r, c), s in sorted(tracked.items(), key=lambda x: x[1]):
        if farmer == ["PASS"]:
            farmer = ["CLEAR_WEED", r, c]
            tracked.pop((r, c), None)
            break
        for h_idx in range(len(hands)):
            if hands[h_idx] == ["PASS"]:
                hands[h_idx] = ["CLEAR_WEED", r, c]
                tracked.pop((r, c), None)
                break
    action["farmer"] = farmer
    action["hands"] = hands
    return action'''

replacement_weed = '''# --- V17 Grandmaster Guards & Autonomous Controllers ---
def _seat_guard(obs):
    return 1 if int(_v43_get(obs, "player", 0) or 0) == 1 else 0

def _farm_guard(obs, seat):
    farms = list(_v43_get(obs, "farms", []) or [])
    return farms[seat] if seat < len(farms) else {}

def _opportunistic_weed_dig(obs, action):
    seat = _seat_guard(obs)
    farm = _farm_guard(obs, seat)
    tiles = farm.get("tiles", [])
    if not tiles:
        return action
        
    farmer = list(action.get("farmer", ["PASS"]))
    if farmer == ["PASS"] and "farmer" in farm:
        fx, fy = farm["farmer"]
        tile = tiles[fy][fx] if 0 <= fy < len(tiles) and 0 <= fx < len(tiles[0]) else None
        if isinstance(tile, dict) and bool(tile.get("weed")):
            farmer = ["DIG"]
            
    hands = [list(h) for h in action.get("hands", [])]
    hand_positions = farm.get("hands", [])
    for idx, pos in enumerate(hand_positions):
        if idx < len(hands) and hands[idx] == ["PASS"]:
            hx, hy = pos
            tile = tiles[hy][hx] if 0 <= hy < len(tiles) and 0 <= hx < len(tiles[0]) else None
            if isinstance(tile, dict) and bool(tile.get("weed")):
                hands[idx] = ["DIG"]
                
    action["farmer"] = farmer
    action["hands"] = hands
    return action'''

assert target_weed in text, "target_weed not found"
text = text.replace(target_weed, replacement_weed)

# Update agent() function
target_agent = '''def agent(obs, configuration=None):
    try:
        step = int(_v43_get(obs, "step", 0) or 0)
        action = _V43_POLICY(obs, configuration)
        action = _weed_repair_action(obs, action, step)
        action = _capital_guard(obs, action, step)
        action = _terminal_zero_waste_sweep(obs, action, step)
        return _align_hands(action, obs)'''

replacement_agent = '''def agent(obs, configuration=None):
    try:
        step = int(_v43_get(obs, "step", 0) or 0)
        action = _V43_POLICY(obs, configuration)
        action = _opportunistic_weed_dig(obs, action)
        action = _capital_guard(obs, action, step)
        action = _terminal_zero_waste_sweep(obs, action, step)
        return _align_hands(action, obs)'''

assert target_agent in text, "target_agent not found"
text = text.replace(target_agent, replacement_agent)

with open("submission_v17_apex_colossus.py", "w", encoding="utf-8") as f:
    f.write(text)

with open("submission.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Generated submission_v17_apex_colossus.py and updated submission.py! Length:", len(text))
