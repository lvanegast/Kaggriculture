import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v19_apex_sovereign as s19

def _fertilizer_race_and_surplus_drain(obs, action, step):
    private = obs.get('private', {}) if isinstance(obs, dict) else getattr(obs, 'private', {})
    shed = dict(private.get('shed', {}) if isinstance(private, dict) else {})
    market_obs = obs.get('market', {}) if isinstance(obs, dict) else getattr(obs, 'market', {})
    prices = market_obs.get('prices', {}) if isinstance(market_obs, dict) else {}
    farms = obs.get('farms', []) if isinstance(obs, dict) else getattr(obs, 'farms', [])
    player = s19._seat_guard(obs)
    farm = farms[player] if player < len(farms) else {}
    
    market = list(action.get('market', []))
    
    # Existing sell orders
    for o in market:
        if len(o) >= 3 and o[0] == 'SELL' and o[1] in shed:
            shed[o[1]] = max(0, shed[o[1]] - int(o[2]))
            
    # Calculate animal count for feed security
    animals_count = 0
    for r in farm.get('tiles', []) or []:
        for t in r:
            if isinstance(t, dict) and 'animal' in t:
                animals_count += 1
                
    day = step // 24
    remaining_days = max(0, 30 - day)
    needed_feed = animals_count * remaining_days
    
    # 1. Fertilizer Race: Sell fertilizer while price is high (step >= 72 and step % 4 == 0)
    if step >= 72 and step % 4 == 0:
        fert_price = prices.get('FERTILIZER', 100)
        fert_shed = shed.get('FERTILIZER', 0)
        if fert_price >= 40 and fert_shed > 0 and len(market) < 10:
            batch = min(fert_shed, 3)
            market.append(['SELL', 'FERTILIZER', batch])
            shed['FERTILIZER'] -= batch

    # 2. Surplus Cash Crops (Strawberry, Milk, Wool): sell surplus above buffer at step % 4 == 0
    if step >= 240 and step % 4 == 0:
        for crop in ('STRAWBERRY', 'MILK', 'WOOL'):
            rem = shed.get(crop, 0)
            if rem >= 4 and len(market) < 10:
                batch = min(rem, 3)
                market.append(['SELL', crop, batch])
                shed[crop] -= batch

    # 3. Late-game Wheat Drain: Sell wheat exceeding animal feed requirement at peak price
    if step >= 576 and step % 4 == 0:
        wheat_rem = shed.get('WHEAT', 0)
        safe_wheat_surplus = max(0, wheat_rem - (needed_feed + 4))
        if safe_wheat_surplus > 0 and len(market) < 10:
            batch = min(safe_wheat_surplus, 4)
            market.append(['SELL', 'WHEAT', batch])
            shed['WHEAT'] -= batch
            
    action['market'] = market
    return action

def agent_v20_candidate(obs, config=None):
    step = int(s19._v43_get(obs, "step", 0) or 0)
    act = s19._V43_POLICY(obs, config)
    act = s19._capital_guard(obs, act, step)
    act = _fertilizer_race_and_surplus_drain(obs, act, step)
    act = s19._monetizable_terminal_units(obs, act, step)
    act = s19._terminal_zero_waste_sweep(obs, act, step)
    act = s19._reorder_market_demand_aware(obs, act, alpha=1.0)
    return s19._align_hands(act, obs)

if __name__ == "__main__":
    seeds = [42, 100, 2024, 7, 999, 1234, 555, 888, 314, 2718]
    scores = []
    print("Evaluating agent_v20_candidate in self-play across 10 seeds...", flush=True)
    for s in seeds:
        env = ke.make("kaggriculture", configuration={"seed": s})
        env.run([agent_v20_candidate, agent_v20_candidate])
        s0 = env.steps[-1][0]["reward"]
        s1 = env.steps[-1][1]["reward"]
        scores.append((s0 + s1) / 2)
        print(f"Seed {s:5d}: P0=${s0:8.0f} | P1=${s1:8.0f} | Avg=${(s0+s1)/2:8.0f}", flush=True)

    print(f"\nOverall Average: ${sum(scores)/len(scores):8.1f}", flush=True)
