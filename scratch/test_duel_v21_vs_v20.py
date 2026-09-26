import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v19_apex_sovereign as s19
from scratch.test_fert_liquidate import agent_v20
from scratch.test_v20_v21_synthesis import agent_v20 as agent_v21_perfect

seeds = [42, 100, 2024, 7, 999, 1234, 555, 888, 314, 2718]
diffs = []
print("Evaluating 1v1 DUEL: agent_v21 (P0) vs agent_v20 (P1) across 10 seeds...", flush=True)
for s in seeds:
    env = ke.make("kaggriculture", configuration={"seed": s})
    env.run([agent_v21_perfect, agent_v20])
    s0 = env.steps[-1][0]["reward"]
    s1 = env.steps[-1][1]["reward"]
    d = s0 - s1
    diffs.append(d)
    print(f"Seed {s:5d}: v21=${s0:8.0f} | v20=${s1:8.0f} | Diff=${d:+8.0f}", flush=True)

print(f"\nAverage Margin v21 vs v20: ${sum(diffs)/len(diffs):+8.1f}", flush=True)
