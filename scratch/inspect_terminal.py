import sys
from pathlib import Path
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))

import kaggle_environments as ke
import submission_v16_apex_titan as v16

env = ke.make("kaggriculture", configuration={"seed": 42})
env.reset()

# Run up to step 717
while env.steps[-1][0]["observation"]["step"] < 718:
    obs0 = env.steps[-1][0]["observation"]
    obs1 = env.steps[-1][1]["observation"]
    a0 = v16.agent(obs0)
    a1 = v16.agent(obs1)
    env.step([a0, a1])

obs0 = env.steps[-1][0]["observation"]
print("Step 718 obs0 private shed:", obs0["private"]["shed"])
a0_base = v16._V43_POLICY(obs0)
print("Step 718 base v43 market orders:", a0_base.get("market"))
a0_v16 = v16.agent(obs0)
print("Step 718 v16 agent market orders:", a0_v16.get("market"))

# Step 719
env.step([a0_v16, v16.agent(env.steps[-1][1]["observation"])])
obs0_719 = env.steps[-1][0]["observation"]
print("Step 719 obs0 private shed:", obs0_719["private"]["shed"])
a0_719_base = v16._V43_POLICY(obs0_719)
print("Step 719 base v43 market orders:", a0_719_base.get("market"))
a0_719_v16 = v16.agent(obs0_719)
print("Step 719 v16 agent market orders:", a0_719_v16.get("market"))
