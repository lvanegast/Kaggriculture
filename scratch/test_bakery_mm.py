import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v16_apex_titan as s16
from v43.sparse_router import build_sparse_shop_router, SparseShopRouterConfig

cfg_mm = SparseShopRouterConfig(
    yarn_first_start=88,
    yarn_second_start=153,
    bakery_market_maker=True,
    egg_batch=10,
    egg_cash_reserve=2500.0,
    shed_headroom=15
)
policy_mm = build_sparse_shop_router(s16._V43_ROUTES, cfg_mm)

def agent_mm(obs, config=None):
    step = int(obs.get('step', 0) or 0)
    act = policy_mm(obs, config)
    act = s16._capital_guard(obs, act, step)
    act = s16._terminal_zero_waste_sweep(obs, act, step)
    return s16._align_hands(act, obs)

seeds = [42, 100, 2024, 7, 999, 1234, 555, 888, 314, 2718]
scores_mm = []
print("Evaluating bakery_market_maker=True across 10 seeds...")
for s in seeds:
    env = ke.make("kaggriculture", configuration={"seed": s})
    env.run([agent_mm, agent_mm])
    s0 = env.steps[-1][0]["reward"]
    s1 = env.steps[-1][1]["reward"]
    scores_mm.append((s0 + s1) / 2)
    print(f"Seed {s:5d}: P0=${s0:8.0f} | P1=${s1:8.0f}")

print(f"\nAverage with bakery_market_maker=True: ${sum(scores_mm)/len(scores_mm):8.1f}")
