import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v19_apex_sovereign as s19

_SELLABLE = ('WOOL', 'MELON', 'MILK', 'STRAWBERRY', 'FERTILIZER', 'CARROT', 'TOMATO', 'EGG', 'WHEAT')

def _post_day24_fertilizer_liquidator(obs, action, step):
    if step < 596:
        return action
    private = obs.get('private', {}) if isinstance(obs, dict) else getattr(obs, 'private', {})
    shed = dict(private.get('shed', {}) if isinstance(private, dict) else {})
    fert_count = shed.get('FERTILIZER', 0)
    if fert_count <= 0:
        return action
        
    market_obs = obs.get('market', {}) if isinstance(obs, dict) else getattr(obs, 'market', {})
    prices = market_obs.get('prices', {}) if isinstance(market_obs, dict) else {}
    fert_price = prices.get('FERTILIZER', 1)
    
    if fert_price <= 1:
        return action
        
    market = list(action.get('market', []))
    for o in market:
        if len(o) >= 3 and o[0] == 'SELL' and o[1] == 'FERTILIZER':
            fert_count -= int(o[2])
            
    if fert_count > 0 and len(market) < 10:
        batch = min(fert_count, 3)
        market.append(['SELL', 'FERTILIZER', batch])
        action['market'] = market
        
    return action

def _perfect_terminal_sweep(obs, action, step):
    if step not in (718, 719):
        return action
    private = obs.get('private', {}) if isinstance(obs, dict) else getattr(obs, 'private', {})
    shed = dict(private.get('shed', {}) if isinstance(private, dict) else {})
    prices = obs.get('market', {}).get('prices', {}) if isinstance(obs.get('market'), dict) else {}
    
    sells = []
    for p in _SELLABLE:
        qty = int(shed.get(p, 0) or 0)
        if qty > 0:
            price = prices.get(p, 1)
            score = price * qty
            sells.append((score, p, qty))
            
    sells.sort(reverse=True)
    action['market'] = [['SELL', p, q] for _, p, q in sells[:10]]
    return action

def agent_v20(obs, config=None):
    step = int(s19._v43_get(obs, "step", 0) or 0)
    act = s19._V43_POLICY(obs, config)
    act = s19._capital_guard(obs, act, step)
    act = _post_day24_fertilizer_liquidator(obs, act, step)
    act = s19._monetizable_terminal_units(obs, act, step)
    act = _perfect_terminal_sweep(obs, act, step)
    act = s19._reorder_market_demand_aware(obs, act, alpha=1.0)
    return s19._align_hands(act, obs)

seeds = [42, 100, 2024, 7, 999, 1234, 555, 888, 314, 2718]
scores_v20 = []
print("Evaluating agent_v20 (Fert Liquidator + Perfect Terminal Sweep) across 10 seeds...", flush=True)
for s in seeds:
    env = ke.make("kaggriculture", configuration={"seed": s})
    env.run([agent_v20, agent_v20])
    s0 = env.steps[-1][0]["reward"]
    s1 = env.steps[-1][1]["reward"]
    scores_v20.append((s0 + s1) / 2)
    print(f"Seed {s:5d}: P0=${s0:8.0f} | P1=${s1:8.0f} | Avg=${(s0+s1)/2:8.0f}", flush=True)

print(f"\nOverall Average v20 in self-play: ${sum(scores_v20)/len(scores_v20):8.1f}", flush=True)
