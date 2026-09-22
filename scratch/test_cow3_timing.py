"""
Test hypothesis: 2 Cows Day 0 + 8 Melons Day 0, then Cow 3 on Day 3 vs 3 Cows Day 0.
"""
import sys
sys.path.append(".")
sys.path.append("scratch")
import kaggle_environments as ke
from submission_v13_ranch_titan import agent as v13_agent
from test_ranch_tactics import make_variant

# Let's write an agent that does 2 Cows Day 0 + 8 Melons Day 0, then buys Cow 3 on Day 3
def agent_delayed_cow3(obs, config=None):
    try:
        farms = obs.get("farms", [])
        player = obs.get("player", 0)
        private = obs.get("private", {}) or {}
        if not farms or player >= len(farms):
            return {"farmer": ["PASS"], "hands": [], "market": []}

        farm = farms[player]
        fx, fy = farm.get("farmer", (4, 4))
        hands_pos = farm.get("hands", [])
        tiles = farm.get("tiles", [])
        day = obs.get("day", 0)
        hour = obs.get("hour", 0)
        step = obs.get("step", 0)
        seeds = private.get("seeds", {})
        shed = private.get("shed", {})
        inventories = private.get("inventories", [])
        f_inv = inventories[0] if inventories else {}
        money = farm.get("money", 0)

        target_melons = 12
        target_carrots = 6
        max_hands = 3

        market_orders = []

        # 1. Market Phase: Liquidate Produce & Maintain Wheat
        for item in ["MILK", "FERTILIZER", "MELON", "STRAWBERRY", "TOMATO", "CARROT", "WHEAT"]:
            qty = shed.get(item, 0)
            if item == "WHEAT" and day < 28:
                continue
            if qty > 0:
                market_orders.append(["SELL", item, qty])

        # Day 0 Opening: NE Land + 2 Cows + 10 Wheat + 8 Melons + 6 Carrots + 1 Farmhand ($2,845)
        if day == 0 and step == 0:
            market_orders.append(["BUY_LAND"])                # $1000
            market_orders.append(["BUY_ANIMAL", "COW", 2])     # $800
            market_orders.append(["BUY_PRODUCT", "WHEAT", 10]) # $250
            market_orders.append(["BUY_SEED", "MELON", 8])     # $640
            market_orders.append(["BUY_SEED", "CARROT", 6])    # $120
            market_orders.append(["HIRE"])                     # $25
        else:
            # Buy Cow 3 on Day 3 or 4 when money >= 500
            pt3 = tiles[4][6] if 4 < len(tiles) and 6 < len(tiles[0]) else None
            cow3_ready = isinstance(pt3, dict) and "animal" in pt3
            if day in (3, 4) and not cow3_ready and shed.get("COW", 0) == 0 and money >= 450:
                market_orders.append(["BUY_ANIMAL", "COW", 1])

            # Wheat replenishment
            n_cows = 3 if cow3_ready or shed.get("COW", 0) > 0 else 2
            needed_wheat = 8 if n_cows == 3 else 6
            if day <= 27 and shed.get("WHEAT", 0) < needed_wheat and money >= 200:
                market_orders.append(["BUY_PRODUCT", "WHEAT", needed_wheat])

            # Dynamic Labor Scaling: Maintain up to 3 farmhands
            if day <= 26 and len(hands_pos) < max_hands and money >= 50:
                market_orders.append(["HIRE"])

            # Crop Seeds: Melons up to 12 (cutoff Day 14), Carrots up to 6 (cutoff Day 25)
            m_seeds = seeds.get("MELON", 0)
            c_seeds = seeds.get("CARROT", 0)
            if (day <= 2 or 12 <= day <= 14) and m_seeds < target_melons and money >= 80:
                needed_m = min(target_melons - m_seeds, int(money // 80))
                if needed_m > 0:
                    market_orders.append(["BUY_SEED", "MELON", needed_m])
            if day <= 25 and c_seeds < target_carrots and money >= 20:
                needed_c = min(target_carrots - c_seeds, int(money // 20))
                if needed_c > 0:
                    market_orders.append(["BUY_SEED", "CARROT", needed_c])

        market_orders = market_orders[:10]

        # 2. Quadrant Layout
        shed_nw = (4, 4)
        crop_slots = [
            (3, 4), (4, 3), (3, 3), (2, 4), (4, 2), (2, 3), (3, 2), (2, 2),
            (1, 4), (4, 1), (1, 3), (3, 1), (1, 2), (2, 1), (0, 4), (4, 0),
            (0, 3), (3, 0), (0, 2), (2, 0)
        ]
        melon_slots = crop_slots[:target_melons]
        carrot_slots = crop_slots[target_melons : target_melons + target_carrots]
        cluster_nw = [shed_nw] + crop_slots[:target_melons + target_carrots]

        shed_ne = (5, 4)   # Pasture 1 & NE Shed Door
        pasture_2 = (5, 3) # Pasture 2
        pasture_3 = (6, 4) # Pasture 3

        def _step_direction(current, target):
            cx, cy = current
            tx, ty = target
            if cx < tx: return "EAST"
            elif cx > tx: return "WEST"
            elif cy < ty: return "SOUTH"
            elif cy > ty: return "NORTH"
            return "PASS"

        # 3. Ranch State
        pt1 = tiles[4][5] if 4 < len(tiles) and 5 < len(tiles[0]) else None
        pt2 = tiles[3][5] if 3 < len(tiles) and 5 < len(tiles[0]) else None
        pt3 = tiles[4][6] if 4 < len(tiles) and 6 < len(tiles[0]) else None

        cow1_ready = isinstance(pt1, dict) and "animal" in pt1
        cow2_ready = isinstance(pt2, dict) and "animal" in pt2
        cow3_ready = isinstance(pt3, dict) and "animal" in pt3

        cow1_needs = cow1_ready and (
            not pt1.get("fed_today") or not pt1.get("cared_today") or pt1.get("fertilizer_available") or pt1.get("yield_units", 0) > 0
        )
        cow2_needs = cow2_ready and (
            not pt2.get("fed_today") or not pt2.get("cared_today") or pt2.get("fertilizer_available") or pt2.get("yield_units", 0) > 0
        )
        cow3_needs = cow3_ready and (
            not pt3.get("fed_today") or not pt3.get("cared_today") or pt3.get("fertilizer_available") or pt3.get("yield_units", 0) > 0
        )

        # Build pasture 3 if Cow 3 bought
        cow3_in_shed = shed.get("COW", 0) > 0 or f_inv.get("COW", 0) > 0
        ranch_active = (cow1_needs or cow2_needs or cow3_needs or (day == 0 and (not cow1_ready or not cow2_ready)) or cow3_in_shed)

        claimed_targets = set()

        def resolve_farmer_action():
            # Day 0 Deterministic 2-Cow Setup Sequence
            if day == 0:
                if step == 0: return ["EAST"]           # to (5,4)
                if step == 1: return ["BUILD_PASTURE"]  # at (5,4)
                if step == 2: return ["NORTH"]          # to (5,3)
                if step == 3: return ["BUILD_PASTURE"]  # at (5,3)
                if step == 4: return ["SOUTH"]          # to (5,4)
                if step == 5: return ["PICKUP", "COW", 2]
                if step == 6: return ["PLACE", "COW"]   # Cow 1 at (5,4)
                if step == 7: return ["NORTH"]          # to (5,3)
                if step == 8: return ["PLACE", "COW"]   # Cow 2 at (5,3)
                if step == 9: return ["SOUTH"]          # to (5,4)
                if step == 10: return ["PICKUP", "WHEAT", 2]
                if step == 11: return ["FEED"]          # feed Cow 1
                if step == 12: return ["CARE"]          # care Cow 1
                if step == 13: return ["NORTH"]         # to (5,3)
                if step == 14: return ["FEED"]          # feed Cow 2
                if step == 15: return ["CARE"]          # care Cow 2
                if step == 16: return ["SOUTH"]         # to (5,4)
                if step == 17: return ["WEST"]          # to (4,4)
                return resolve_crop_worker_action(fx, fy, f_inv)

            # Placement of Cow 3 when bought on Day 3/4
            if cow3_in_shed:
                if (fx, fy) == (4, 4):
                    return ["EAST"] # to (5,4)
                if (fx, fy) == (5, 4):
                    if shed.get("COW", 0) > 0 and f_inv.get("COW", 0) == 0:
                        return ["PICKUP", "COW", 1]
                    return ["EAST"] # to (6,4)
                if (fx, fy) == (6, 4):
                    if pt3 is None:
                        return ["BUILD_PASTURE"]
                    if f_inv.get("COW", 0) > 0:
                        return ["PLACE", "COW"]
                    return ["WEST"]

            # Days 1+: Morning Ranch Routine
            if ranch_active:
                has_produce = (f_inv.get("FERTILIZER", 0) > 0 or f_inv.get("MILK", 0) > 0)
                if (fx, fy) == (4, 4):
                    return ["EAST"] # to (5,4)
                if (fx, fy) == (5, 4):
                    if pt1 and isinstance(pt1, dict) and pt1.get("fertilizer_available"):
                        return ["COLLECT_FERTILIZER"]
                    if pt1 and isinstance(pt1, dict) and pt1.get("yield_units", 0) > 0:
                        return ["HARVEST"]
                    if pt1 and isinstance(pt1, dict) and not pt1.get("fed_today"):
                        if f_inv.get("WHEAT", 0) > 0:
                            return ["FEED"]
                        elif shed.get("WHEAT", 0) > 0:
                            needed_w = (1 if not pt1.get("fed_today") else 0) + (1 if cow2_needs else 0) + (1 if cow3_needs else 0)
                            return ["PICKUP", "WHEAT", max(1, needed_w)]
                    if pt1 and isinstance(pt1, dict) and not pt1.get("cared_today"):
                        return ["CARE"]
                    if cow2_needs:
                        return ["NORTH"] # tend Cow 2 at (5,3)
                    if cow3_needs:
                        return ["EAST"]  # tend Cow 3 at (6,4)
                    if has_produce:
                        return ["DROP"]  # drop into shed at (5,4)
                    return ["WEST"]      # return to NW (4,4)
                if (fx, fy) == (5, 3):
                    if pt2 and isinstance(pt2, dict) and pt2.get("fertilizer_available"):
                        return ["COLLECT_FERTILIZER"]
                    if pt2 and isinstance(pt2, dict) and pt2.get("yield_units", 0) > 0:
                        return ["HARVEST"]
                    if pt2 and isinstance(pt2, dict) and not pt2.get("fed_today"):
                        if f_inv.get("WHEAT", 0) > 0:
                            return ["FEED"]
                        else:
                            return ["SOUTH"] # return to get wheat
                    if pt2 and isinstance(pt2, dict) and not pt2.get("cared_today"):
                        return ["CARE"]
                    return ["SOUTH"] # return to (5,4)
                if (fx, fy) == (6, 4):
                    if pt3 and isinstance(pt3, dict) and pt3.get("fertilizer_available"):
                        return ["COLLECT_FERTILIZER"]
                    if pt3 and isinstance(pt3, dict) and pt3.get("yield_units", 0) > 0:
                        return ["HARVEST"]
                    if pt3 and isinstance(pt3, dict) and not pt3.get("fed_today"):
                        if f_inv.get("WHEAT", 0) > 0:
                            return ["FEED"]
                        else:
                            return ["WEST"] # return to get wheat
                    if pt3 and isinstance(pt3, dict) and not pt3.get("cared_today"):
                        return ["CARE"]
                    return ["WEST"] # return to (5,4)

            return resolve_crop_worker_action(fx, fy, f_inv)

        def resolve_crop_worker_action(wx, wy, worker_inv):
            has_items = any(qty > 0 for qty in worker_inv.values())

            if (wx, wy) == shed_nw and has_items:
                return ["DROP"]

            if wy < len(tiles) and wx < len(tiles[0]):
                ct = tiles[wy][wx]
                if isinstance(ct, dict):
                    k = ct.get("kind")
                    if k == "PLANT":
                        crop = ct.get("crop")
                        age = day - ct.get("planted_day", 0)
                        y_units = ct.get("yield_units", 0)
                        mature = (age >= 12 and y_units > 0) if crop == "MELON" else (age >= 3 and y_units > 0)
                        if mature:
                            claimed_targets.add((wx, wy))
                            return ["HARVEST"]
                        elif not ct.get("watered_today", False) and day <= 28:
                            claimed_targets.add((wx, wy))
                            return ["WATER"]
                    elif k == "WEED":
                        claimed_targets.add((wx, wy))
                        return ["DIG"]
                elif ct is None and (wx, wy) in cluster_nw:
                    m_s = seeds.get("MELON", 0)
                    c_s = seeds.get("CARROT", 0)
                    if (wx, wy) in melon_slots and m_s > 0 and (day <= 2 or 12 <= day <= 14):
                        claimed_targets.add((wx, wy))
                        return ["PLANT", "MELON"]
                    elif (wx, wy) in carrot_slots and c_s > 0 and day <= 25:
                        claimed_targets.add((wx, wy))
                        return ["PLANT", "CARROT"]

            needed = []
            m_s = seeds.get("MELON", 0)
            c_s = seeds.get("CARROT", 0)
            for cx, cy in cluster_nw:
                if (cx, cy) in claimed_targets: continue
                if cy >= len(tiles) or cx >= len(tiles[0]): continue
                t = tiles[cy][cx]
                if isinstance(t, dict):
                    k = t.get("kind")
                    if k == "PLANT":
                        crop = t.get("crop")
                        age = day - t.get("planted_day", 0)
                        y_units = t.get("yield_units", 0)
                        mature = (age >= 12 and y_units > 0) if crop == "MELON" else (age >= 3 and y_units > 0)
                        if mature: needed.append(((cx, cy), 1))
                        elif not t.get("watered_today", False) and day <= 28: needed.append(((cx, cy), 2))
                    elif k == "WEED": needed.append(((cx, cy), 3))
                elif t is None and day <= 25:
                    if (cx, cy) in melon_slots and m_s > 0 and (day <= 2 or 12 <= day <= 14): needed.append(((cx, cy), 4))
                    elif (cx, cy) in carrot_slots and c_s > 0: needed.append(((cx, cy), 4))

            if day >= 29 and has_items:
                return [_step_direction((wx, wy), shed_nw)]

            if needed:
                needed.sort(key=lambda item: (item[1], abs(wx - item[0][0]) + abs(wy - item[0][1])))
                tx, ty = needed[0][0]
                claimed_targets.add((tx, ty))
                return [_step_direction((wx, wy), (tx, ty))]
            elif has_items:
                return [_step_direction((wx, wy), shed_nw)]

            return ["PASS"]

        farmer_act = resolve_farmer_action()
        hands_act = []
        for h_idx, (hx, hy) in enumerate(hands_pos):
            h_inv = inventories[h_idx + 1] if len(inventories) > h_idx + 1 else {}
            h_act = resolve_crop_worker_action(hx, hy, h_inv)
            hands_act.append(h_act)

        return {"farmer": farmer_act, "hands": hands_act, "market": market_orders}

    except Exception:
        return {"farmer": ["PASS"], "hands": [], "market": []}

def compare():
    env = ke.make("kaggriculture")
    
    # Delayed Cow 3 vs Starter
    env.reset()
    env.run([agent_delayed_cow3, "starter"])
    p0 = env.state[0].observation["farms"][0]["money"]
    print(f"Delayed Cow 3 (8 Melons Day 0) vs Starter: ${p0:.2f}")

    # Head to Head: Delayed Cow 3 vs v13 Titan
    env.reset()
    env.run([agent_delayed_cow3, v13_agent])
    p0 = env.state[0].observation["farms"][0]["money"]
    p1 = env.state[0].observation["farms"][1]["money"]
    print(f"Delayed Cow 3 (P0)=${p0:.2f} vs v13 Titan (P1)=${p1:.2f} -> Diff: ${p0-p1:+.2f}")

    env.reset()
    env.run([v13_agent, agent_delayed_cow3])
    p0 = env.state[0].observation["farms"][0]["money"]
    p1 = env.state[0].observation["farms"][1]["money"]
    print(f"v13 Titan (P0)=${p0:.2f} vs Delayed Cow 3 (P1)=${p1:.2f} -> Diff: ${p1-p0:+.2f}")

if __name__ == "__main__":
    compare()
