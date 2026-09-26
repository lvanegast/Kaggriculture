import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v19_apex_sovereign as s19

def _suppress_dead_wheat_planting(action, step):
    # Any wheat planted after step 624 cannot mature in 96 steps before step 720
    if step < 624:
        return action
        
    farmer = list(action.get("farmer", ["PASS"]))
    if len(farmer) >= 2 and farmer[0] == "PLANT" and farmer[1] == "WHEAT":
        farmer = ["PASS"]
        
    hands = [list(h) for h in action.get("hands", [])]
    for idx, h in enumerate(hands):
        if len(h) >= 2 and h[0] == "PLANT" and h[1] == "WHEAT":
            hands[idx] = ["PASS"]
            
    action["farmer"] = farmer
    action["hands"] = hands
    return action

def agent_smart_late(obs, config=None):
    step = int(s19._v43_get(obs, "step", 0) or 0)
    act = s19._V43_POLICY(obs, config)
    act = s19._capital_guard(obs, act, step)
    act = _suppress_dead_wheat_planting(act, step)
    act = s19._monetizable_terminal_units(obs, act, step)
    act = s19._terminal_zero_waste_sweep(obs, act, step)
    act = s19._reorder_market_demand_aware(obs, act, alpha=1.0)
    return s19._align_hands(act, obs)

if __name__ == "__main__":
    seeds = [42, 100, 2024, 7, 999, 1234, 555, 888, 314, 2718]
    scores_new = []
    scores_v19 = []
    print("Evaluating agent_smart_late vs v19 across 10 seeds...", flush=True)
    for s in seeds:
        env = ke.make("kaggriculture", configuration={"seed": s})
        env.run([agent_smart_late, agent_smart_late])
        s0 = env.steps[-1][0]["reward"]
        s1 = env.steps[-1][1]["reward"]
        scores_new.append((s0 + s1) / 2)
        print(f"Seed {s:5d}: P0=${s0:8.0f} | P1=${s1:8.0f} | Avg=${(s0+s1)/2:8.0f}", flush=True)

    print(f"\nOverall Average: ${sum(scores_new)/len(scores_new):8.1f}", flush=True)
