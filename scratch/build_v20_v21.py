from pathlib import Path

v19_path = Path("submission_v19_apex_sovereign.py")
v19_content = v19_path.read_text(encoding="utf-8")

# --- BUILD V20 ---
v20_content = v19_content

# Update header
v20_header = '''"""Submission v20 - Apex Liquidator.

Enhancements over v19:
- Post-Day 24 Fertilizer Liquidation Engine: Sells surplus fertilizer after Step 595
  (when all crop fertilization permanently ceases) at peak market price ($15-$24)
  before it collapses to $1 residual value on Days 28-29.
- Demand-Aware Market Impact Reordering (alpha=1.0).
- Capital Guard (guaranteed step 97 Cow purchase under price deflation).
- Pre-Terminal Monetizable Unit Salvage (steps 717-718 drop/harvest routines).
- Terminal Zero-Waste Market Sweep (steps 718-719).
"""'''
v20_content = v20_content.replace(v20_content[:v20_content.find("\n\nimport")], v20_header, 1)

fert_liquidator_code = '''
# --- V20 Post-Day 24 Fertilizer Liquidator ---
def _post_day24_fertilizer_liquidator(obs, action, step):
    if step < 596:
        return action
    private = obs.get("private", {}) if isinstance(obs, dict) else getattr(obs, "private", {})
    shed = dict(private.get("shed", {}) if isinstance(private, dict) else {})
    fert_count = int(shed.get("FERTILIZER", 0) or 0)
    if fert_count <= 0:
        return action

    market_obs = obs.get("market", {}) if isinstance(obs, dict) else getattr(obs, "market", {})
    prices = market_obs.get("prices", {}) if isinstance(market_obs, dict) else {}
    fert_price = prices.get("FERTILIZER", 1)

    if fert_price <= 1:
        return action

    market = list(action.get("market", []))
    for o in market:
        if len(o) >= 3 and o[0] == "SELL" and o[1] == "FERTILIZER":
            fert_count -= int(o[2])

    if fert_count > 0 and len(market) < 10:
        batch = min(fert_count, 3)
        market.append(["SELL", "FERTILIZER", batch])
        action["market"] = market

    return action
'''

# Insert fert_liquidator_code right before _monetizable_terminal_units
v20_content = v20_content.replace(
    "# --- V19 Pre-Terminal Unit Salvage ---",
    fert_liquidator_code + "\n# --- V20 Pre-Terminal Unit Salvage ---"
)

# Update agent() in v20
old_agent_v20 = '''def agent(obs, configuration=None):
    try:
        step = int(_v43_get(obs, "step", 0) or 0)
        action = _V43_POLICY(obs, configuration)
        action = _capital_guard(obs, action, step)
        action = _monetizable_terminal_units(obs, action, step)
        action = _terminal_zero_waste_sweep(obs, action, step)
        action = _reorder_market_demand_aware(obs, action, alpha=1.0)
        return _align_hands(action, obs)'''

new_agent_v20 = '''def agent(obs, configuration=None):
    try:
        step = int(_v43_get(obs, "step", 0) or 0)
        action = _V43_POLICY(obs, configuration)
        action = _capital_guard(obs, action, step)
        action = _post_day24_fertilizer_liquidator(obs, action, step)
        action = _monetizable_terminal_units(obs, action, step)
        action = _terminal_zero_waste_sweep(obs, action, step)
        action = _reorder_market_demand_aware(obs, action, alpha=1.0)
        return _align_hands(action, obs)'''

v20_content = v20_content.replace(old_agent_v20, new_agent_v20)
Path("submission_v20_apex_liquidator.py").write_text(v20_content, encoding="utf-8")
print("Wrote submission_v20_apex_liquidator.py")

# --- BUILD V21 ---
v21_content = v20_content

# Update header
v21_header = '''"""Submission v21 - Apex Sovereign Prime.

Enhancements over v20:
- Perfect Terminal Sweep: Replaces raw market orders at steps 718-719 with strictly
  verified non-zero shed inventory, ranked by total monetizable value (price * quantity),
  purging ghost/zero-quantity market orders that eat up the 10-order market capacity.
- Post-Day 24 Fertilizer Liquidation Engine: Sells surplus fertilizer after Step 595
  at peak market price ($15-$24) before it collapses to $1 residual value.
- Demand-Aware Market Impact Reordering (alpha=1.0).
- Capital Guard (guaranteed step 97 Cow purchase under price deflation).
- Pre-Terminal Monetizable Unit Salvage (steps 717-718 drop/harvest routines).
"""'''
v21_content = v21_content.replace(v20_header, v21_header, 1)

perfect_sweep_code = '''# --- V21 Perfect Terminal Sweep ---
def _perfect_terminal_sweep(obs, action, step):
    if step not in (718, 719):
        return action
    private = obs.get("private", {}) if isinstance(obs, dict) else getattr(obs, "private", {})
    shed = dict(private.get("shed", {}) if isinstance(private, dict) else {})
    prices = obs.get("market", {}).get("prices", {}) if isinstance(obs.get("market"), dict) else {}

    sells = []
    for p in _PRODUCTS_ORDER:
        qty = int(shed.get(p, 0) or 0)
        if qty > 0:
            price = prices.get(p, 1)
            score = price * qty
            sells.append((score, p, qty))

    sells.sort(reverse=True)
    action["market"] = [["SELL", p, q] for _, p, q in sells[:10]]
    return action
'''

# Replace _terminal_zero_waste_sweep with _perfect_terminal_sweep in v21
v21_content = v21_content.replace(
    '''# --- V19 Terminal Zero-Waste Sweep ---
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
    return action''',
    perfect_sweep_code
)

# Update agent() in v21
new_agent_v21 = '''def agent(obs, configuration=None):
    try:
        step = int(_v43_get(obs, "step", 0) or 0)
        action = _V43_POLICY(obs, configuration)
        action = _capital_guard(obs, action, step)
        action = _post_day24_fertilizer_liquidator(obs, action, step)
        action = _monetizable_terminal_units(obs, action, step)
        action = _perfect_terminal_sweep(obs, action, step)
        action = _reorder_market_demand_aware(obs, action, alpha=1.0)
        return _align_hands(action, obs)'''

v21_content = v21_content.replace(new_agent_v20, new_agent_v21)
Path("submission_v21_apex_sovereign_prime.py").write_text(v21_content, encoding="utf-8")
print("Wrote submission_v21_apex_sovereign_prime.py")
