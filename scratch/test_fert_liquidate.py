import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v19_apex_sovereign as s19

def _post_day24_fertilizer_liquidator(obs, action, step):
    # Only after step 595 when fertilization permanently ends
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
    
    # Don't sell if price has already crashed to 1 (terminal sweep will catch it anyway)
    if fert_price <= 1:
        return action
        
    market = list(action.get('market', []))
    # Deduct existing sales
    for o in market:
        if len(o) >= 3 and o[0] == 'SELL' and o[1] == 'FERTILIZER':
            fert_count -= int(o[2])
            
    if fert_count > 0 and len(market) < 10:
        batch = min(fert_count, 3)
        market.append(['SELL', 'FERTILIZER', batch])
        action['market'] = market
        
    return action

def agent_v20(obs, config=None):
    step = int(s19._v43_get(obs, "step", 0) or 0)
    act = s19._V43_POLICY(obs, config)
    act = s19._capital_guard(obs, act, step)
    act = _post_day24_fertilizer_liquidator(obs, act, step)
    act = s19._monetizable_terminal_units(obs, act, step)
    act = s19._terminal_zero_waste_sweep(obs, act, step)
    act = s19._reorder_market_demand_aware(obs, act, alpha=1.0)
    return s19._align_hands(act, obs)

seeds = [42, 100, 2024, 7, 999, 1234, 555, 888, 314, 2718]
scores_v20 = []
print("Evaluating agent_v20 in self-play across 10 seeds...", flush=True)
for s in seeds:
    env = ke.make("kaggriculture", configuration={"seed": s})
    env.run([agent_v20, agent_v20])
    s0 = env.steps[-1][0]["reward"]
    s1 = env.steps[-1][1]["reward"]
    scores_v20.append((s0 + s1) / 2)
    print(f"Seed {s:5d}: P0=${s0:8.0f} | P1=${s1:8.0f} | Avg=${(s0+s1)/2:8.0f}", flush=True)

print(f"\nOverall Average v20: ${sum(scores_v20)/len(scores_v20):8.1f}", flush=True)
