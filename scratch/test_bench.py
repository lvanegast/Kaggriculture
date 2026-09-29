import sys
from pathlib import Path
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))

from src.kaggriculture.sim.kaggle_wrapper import run_episode

seeds = [42, 100, 2024, 7, 999]
for s in seeds:
    res = run_episode('submission_v16_apex_titan.py', 'submission_v16_apex_titan.py', seed=s)
    print(f"Seed {s}: P0={res['reward_player0']:.1f}, P1={res['reward_player1']:.1f}")
