import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v19_apex_sovereign as s19

env = ke.make("kaggriculture", configuration={"seed": 42})
env.run([s19.agent, s19.agent])

for step in range(550, 720, 24):
    obs = env.steps[step][0]["observation"]
    prices = obs["market"]["prices"]
    shed = obs["private"]["shed"]
    print(f"Step {step} (Day {step//24}):")
    print(f"  Prices: STRAW={prices.get('STRAWBERRY')}, WOOL={prices.get('WOOL')}, MILK={prices.get('MILK')}, WHEAT={prices.get('WHEAT')}, FERT={prices.get('FERTILIZER')}")
    print(f"  Shed:   STRAW={shed.get('STRAWBERRY', 0)}, WOOL={shed.get('WOOL', 0)}, MILK={shed.get('MILK', 0)}, WHEAT={shed.get('WHEAT', 0)}, FERT={shed.get('FERTILIZER', 0)}")
