"""
Test refinements on v13 (472 Elo):
- Ensure 0 missed water on Days 0-2
- Adapt crop mix if opponent rushes melons
- Measure consistency across 10 different random seeds
"""
import sys
sys.path.append(".")
import kaggle_environments as ke
from submission_v13_ranch_titan import agent as v13_agent

def evaluate_seeds(agent_fn, n_seeds=5):
    scores = []
    for seed in range(n_seeds):
        env = ke.make("kaggriculture", configuration={"seed": seed * 42})
        env.reset()
        env.run([agent_fn, "starter"])
        s0 = env.state[0].observation["farms"][0]["money"]
        scores.append(s0)
    avg = sum(scores) / len(scores)
    print(f"Scores over {n_seeds} seeds: {scores} -> Avg: ${avg:.2f}")
    return avg

if __name__ == "__main__":
    print("Evaluating v13 consistency across seeds:")
    evaluate_seeds(v13_agent, 5)
