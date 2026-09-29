import sys
from pathlib import Path
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))

import kaggle_environments as ke
import submission_v16_apex_titan as v16
from scratch.test_v26_concept import v26_agent
from src.kaggriculture.sim.kaggle_wrapper import run_episode

seeds = [42, 100, 2024, 7, 999]
for s in seeds:
    res = run_episode('submission_v16_apex_titan.py', v26_agent, seed=s)
    diff = res['reward_player1'] - res['reward_player0']
    print(f"Seed {s} (swap): v16={res['reward_player0']:.1f} vs v26={res['reward_player1']:.1f} (v26 Diff: {diff:+.1f})")
