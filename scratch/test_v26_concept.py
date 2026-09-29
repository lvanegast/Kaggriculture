import sys
from pathlib import Path
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))

import kaggle_environments as ke
import submission_v16_apex_titan as v16

def v26_agent(obs, configuration=None):
    try:
        step = int(v16._v43_get(obs, "step", 0) or 0)
        action = v16._V43_POLICY(obs, configuration)
        action = v16._weed_repair_action(obs, action, step)
        action = v16._capital_guard(obs, action, step)
        
        # Post-day 24 fertilizer liquidator (append only)
        if step >= 596:
            private = obs.get("private", {}) if isinstance(obs, dict) else getattr(obs, "private", {})
            shed = dict(private.get("shed", {}) if isinstance(private, dict) else {})
            fert_count = int(shed.get("FERTILIZER", 0) or 0)
            if fert_count > 0:
                market = list(action.get("market", []))
                for o in market:
                    if len(o) >= 3 and o[0] == "SELL" and o[1] == "FERTILIZER":
                        fert_count -= int(o[2])
                if fert_count > 0 and len(market) < 10:
                    market.append(["SELL", "FERTILIZER", min(fert_count, 3)])
                    action["market"] = market

        # Smart Terminal Sweep: cleans ghost sells of 0-inventory items, fills with real shed items
        if step >= 718:
            private = obs.get("private", {}) if isinstance(obs, dict) else getattr(obs, "private", {})
            shed = dict(private.get("shed", {}) if isinstance(private, dict) else {})
            market = list(action.get("market", []))
            
            # Keep non-sells or sells of items that actually have positive shed inventory
            valid_market = []
            for o in market:
                if len(o) >= 3 and o[0] == "SELL":
                    item = o[1]
                    if shed.get(item, 0) > 0:
                        valid_market.append(o)
                        shed[item] = max(0, shed[item] - int(o[2]))
                else:
                    valid_market.append(o)
                    
            for p in v16._PRODUCTS_ORDER:
                rem = shed.get(p, 0)
                if rem > 0 and len(valid_market) < 10:
                    valid_market.append(["SELL", p, rem])
            action["market"] = valid_market

        return v16._align_hands(action, obs)
    except Exception:
        farm = v16._farm_guard(obs, v16._seat_guard(obs))
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (v16._v43_get(farm, "hands", []) or [])],
            "market": [],
        }

from src.kaggriculture.sim.kaggle_wrapper import run_episode

seeds = [42, 100, 2024, 7, 999]
for s in seeds:
    res = run_episode(v26_agent, 'submission_v16_apex_titan.py', seed=s)
    print(f"Seed {s}: v26={res['reward_player0']:.1f} vs v16={res['reward_player1']:.1f} (Diff: {res['reward_player0'] - res['reward_player1']:+.1f})")
