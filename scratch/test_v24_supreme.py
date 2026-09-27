import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v23_apex_arbitrageur as s23

children = s23._V43_POLICY.children

def agent_v24_supreme(obs, config=None):
    step = int(s23._v43_get(obs, "step", 0) or 0)
    town = s23._v43_get(obs, "town", {}) or {}
    shops = list(s23._v43_get(town, "unlocked_shops", []) or [])
    
    # Smart Adaptive Shop Routing
    route = "default"
    if shops:
        if shops[0] == "YARN_STORE" and step >= 88:
            route = "yarn_first"
        elif "YARN_STORE" in shops and step >= 153:
            route = "yarn_second"
            
    actions = {name: pol(obs, config) for name, pol in children.items()}
    act = actions[route]
    
    act = s23._active_fertilizer_harvester(obs, act, step)
    act = s23._midgame_fertilizer_pacer(obs, act, step)
    act = s23._universal_town_arbitrageur(obs, act, step)
    act = s23._capital_guard(obs, act, step)
    act = s23._post_day24_fertilizer_liquidator(obs, act, step)
    act = s23._monetizable_terminal_units(obs, act, step)
    act = s23._perfect_terminal_sweep(obs, act, step)
    act = s23._reorder_market_demand_aware(obs, act, alpha=1.0)
    return s23._align_hands(act, obs)

seeds = [42, 100, 2024, 7, 999, 1234, 555, 888, 314, 2718]
scores = []
print("Evaluating v24 Supreme (Adaptive Route + Arbitrageur + Bio-Harvester)...")
for s in seeds:
    env = ke.make("kaggriculture", configuration={"seed": s})
    env.run([agent_v24_supreme, agent_v24_supreme])
    s0 = env.steps[-1][0]["reward"]
    s1 = env.steps[-1][1]["reward"]
    avg = (s0 + s1) / 2
    scores.append(avg)
    print(f"Seed {s:5d}: P0=${s0:8.0f} | P1=${s1:8.0f} | Avg=${avg:8.0f}")

print(f"\nOverall Average v24 Supreme: ${sum(scores)/len(scores):8.1f}")
