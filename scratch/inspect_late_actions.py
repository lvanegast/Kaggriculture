import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v19_apex_sovereign as s19

env = ke.make("kaggriculture", configuration={"seed": 42})
env.run([s19.agent, s19.agent])

plant_turns = []
harvest_turns = []
for step in range(len(env.steps)):
    act0 = env.steps[step][0].get("action", {})
    all_acts = [act0.get("farmer", [])] + list(act0.get("hands", []))
    for a in all_acts:
        if isinstance(a, list) and len(a) > 0:
            if a[0] == "PLANT":
                plant_turns.append((step, step//24, a))
            elif a[0] == "HARVEST":
                harvest_turns.append((step, step//24, a))

print(f"Total PLANT actions: {len(plant_turns)}")
print(f"Last 10 PLANT actions:")
for st, day, a in plant_turns[-10:]:
    print(f"  Step {st:3d} (Day {day:2d}): {a}")

print(f"\nTotal HARVEST actions: {len(harvest_turns)}")
print(f"Last 10 HARVEST actions:")
for st, day, a in harvest_turns[-10:]:
    print(f"  Step {st:3d} (Day {day:2d}): {a}")
