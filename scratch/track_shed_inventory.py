import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
from scratch.eval_10seeds import load_agent

a = load_agent("submission_v17_apex_colossus.py")
env = ke.make("kaggriculture", configuration={"seed": 42})
env.run([a, a])

print("=== DAY-BY-DAY SHED INVENTORY (Seed 42) ===")
for day in range(30):
    step = day * 24 + 23
    obs0 = env.steps[step][0]["observation"]
    shed0 = obs0["private"]["shed"]
    money0 = obs0["farms"][0]["money"]
    valuable = {k: v for k, v in shed0.items() if v > 0 and k != 'WHEAT'}
    if valuable:
        print(f"Day {day:2d} (Step {step:3d}): Money=${money0:6.0f} | Valuable in shed: {valuable}")
