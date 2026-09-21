import sys
sys.path.append(".")
import kaggle_environments as ke
import submission as v13
import submission_v12_ranch_apex as v12


env = ke.make("kaggriculture")

env.reset()
env.run([v13.agent, v12.agent])
p0 = env.state[0].observation["farms"][0]["money"]
p1 = env.state[0].observation["farms"][1]["money"]
print(f"Match 1: v13 (P0)=${p0:.2f} vs v12 (P1)=${p1:.2f} -> Diff: ${p0-p1:+.2f}")

env.reset()
env.run([v12.agent, v13.agent])
p0 = env.state[0].observation["farms"][0]["money"]
p1 = env.state[0].observation["farms"][1]["money"]
print(f"Match 2: v12 (P0)=${p0:.2f} vs v13 (P1)=${p1:.2f} -> Diff: ${p1-p0:+.2f}")
