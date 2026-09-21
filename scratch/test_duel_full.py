"""
Duel comparison: FarmBrain v12 Ranch Apex vs FarmBrain v11 Apex Master.
"""
import kaggle_environments as ke
import sys
sys.path.append(".")
sys.path.append("scratch")
from test_ranch_hybrid import agent as ranch_agent
from submission_v11_apex_master import agent as v11_agent


def duel():
    env = ke.make("kaggriculture")
    
    # Match 1: Ranch (P0) vs v11 (P1)
    env.reset()
    print("Match 1: Ranch (P0) vs v11 (P1)...")
    env.run([ranch_agent, v11_agent])
    p0_score = env.state[0].observation["farms"][0]["money"]
    p1_score = env.state[0].observation["farms"][1]["money"]
    print(f"Outcome: Ranch (P0)=${p0_score:.2f} vs v11 (P1)=${p1_score:.2f} -> Diff: ${p0_score - p1_score:+.2f}")

    # Match 2: v11 (P0) vs Ranch (P1)
    env.reset()
    print("\nMatch 2: v11 (P0) vs Ranch (P1)...")
    env.run([v11_agent, ranch_agent])
    p0_score = env.state[0].observation["farms"][0]["money"]
    p1_score = env.state[0].observation["farms"][1]["money"]
    print(f"Outcome: v11 (P0)=${p0_score:.2f} vs Ranch (P1)=${p1_score:.2f} -> Diff: ${p1_score - p0_score:+.2f}")

if __name__ == "__main__":
    duel()
