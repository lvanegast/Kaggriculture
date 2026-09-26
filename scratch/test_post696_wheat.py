import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v19_apex_sovereign as s19

env = ke.make("kaggriculture", configuration={"seed": 42})
env.run([s19.agent, s19.agent])

# Check shed wheat inventory from step 690 to 720
print("Step | Wheat in Shed | Wheat Price | Reward P0 | Reward P1")
for st in range(694, 720):
    obs0 = env.steps[st][0]["observation"]
    obs1 = env.steps[st][1]["observation"]
    w0 = obs0["private"]["shed"].get("WHEAT", 0)
    p = obs0["market"]["prices"].get("WHEAT", 0)
    r0 = env.steps[st][0].get("reward", 0)
    r1 = env.steps[st][1].get("reward", 0)
    print(f"{st:4d} | Shed Wheat: {w0:3d} | Price: ${p:2d} | R0: {r0} | R1: {r1}")
