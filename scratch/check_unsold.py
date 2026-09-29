import sys
from pathlib import Path
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))

import kaggle_environments as ke
import submission_v16_apex_titan as v16

seeds = [42, 100, 2024, 7, 999, 1234, 555, 888, 314, 2718]

for s in seeds:
    env = ke.make("kaggriculture", configuration={"seed": s})
    env.reset()
    while not env.done:
        obs0 = env.steps[-1][0]["observation"]
        obs1 = env.steps[-1][1]["observation"]
        a0 = v16.agent(obs0)
        a1 = v16.agent(obs1)
        env.step([a0, a1])
    final_obs0 = env.steps[-1][0]["observation"]
    shed0 = final_obs0["private"]["shed"]
    non_zero = {k: v for k, v in shed0.items() if v > 0}
    reward = env.steps[-1][0]["reward"]
    print(f"Seed {s}: Reward={reward:.1f}, Unsold Shed={non_zero}")
