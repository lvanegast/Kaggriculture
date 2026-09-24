import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
from scratch.eval_10seeds import load_agent

a1 = load_agent("submission_v16_apex_titan.py")

with open("scratch/debug_out.txt", "w") as out:
    def debug_a1(obs, config=None):
        out.write(f"type: {type(obs)}, keys: {list(obs.keys())[:5]}\n")
        return a1(obs, config)

    env = ke.make("kaggriculture", configuration={"seed": 7})
    env.run([load_agent("submission_v16_apex_titan.py"), debug_a1])
    out.write(f"Done! P0={env.steps[-1][0]['reward']}, P1={env.steps[-1][1]['reward']}\n")

with open("scratch/debug_out.txt", "r") as out:
    lines = out.readlines()
    print("Logged lines:", len(lines))
    print("First 5 lines:", lines[:5])
    print("Last 2 lines:", lines[-2:])
