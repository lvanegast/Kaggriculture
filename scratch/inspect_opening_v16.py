import sys
from pathlib import Path
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))

import kaggle_environments as ke
import submission_v16_apex_titan as v16

env = ke.make("kaggriculture", configuration={"seed": 42})
env.reset()

steps_to_inspect = {0, 1, 2, 3, 4, 5, 6, 28, 29, 30, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57}

while env.steps[-1][0]["observation"]["step"] <= 58:
    obs0 = env.steps[-1][0]["observation"]
    step = obs0["step"]
    a0 = v16.agent(obs0)
    a1 = v16.agent(env.steps[-1][1]["observation"])
    if step in steps_to_inspect:
        print(f"Step {step:2d}: Farmer={a0.get('farmer')}, Hands={a0.get('hands')}, Market={a0.get('market')}")
    env.step([a0, a1])
