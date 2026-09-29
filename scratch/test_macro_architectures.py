"""Macro Architecture Exploration for Kaggriculture.
Testing different economic engines against the starter baseline and v16.
"""
import sys
import os
import kaggle_environments as ke

def test_engine_run(agent_fn, name="test_agent", seed=42):
    env = ke.make("kaggriculture", configuration={"seed": seed})
    # Run against naive baseline
    env.run([agent_fn, "starter"])
    p0_reward = env.steps[-1][0].get("reward", 0) or 0
    p1_reward = env.steps[-1][1].get("reward", 0) or 0
    print(f"[{name}] Seed {seed}: P0 (Agent) = ${p0_reward:,.2f} | P1 (Starter) = ${p1_reward:,.2f}")
    return p0_reward

if __name__ == "__main__":
    print("Testing framework initialized.")
