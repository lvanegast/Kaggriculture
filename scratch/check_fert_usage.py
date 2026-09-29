import sys
from pathlib import Path
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))

import kaggle_environments as ke
import submission_v16_apex_titan as v16

env = ke.make("kaggriculture", configuration={"seed": 42})
env.reset()

fert_actions = []

while not env.done:
    obs0 = env.steps[-1][0]["observation"]
    obs1 = env.steps[-1][1]["observation"]
    step = obs0["step"]
    a0 = v16.agent(obs0)
    a1 = v16.agent(obs1)
    
    # check if any unit in a0 does FERTILIZE
    unit_acts = [a0.get("farmer", ["PASS"])] + a0.get("hands", [])
    for u in unit_acts:
        if u and u[0] == "FERTILIZE":
            fert_actions.append((step, u))
            
    env.step([a0, a1])

print(f"Total FERTILIZE actions in match: {len(fert_actions)}")
late_fert = [x for x in fert_actions if x[0] >= 596]
print(f"Late FERTILIZE actions (step >= 596): {len(late_fert)}")
for s, u in late_fert[:10]:
    print(f"  Step {s}: {u}")
