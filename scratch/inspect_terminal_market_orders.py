import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v19_apex_sovereign as s19

env = ke.make("kaggriculture", configuration={"seed": 42})
env.run([s19.agent, s19.agent])

print("=== TERMINAL MARKET ORDERS (Steps 710-719) ===")
for step in range(710, 720):
    raw_action = s19._V43_POLICY(env.steps[step][0]["observation"], None)
    m = raw_action.get("market", [])
    print(f"Step {step}: raw market orders = {m}")
