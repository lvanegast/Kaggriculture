import os

with open('submission_v15_premium_titan.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = 'def agent(obs, configuration=None):'
idx = text.find(target)
if idx == -1:
    raise ValueError('agent function not found')

enhancements = '''# --- V16 Grandmaster Capital Guard & Zero-Waste Enhancements ---
_PRODUCTS_ORDER = ('WOOL', 'MELON', 'MILK', 'STRAWBERRY', 'FERTILIZER', 'CARROT', 'TOMATO', 'EGG', 'WHEAT')

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

'''

new_agent = '''def agent(obs, configuration=None):
    try:
        step = int(_v43_get(obs, "step", 0) or 0)
        action = _V43_POLICY(obs, configuration)
        action = _weed_repair_action(obs, action, step)
        action = _capital_guard(obs, action, step)
        action = _terminal_zero_waste_sweep(obs, action, step)
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

new_text = text[:idx] + enhancements + new_agent

with open('submission_v16_apex_titan.py', 'w', encoding='utf-8') as f:
    f.write(new_text)

print('Successfully generated submission_v16_apex_titan.py! Length:', len(new_text))
