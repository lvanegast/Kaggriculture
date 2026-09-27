import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v21_apex_sovereign_prime as s21

children = s21._V43_POLICY.children

def agent_via_a(obs, config=None):
    step = int(s21._v43_get(obs, "step", 0) or 0)
    town = s21._v43_get(obs, "town", {}) or {}
    shops = list(s21._v43_get(town, "unlocked_shops", []) or [])
    
    # Adaptive Yarn Route: if YARN_STORE is unlocked at all, use yarn_first from step 88
    route = "default"
    if "YARN_STORE" in shops and step >= 88:
        route = "yarn_first"
        
    actions = {name: pol(obs, config) for name, pol in children.items()}
    act = actions[route]
    
    act = s21._capital_guard(obs, act, step)
    act = s21._post_day24_fertilizer_liquidator(obs, act, step)
    act = s21._monetizable_terminal_units(obs, act, step)
    act = s21._perfect_terminal_sweep(obs, act, step)
    act = s21._reorder_market_demand_aware(obs, act, alpha=1.0)
    return s21._align_hands(act, obs)

seeds = [42, 100, 2024, 7, 999, 1234, 555, 888, 314, 2718]
scores_via_a = []
print("Evaluating Vía A (Adaptive Yarn Routing) across 10 seeds...", flush=True)
for s in seeds:
    env = ke.make("kaggriculture", configuration={"seed": s})
    env.run([agent_via_a, agent_via_a])
    s0 = env.steps[-1][0]["reward"]
    s1 = env.steps[-1][1]["reward"]
    avg = (s0 + s1) / 2
    scores_via_a.append(avg)
    print(f"Seed {s:5d}: P0=${s0:8.0f} | P1=${s1:8.0f} | Avg=${avg:8.0f}", flush=True)

print(f"\nOverall Average Vía A: ${sum(scores_via_a)/len(scores_via_a):8.1f}", flush=True)
