import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v16_apex_titan as s16
import submission_v17_apex_colossus as s17
import submission_v18_apex_dominator as s18
import submission_v19_apex_sovereign as s19
import submission_v20_apex_liquidator as s20
import submission_v21_apex_sovereign_prime as s21

bots = {
    "v16 (1118 Elo)": s16.agent,
    "v17 (1025 Elo)": s17.agent,
    "v18": s18.agent,
    "v19 (950 Elo)": s19.agent,
    "v20": s20.agent,
    "v21": s21.agent,
}

seeds = [42, 100, 2024, 7, 999, 1234, 555, 888, 314, 2718]

# Duel v19 vs v16 (both sides: P0 vs P1 and P1 vs P0)
print("=== DUEL: v19 vs v16 (both seats, 10 seeds) ===")
v19_margins = []
for s in seeds:
    # Match 1: v19 as P0, v16 as P1
    env1 = ke.make("kaggriculture", configuration={"seed": s})
    env1.run([s19.agent, s16.agent])
    d1 = env1.steps[-1][0]["reward"] - env1.steps[-1][1]["reward"]
    
    # Match 2: v16 as P0, v19 as P1
    env2 = ke.make("kaggriculture", configuration={"seed": s})
    env2.run([s16.agent, s19.agent])
    d2 = env2.steps[-1][1]["reward"] - env2.steps[-1][0]["reward"]
    
    net = (d1 + d2) / 2
    v19_margins.append(net)
    print(f"Seed {s:5d}: v19 margin = {net:+8.1f} (P0: {d1:+8.0f}, P1: {d2:+8.0f})")

print(f"\nOverall v19 vs v16 net margin: {sum(v19_margins)/len(v19_margins):+8.1f}")
