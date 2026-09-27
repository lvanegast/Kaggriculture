import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v21_apex_sovereign_prime as s21
from v43.sparse_router import build_sparse_shop_router, SparseShopRouterConfig

# Force yarn_first on all steps regardless of shops!
cfg_yarn = SparseShopRouterConfig(yarn_first_start=0)

# Build custom policy where selected_route always returns 'yarn_first' or 'yarn_second'
children = s21._V43_POLICY.children

def agent_forced_yarn_first(obs, config=None):
    step = int(s21._v43_get(obs, "step", 0) or 0)
    # Call children to keep state synced
    actions = {name: pol(obs, config) for name, pol in children.items()}
    act = actions["yarn_first"]
    act = s21._capital_guard(obs, act, step)
    act = s21._post_day24_fertilizer_liquidator(obs, act, step)
    act = s21._monetizable_terminal_units(obs, act, step)
    act = s21._perfect_terminal_sweep(obs, act, step)
    act = s21._reorder_market_demand_aware(obs, act, alpha=1.0)
    return s21._align_hands(act, obs)

def agent_forced_yarn_second(obs, config=None):
    step = int(s21._v43_get(obs, "step", 0) or 0)
    actions = {name: pol(obs, config) for name, pol in children.items()}
    act = actions["yarn_second"]
    act = s21._capital_guard(obs, act, step)
    act = s21._post_day24_fertilizer_liquidator(obs, act, step)
    act = s21._monetizable_terminal_units(obs, act, step)
    act = s21._perfect_terminal_sweep(obs, act, step)
    act = s21._reorder_market_demand_aware(obs, act, alpha=1.0)
    return s21._align_hands(act, obs)

seeds = [42, 100, 2024, 7, 999, 1234, 555, 888, 314, 2718]
scores_first = []
scores_second = []

print("=== TESTING FORCED YARN_FIRST ROUTE ===")
for s in seeds:
    env = ke.make("kaggriculture", configuration={"seed": s})
    env.run([agent_forced_yarn_first, agent_forced_yarn_first])
    s0 = env.steps[-1][0]["reward"]
    s1 = env.steps[-1][1]["reward"]
    avg = (s0 + s1) / 2
    scores_first.append(avg)
    print(f"Seed {s:5d}: Avg = ${avg:8.0f}")

print(f"\nOverall Average (Forced yarn_first): ${sum(scores_first)/len(scores_first):8.1f}")

print("\n=== TESTING FORCED YARN_SECOND ROUTE ===")
for s in seeds:
    env = ke.make("kaggriculture", configuration={"seed": s})
    env.run([agent_forced_yarn_second, agent_forced_yarn_second])
    s0 = env.steps[-1][0]["reward"]
    s1 = env.steps[-1][1]["reward"]
    avg = (s0 + s1) / 2
    scores_second.append(avg)
    print(f"Seed {s:5d}: Avg = ${avg:8.0f}")

print(f"\nOverall Average (Forced yarn_second): ${sum(scores_second)/len(scores_second):8.1f}")
