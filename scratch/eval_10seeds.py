import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import importlib.util
from src.kaggriculture.sim.kaggle_wrapper import run_episode

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location("agent_mod", filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

def evaluate_selfplay(agent_path):
    seeds = [42, 100, 2024, 7, 999, 1234, 555, 888, 314, 2718]
    print(f"Evaluating {agent_path} in self-play across {len(seeds)} seeds...")
    p0_scores = []
    p1_scores = []
    
    for s in seeds:
        a0 = load_agent(agent_path)
        a1 = load_agent(agent_path)
        res = run_episode(a0, a1, seed=s)
        s0 = res["reward_player0"]
        s1 = res["reward_player1"]
        p0_scores.append(s0)
        p1_scores.append(s1)
        print(f"Seed {s:5d}: P0=${s0:8.0f} | P1=${s1:8.0f} | Diff=${s0-s1:8.0f}")
        
    avg_p0 = sum(p0_scores) / len(p0_scores)
    avg_p1 = sum(p1_scores) / len(p1_scores)
    avg_tot = (avg_p0 + avg_p1) / 2
    print(f"\nSummary for {agent_path}:")
    print(f"Avg P0: ${avg_p0:8.1f}")
    print(f"Avg P1: ${avg_p1:8.1f}")
    print(f"Overall Avg: ${avg_tot:8.1f}")

if __name__ == "__main__":
    evaluate_selfplay("submission_v16_apex_titan.py")
