import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v19_apex_sovereign as s19
from scratch.test_v20_v21_synthesis import _post_day24_fertilizer_liquidator, _perfect_terminal_sweep

seeds = [42, 100, 2024, 7, 999, 1234, 555, 888, 314, 2718]

for alpha in [0.0, 0.5, 1.0, 1.5, 2.0]:
    def make_agent(a):
        def _agent(obs, config=None):
            step = int(s19._v43_get(obs, "step", 0) or 0)
            act = s19._V43_POLICY(obs, config)
            act = s19._capital_guard(obs, act, step)
            act = _post_day24_fertilizer_liquidator(obs, act, step)
            act = s19._monetizable_terminal_units(obs, act, step)
            act = _perfect_terminal_sweep(obs, act, step)
            act = s19._reorder_market_demand_aware(obs, act, alpha=a)
            return s19._align_hands(act, obs)
        return _agent

    agent_a = make_agent(alpha)
    scores = []
    for s in seeds:
        env = ke.make("kaggriculture", configuration={"seed": s})
        env.run([agent_a, agent_a])
        scores.append((env.steps[-1][0]["reward"] + env.steps[-1][1]["reward"]) / 2)
    avg_score = sum(scores) / len(scores)
    print(f"Alpha {alpha:3.1f}: Avg = ${avg_score:8.1f}")
