import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v16_apex_titan as s16
from scratch.eval_10seeds import load_agent

a = load_agent("submission_v16_apex_titan.py")
seeds = [42, 100, 2024, 7, 999, 1234, 555, 888, 314, 2718]

for s in seeds:
    env = ke.make("kaggriculture", configuration={"seed": s})
    env.run([a, a])
    for step_num in (96, 97, 154, 157, 168, 192, 248):
        if step_num < len(env.steps):
            # check if buy animal succeeded
            # in observation private: shed animal counts
            for p in (0, 1):
                obs = env.steps[step_num][p]["observation"]
                money = obs["farms"][p]["money"]
                shed = obs["private"]["shed"]
                # print if money is close to deficit
                if money < 100:
                    print(f"Seed {s:5d}, Step {step_num:3d}, Player {p}: TIGHT MONEY = ${money:.0f}, shed cows={shed.get('COW')}, sheep={shed.get('SHEEP')}")
