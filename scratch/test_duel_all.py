import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
from scratch.eval_10seeds import load_agent

opponents = [
    ("v15", "submission_v15_premium_titan.py"),
    ("v14", "submission_v14_ranch_colossus.py"),
    ("v12", "submission_v12_ranch_apex.py"),
    ("v10", "submission_v10_apex.py"),
]

seeds = [42, 100, 2024, 7, 999]

for name, opp_path in opponents:
    print(f"\n==========================================")
    print(f"Match: v16 (Apex Titan) vs {name} ({opp_path})")
    print(f"==========================================")
    v16_wins = 0
    opp_wins = 0
    v16_scores = []
    opp_scores = []
    
    for s in seeds:
        # Game 1: v16 as P0
        a_v16 = load_agent("submission_v16_apex_titan.py")
        a_opp = load_agent(opp_path)
        env = ke.make("kaggriculture", configuration={"seed": s})
        env.run([a_v16, a_opp])
        r0 = env.steps[-1][0]["reward"]
        r1 = env.steps[-1][1]["reward"]
        v16_scores.append(r0)
        opp_scores.append(r1)
        if r0 > r1: v16_wins += 1
        elif r1 > r0: opp_wins += 1
        print(f"Seed {s:5d} (v16 as P0): v16=${r0:8.0f} | {name}=${r1:8.0f} -> {'v16 WIN' if r0>r1 else 'LOSS'}")

        # Game 2: v16 as P1 (swap sides)
        a_v16 = load_agent("submission_v16_apex_titan.py")
        a_opp = load_agent(opp_path)
        env = ke.make("kaggriculture", configuration={"seed": s})
        env.run([a_opp, a_v16])
        r0 = env.steps[-1][0]["reward"]
        r1 = env.steps[-1][1]["reward"]
        v16_scores.append(r1)
        opp_scores.append(r0)
        if r1 > r0: v16_wins += 1
        elif r0 > r1: opp_wins += 1
        print(f"Seed {s:5d} (v16 as P1): v16=${r1:8.0f} | {name}=${r0:8.0f} -> {'v16 WIN' if r1>r0 else 'LOSS'}")

    total_games = len(v16_scores)
    avg_v16 = sum(v16_scores) / total_games
    avg_opp = sum(opp_scores) / total_games
    print(f"SUMMARY vs {name}: v16 Wins={v16_wins}/{total_games} ({v16_wins/total_games*100:.1f}%), Avg v16=${avg_v16:8.1f} vs Avg {name}=${avg_opp:8.1f} (Margin: +${avg_v16 - avg_opp:8.1f})")
