"""
Duel: Variant B (3 Cows, 3 Hands, 12 Melons) vs submission_v12_ranch_apex.py
"""
import sys
sys.path.append(".")
sys.path.append("scratch")
import kaggle_environments as ke
from test_ranch_tactics import make_variant
from submission_v12_ranch_apex import agent as v12_agent

def duel():
    var_b = make_variant(max_hands=3, target_melons=12)
    env = ke.make("kaggriculture")
    
    # Match 1: Var B (P0) vs v12 (P1)
    env.reset()
    print("Match 1: Var B (P0) vs v12 (P1)...")
    env.run([var_b, v12_agent])
    p0 = env.state[0].observation["farms"][0]["money"]
    p1 = env.state[0].observation["farms"][1]["money"]
    print(f"Match 1: Var B (P0)=${p0:.2f} vs v12 (P1)=${p1:.2f} -> Diff: ${p0 - p1:+.2f}")

    # Match 2: v12 (P0) vs Var B (P1)
    env.reset()
    print("\nMatch 2: v12 (P0) vs Var B (P1)...")
    env.run([v12_agent, var_b])
    p0 = env.state[0].observation["farms"][0]["money"]
    p1 = env.state[0].observation["farms"][1]["money"]
    print(f"Match 2: v12 (P0)=${p0:.2f} vs Var B (P1)=${p1:.2f} -> Diff: ${p1 - p0:+.2f}")

if __name__ == "__main__":
    duel()
