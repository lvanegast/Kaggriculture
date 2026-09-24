import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v16_apex_titan as s16
from scripts.v22_market_impact import reorder_market

def agent_front(obs, config=None):
    step = int(obs.get('step', 0) or 0)
    act = s16._V43_POLICY(obs, config)
    # Apply impact_front instead of impact_slots
    act = reorder_market(obs, act, mode="impact_front")
    act = s16._capital_guard(obs, act, step)
    act = s16._terminal_zero_waste_sweep(obs, act, step)
    return s16._align_hands(act, obs)

seeds = [42, 100, 2024, 7, 999, 1234, 555, 888, 314, 2718]
scores_front = []
print("Evaluating impact_front across 10 seeds...")
for s in seeds:
    env = ke.make("kaggriculture", configuration={"seed": s})
    env.run([agent_front, agent_front])
    s0 = env.steps[-1][0]["reward"]
    s1 = env.steps[-1][1]["reward"]
    scores_front.append((s0 + s1) / 2)
    print(f"Seed {s:5d}: P0=${s0:8.0f} | P1=${s1:8.0f}")

print(f"\nAverage with impact_front: ${sum(scores_front)/len(scores_front):8.1f}")
