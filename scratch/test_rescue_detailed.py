import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
from scratch.eval_10seeds import load_agent

a0 = load_agent("submission_v16_apex_titan.py")
a1 = load_agent("submission_v16_apex_titan.py")

with open("scratch/rescue_log.txt", "w") as log:
    def custom_a1(obs, config=None):
        step = obs.step
        act = a1(obs, config)
        if step in (192, 193, 194):
            log.write(f"Before Step {step}: Farmer={act.get('farmer')}, shed_cow={obs.private.shed.get('COW')}, inv_cow={obs.private.inventories[0].get('COW')}\n")
            if step == 192 and act.get("farmer") == ["FEED"]:
                log.write(f"--> Overriding step 192 to PICKUP COW 2!\n")
                act["farmer"] = ["PICKUP", "COW", 2]
            log.write(f"After Step {step}: Farmer={act.get('farmer')}\n")
        return act

    env = ke.make("kaggriculture", configuration={"seed": 7}, debug=True)
    env.run([a0, custom_a1])
    log.write(f"Final rewards: P0={env.steps[-1][0]['reward']}, P1={env.steps[-1][1]['reward']}\n")

with open("scratch/rescue_log.txt", "r") as log:
    print(log.read())
