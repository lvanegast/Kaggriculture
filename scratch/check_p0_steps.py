import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
from scratch.eval_10seeds import load_agent

def run():
    env = ke.make("kaggriculture", configuration={"seed": 7})
    a0 = load_agent("submission_v16_apex_titan.py")
    a1 = load_agent("submission_v16_apex_titan.py")
    env.run([a0, a1])
    
    for step in range(191, 202):
        s = env.steps[step][0]
        obs = s["observation"]
        farm = obs["farms"][0]
        priv = obs["private"]
        pos = farm["farmer"]
        cows = priv["shed"].get("COW", 0)
        inv = priv["inventories"][0]
        act = s.get("action", {})
        farmer_act = act.get("farmer") if act else None
        print(f"Step {step:3d}: P0 Farmer pos={pos}, shed={cows}, inv={inv}, act={farmer_act}")

if __name__ == "__main__":
    run()
