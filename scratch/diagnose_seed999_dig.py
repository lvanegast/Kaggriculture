import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v17_apex_colossus as s17
from scratch.test_true_weed_dig import agent_true_dig

env17 = ke.make("kaggriculture", configuration={"seed": 999})
env17.run([s17.agent, s17.agent])
r17 = env17.steps[-1][0]["reward"]

env_dig = ke.make("kaggriculture", configuration={"seed": 999})
env_dig.run([agent_true_dig, agent_true_dig])
r_dig = env_dig.steps[-1][0]["reward"]

print(f"Seed 999: v17=${r17} vs dig=${r_dig}")

# Check when the first divergence occurs
for step in range(len(env17.steps)):
    s17_act = env17.steps[step][0]["action"]
    sdig_act = env_dig.steps[step][0]["action"]
    obs17 = env17.steps[step][0]["observation"]
    obs_dig = env_dig.steps[step][0]["observation"]
    m17 = obs17["farms"][0]["money"]
    m_dig = obs_dig["farms"][0]["money"]
    if abs(m17 - m_dig) > 1.0 or s17_act != sdig_act:
        print(f"First divergence at step {step}:")
        print(f"  v17 action: {s17_act}")
        print(f"  dig action: {sdig_act}")
        print(f"  v17 money: {m17}, dig money: {m_dig}")
        print(f"  v17 farmer: {obs17['farms'][0]['farmer']}, dig farmer: {obs_dig['farms'][0]['farmer']}")
        print(f"  v17 shed: {obs17['private']['shed']}")
        print(f"  dig shed: {obs_dig['private']['shed']}")
        break
