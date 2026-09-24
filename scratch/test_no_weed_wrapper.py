import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v16_apex_titan as s16

def agent_clean(obs, config=None):
    step = int(s16._v43_get(obs, "step", 0) or 0)
    action = s16._V43_POLICY(obs, config)
    # WITHOUT _weed_repair_action (which sends invalid CLEAR_WEED)
    action = s16._capital_guard(obs, action, step)
    action = s16._terminal_zero_waste_sweep(obs, action, step)
    return s16._align_hands(action, obs)

seeds = [42, 100, 2024, 7, 999, 1234, 555, 888, 314, 2718]
scores = []
print("Evaluating agent_clean (without broken CLEAR_WEED) across 10 seeds...")
for s in seeds:
    env = ke.make("kaggriculture", configuration={"seed": s})
    env.run([agent_clean, agent_clean])
    s0 = env.steps[-1][0]["reward"]
    s1 = env.steps[-1][1]["reward"]
    scores.append((s0 + s1) / 2)
    print(f"Seed {s:5d}: P0=${s0:8.0f} | P1=${s1:8.0f}")

print(f"\nAverage without broken CLEAR_WEED: ${sum(scores)/len(scores):8.1f}")
