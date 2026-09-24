import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v16_apex_titan as s16
import traceback

def buggy_agent(obs, config=None):
    step = int(obs.step)
    try:
        act = s16._V43_POLICY(obs, config)
        act = s16._weed_repair_action(obs, act, step)
        act = s16._capital_guard(obs, act, step)
        act = s16._terminal_zero_waste_sweep(obs, act, step)
        act = s16._align_hands(act, obs)
        if step == 192 and act.get("farmer") == ["FEED"]:
            act["farmer"] = ["PICKUP", "COW", 2]
        return act
    except Exception as e:
        print(f"!!! EXCEPTION at step {step}: {e} !!!")
        traceback.print_exc()
        raise e

env = ke.make("kaggriculture", configuration={"seed": 7})
env.run([s16.agent, buggy_agent])
