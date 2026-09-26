import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v19_apex_sovereign as s19

env = ke.make("kaggriculture", configuration={"seed": 42})
env.run([s19.agent, s19.agent])

fertilize_turns = []
for step in range(len(env.steps)):
    act0 = env.steps[step][0].get("action", {})
    farmer = act0.get("farmer", [])
    hands = act0.get("hands", [])
    all_acts = [farmer] + list(hands)
    for a in all_acts:
        if isinstance(a, list) and len(a) > 0:
            if a[0] == "FERTILIZE" or (a[0] == "PICKUP" and len(a) > 1 and a[1] == "FERTILIZER"):
                fertilize_turns.append((step, step//24, a))
                break

print(f"Total turns with FERTILIZE or PICKUP FERTILIZER: {len(fertilize_turns)}")
for st, day, a in fertilize_turns[:20]:
    print(f"  Step {st:3d} (Day {day:2d}): {a}")
