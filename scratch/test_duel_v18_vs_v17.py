import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v17_apex_colossus as s17
from scratch.test_v18_candidate import agent_v18_candidate

seeds = [42, 100, 2024, 7, 999, 1234, 555, 888, 314, 2718]
diffs_p0 = []
diffs_p1 = []

print("Running 1v1 Matches: v18 vs v17...", flush=True)
for s in seeds:
    # Match 1: v18 is P0, v17 is P1
    env1 = ke.make("kaggriculture", configuration={"seed": s})
    env1.run([agent_v18_candidate, s17.agent])
    v18_p0 = env1.steps[-1][0]["reward"]
    v17_p1 = env1.steps[-1][1]["reward"]
    diffs_p0.append(v18_p0 - v17_p1)

    # Match 2: v17 is P0, v18 is P1
    env2 = ke.make("kaggriculture", configuration={"seed": s})
    env2.run([s17.agent, agent_v18_candidate])
    v17_p0 = env2.steps[-1][0]["reward"]
    v18_p1 = env2.steps[-1][1]["reward"]
    diffs_p1.append(v18_p1 - v17_p0)

    print(f"Seed {s:5d} | P0(v18): ${v18_p0:8.0f} vs P1(v17): ${v17_p1:8.0f} (diff: {v18_p0-v17_p1:+6.0f}) | P1(v18): ${v18_p1:8.0f} vs P0(v17): ${v17_p0:8.0f} (diff: {v18_p1-v17_p0:+6.0f})", flush=True)

print(f"\nAverage Margin as P0: ${sum(diffs_p0)/len(diffs_p0):+8.1f}", flush=True)
print(f"Average Margin as P1: ${sum(diffs_p1)/len(diffs_p1):+8.1f}", flush=True)
print(f"Total Combined Margin: ${(sum(diffs_p0)+sum(diffs_p1))/(2*len(diffs_p0)):+8.1f}", flush=True)
