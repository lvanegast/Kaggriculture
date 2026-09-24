import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
from scratch.eval_10seeds import load_agent

def diagnose(seed=7):
    env = ke.make("kaggriculture", configuration={"seed": seed})
    a0 = load_agent("submission_v16_apex_titan.py")
    a1 = load_agent("submission_v16_apex_titan.py")
    env.run([a0, a1])

    print(f"=== SEED {seed} REPORT ===")
    for p in (0, 1):
        obs = env.steps[-1][p]["observation"]
        farm = obs["farms"][p]
        priv = obs["private"]
        print(f"Player {p}: Money=${farm['money']:.0f}, Hands={len(farm.get('hands', []))}")
        print(f"Player {p} Shed: {priv.get('shed', {})}")
        tiles = farm.get("tiles", [])
        animals = sum(1 for row in tiles for t in row if isinstance(t, dict) and "animal" in t)
        pastures = sum(1 for row in tiles for t in row if isinstance(t, dict) and t.get("kind") == "PASTURE")
        weeds = sum(1 for row in tiles for t in row if isinstance(t, dict) and t.get("weed"))
        print(f"Player {p}: Placed Animals={animals}, Pastures={pastures}, Weeds={weeds}")

if __name__ == "__main__":
    diagnose(7)
    diagnose(555)
