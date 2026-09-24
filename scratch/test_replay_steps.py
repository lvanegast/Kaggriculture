import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import copy

# Load submission_v16_apex_titan modules
import submission_v16_apex_titan as s16

def run_with_replay_steps(replay_steps, seeds=[7]):
    # We can patch PlannerConfig in v23.planner or build a modified policy
    modules = copy.deepcopy(s16._V43_MODULES)
    
    # In scripts.v22_weed_repair or v23.planner
    planner_code = modules['v23.planner']
    old_def = "weed_replay_steps: int = 8"
    new_def = f"weed_replay_steps: int = {replay_steps}"
    assert old_def in planner_code, "weed_replay_steps definition not found"
    modules['v23.planner'] = planner_code.replace(old_def, new_def)
    
    # Reload modules
    loaded = {}
    for name, src in modules.items():
        loaded[name] = s16._v43_load(name, src)
        
    v43_build = loaded['v43.sparse_router'].build_sparse_shop_router
    V43Config = loaded['v43.sparse_router'].SparseShopRouterConfig
    
    cfg = V43Config(**{'yarn_first_start': 88, 'yarn_second_start': 153, 'bakery_market_maker': False, 'egg_batch': 10, 'egg_cash_reserve': 2500.0, 'shed_headroom': 15})
    policy = v43_build(s16._V43_ROUTES, cfg)
    
    def test_agent(obs, configuration=None):
        step = int(obs.get("step", 0) or 0)
        action = policy(obs, configuration)
        action = s16._capital_guard(obs, action, step)
        action = s16._terminal_zero_waste_sweep(obs, action, step)
        return s16._align_hands(action, obs)

    print(f"\n--- Testing replay_steps = {replay_steps} ---")
    for s in seeds:
        env = ke.make("kaggriculture", configuration={"seed": s})
        env.run([test_agent, test_agent])
        s0 = env.steps[-1][0]["reward"]
        s1 = env.steps[-1][1]["reward"]
        shed0 = env.steps[-1][0]["observation"]["private"]["shed"].get("COW", 0)
        shed1 = env.steps[-1][1]["observation"]["private"]["shed"].get("COW", 0)
        print(f"Seed {s:5d}: P0=${s0:8.0f} (shed cow={shed0}) | P1=${s1:8.0f} (shed cow={shed1}) | Diff=${s0-s1:8.0f}")

if __name__ == "__main__":
    for r in [8, 10, 12, 14, 16, 20]:
        run_with_replay_steps(r, seeds=[7])
