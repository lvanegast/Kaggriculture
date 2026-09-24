import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v16_apex_titan as s16

def run_test():
    def rescuer_agent(obs, config=None):
        step = int(obs.get("step", 0) or 0)
        action = s16.agent(obs, config)
        
        seat = s16._seat_guard(obs)
        farm = s16._farm_guard(obs, seat)
        fpos = tuple(farm.get("farmer", ()))
        priv = obs.get("private", {}) if isinstance(obs, dict) else getattr(obs, "private", {})
        shed = priv.get("shed", {})
        inv = priv.get("inventories", [{}])[0]
        
        # Step 193 Cow pickup guard
        if step == 193 and fpos in [(4, 4), (5, 4), (4, 5), (5, 5)] and shed.get("COW", 0) >= 2 and inv.get("COW", 0) == 0:
            action["farmer"] = ["PICKUP", "COW", 2]
            
        return action

    print("Running Seed 7 with Step 193 Cow Rescue...")
    env = ke.make("kaggriculture", configuration={"seed": 7})
    env.run([rescuer_agent, rescuer_agent])
    s0 = env.steps[-1][0]["reward"]
    s1 = env.steps[-1][1]["reward"]
    shed0 = env.steps[-1][0]["observation"]["private"]["shed"].get("COW", 0)
    shed1 = env.steps[-1][1]["observation"]["private"]["shed"].get("COW", 0)
    print(f"Seed 7 Result: P0=${s0:.0f} (shed cow={shed0}) | P1=${s1:.0f} (shed cow={shed1}) | Diff=${s0-s1:.0f}")

if __name__ == "__main__":
    run_test()
