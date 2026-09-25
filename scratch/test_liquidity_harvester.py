import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v17_apex_colossus as s17

_CASH_CROPS = ('WOOL', 'MILK', 'STRAWBERRY', 'MELON', 'FERTILIZER')

def liquidity_harvester(obs, action, step):
    private = obs.get('private', {}) if isinstance(obs, dict) else getattr(obs, 'private', {})
    shed = dict(private.get('shed', {}) if isinstance(private, dict) else {})
    market = list(action.get('market', []))
    
    # Deduct existing sell orders
    for o in market:
        if len(o) >= 3 and o[0] == 'SELL' and o[1] in shed:
            shed[o[1]] = max(0, shed[o[1]] - int(o[2]))
            
    # Every 4 steps (coinciding with townShopSellInterval = 4), liquidate surplus high-value goods
    if step % 4 == 0 and step >= 240:
        for p in _CASH_CROPS:
            rem = shed.get(p, 0)
            if rem > 0 and len(market) < 10:
                market.append(['SELL', p, rem])
                shed[p] = 0
                
    action['market'] = market
    return action

def agent_harvester(obs, config=None):
    step = int(s17._v43_get(obs, "step", 0) or 0)
    act = s17._V43_POLICY(obs, config)
    act = s17._opportunistic_weed_dig(obs, act)
    act = s17._capital_guard(obs, act, step)
    act = liquidity_harvester(obs, act, step)
    act = s17._terminal_zero_waste_sweep(obs, act, step)
    return s17._align_hands(act, obs)

seeds = [42, 100, 2024, 7, 999, 1234, 555, 888, 314, 2718]
scores = []
print("Evaluating agent_harvester across 10 seeds...")
for s in seeds:
    env = ke.make("kaggriculture", configuration={"seed": s})
    env.run([agent_harvester, agent_harvester])
    s0 = env.steps[-1][0]["reward"]
    s1 = env.steps[-1][1]["reward"]
    scores.append((s0 + s1) / 2)
    print(f"Seed {s:5d}: P0=${s0:8.0f} | P1=${s1:8.0f} | Avg=${(s0+s1)/2:8.0f}")

print(f"\nOverall Average: ${sum(scores)/len(scores):8.1f}")
