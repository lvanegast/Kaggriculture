"""
Duel comparison: 3-Cow Ranch vs v12 Ranch (2-Cow).
"""
import sys
sys.path.append(".")
sys.path.append("scratch")
import kaggle_environments as ke
from test_three_cows import agent as three_cow_agent
from submission_v12_ranch_apex import agent as v12_agent

def duel():
    env = ke.make("kaggriculture")
    
    # Match 1: 3-Cow (P0) vs v12 (P1)
    env.reset()
    print("Match 1: 3-Cow (P0) vs v12 (P1)...")
    env.run([three_cow_agent, v12_agent])
    p0 = env.state[0].observation["farms"][0]["money"]
    p1 = env.state[0].observation["farms"][1]["money"]
    print(f"Match 1: 3-Cow (P0)=${p0:.2f} vs v12 (P1)=${p1:.2f} -> Diff: ${p0 - p1:+.2f}")

    # Match 2: v12 (P0) vs 3-Cow (P1)
    env.reset()
    print("\nMatch 2: v12 (P0) vs 3-Cow (P1)...")
    env.run([v12_agent, three_cow_agent])
    p0 = env.state[0].observation["farms"][0]["money"]
    p1 = env.state[0].observation["farms"][1]["money"]
    print(f"Match 2: v12 (P0)=${p0:.2f} vs 3-Cow (P1)=${p1:.2f} -> Diff: ${p1 - p0:+.2f}")

if __name__ == "__main__":
    duel()
