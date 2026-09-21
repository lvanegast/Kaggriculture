import kaggle_environments as ke
import sys
sys.path.append("scratch")
from test_ranch_hybrid import agent

env = ke.make("kaggriculture")
env.reset()
for step in range(24):
    obs = env.state[0].observation
    act = agent(obs)
    farm = obs["farms"][0]
    priv = obs["private"]
    fx, fy = farm["farmer"]
    inv = priv["inventories"][0]
    shed = priv["shed"]
    print(f"Step {step:2d}: pos=({fx},{fy}), act={act['farmer']}, inv={inv}, shed_cows={shed.get('COW', 0)}")
    env.step([act, {"farmer": ["PASS"], "hands": [], "market": []}])
