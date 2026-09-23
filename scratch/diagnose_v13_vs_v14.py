"""
Compare v13 (472 Elo) vs v14 (391 Elo) across multiple scenarios:
1. vs Starter
2. vs v7 (431 Elo)
3. vs v11 (Apex)
4. vs each other
"""
import sys
sys.path.append(".")
import kaggle_environments as ke
from submission_v13_ranch_titan import agent as v13_agent
from submission_v14_ranch_colossus import agent as v14_agent
from submission_v7_adaptive import agent as v7_agent
from submission_v11_apex_master import agent as v11_agent

def test_matchup(name, a0, a1):
    env = ke.make("kaggriculture")
    env.reset()
    env.run([a0, a1])
    s0 = env.state[0].observation["farms"][0]["money"]
    s1 = env.state[0].observation["farms"][1]["money"]
    print(f"[{name}] P0: ${s0:.2f} | P1: ${s1:.2f} | Diff: ${s0 - s1:+.2f}")
    return s0, s1

if __name__ == "__main__":
    print("--- Testing v13 (472 Elo) ---")
    test_matchup("v13 vs Starter", v13_agent, "starter")
    test_matchup("v13 vs v7 (431 Elo)", v13_agent, v7_agent)
    test_matchup("v7 vs v13", v7_agent, v13_agent)
    test_matchup("v13 vs v11", v13_agent, v11_agent)
    test_matchup("v11 vs v13", v11_agent, v13_agent)

    print("\n--- Testing v14 (391 Elo) ---")
    test_matchup("v14 vs Starter", v14_agent, "starter")
    test_matchup("v14 vs v7 (431 Elo)", v14_agent, v7_agent)
    test_matchup("v7 vs v14", v7_agent, v14_agent)
    test_matchup("v14 vs v11", v14_agent, v11_agent)
    test_matchup("v11 vs v14", v11_agent, v14_agent)
