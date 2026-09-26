import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v19_apex_sovereign as s19

env = ke.make("kaggriculture", configuration={"seed": 42})
env.run([s19.agent, s19.agent])

obs = env.steps[600][0]["observation"]
farm = obs["farms"][obs["player"]]
animals = []
for r in farm["tiles"]:
    for t in r:
        if isinstance(t, dict) and "animal" in t:
            animals.append(t["animal"])
print("Day 25 Animals (Seed 42):", animals, "Count:", len(animals))
