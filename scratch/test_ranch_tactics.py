"""
Testing optimizations on 3-Cow Ranch:
1. Labor: 3 Farmhands (4 workers total) once cash >= $300
2. Fertilizer usage: Use fertilizer on ripening melons vs selling for $100
3. Crop cluster scaling: 10 Melons + 6 Carrots
"""
import sys
sys.path.append(".")
import kaggle_environments as ke
import copy
from test_three_cows import agent as base_3cow

def run_experiment(name, agent_fn):
    env = ke.make("kaggriculture")
    env.reset()
    env.run([agent_fn, "starter"])
    p0 = env.state[0].observation["farms"][0]["money"]
    p1 = env.state[0].observation["farms"][1]["money"]
    print(f"[{name}] Score: ${p0:.2f} vs Starter: ${p1:.2f}")
    return p0

def _step_direction(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    if x1 < x2: return "EAST"
    if x1 > x2: return "WEST"
    if y1 < y2: return "SOUTH"
    if y1 > y2: return "NORTH"
    return "PASS"


def make_variant(max_hands=3, target_melons=10):
    def agent_variant(obs, config=None):
        # We can adapt test_three_cows logic with parameterized max_hands
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

            market_orders = []

            for item in ["MILK", "FERTILIZER", "MELON", "STRAWBERRY", "TOMATO", "CARROT", "WHEAT"]:
                qty = shed.get(item, 0)
                if item == "WHEAT" and day < 28:
                    continue
                if qty > 0:
                    market_orders.append(["SELL", item, qty])

            if day == 0 and step == 0:
                market_orders.append(["BUY_LAND"])
                market_orders.append(["BUY_ANIMAL", "COW", 3])
                market_orders.append(["BUY_PRODUCT", "WHEAT", 15])
                market_orders.append(["BUY_SEED", "MELON", 4])
                market_orders.append(["BUY_SEED", "CARROT", 4])
                market_orders.append(["HIRE"])
            else:
                if day <= 27 and shed.get("WHEAT", 0) < 8 and money >= 200:
                    market_orders.append(["BUY_PRODUCT", "WHEAT", 8])

                # Dynamic hiring: up to max_hands
                if day <= 26 and len(hands_pos) < max_hands and money >= 50:
                    market_orders.append(["HIRE"])

                m_seeds = seeds.get("MELON", 0)
                c_seeds = seeds.get("CARROT", 0)
                if (day <= 2 or 12 <= day <= 14) and m_seeds < target_melons and money >= 80:
                    needed_m = min(target_melons - m_seeds, int(money // 80))
                    if needed_m > 0:
                        market_orders.append(["BUY_SEED", "MELON", needed_m])
                if day <= 25 and c_seeds < 6 and money >= 20:
                    needed_c = min(6 - c_seeds, int(money // 20))
                    if needed_c > 0:
                        market_orders.append(["BUY_SEED", "CARROT", needed_c])

            market_orders = market_orders[:10]

            shed_nw = (4, 4)
            crop_slots = [
                (3, 4), (4, 3), (3, 3), (2, 4), (4, 2), (2, 3), (3, 2), (2, 2),
                (1, 4), (4, 1), (1, 3), (3, 1), (1, 2), (2, 1), (0, 4), (4, 0),
                (0, 3), (3, 0), (0, 2), (2, 0)
            ]
            melon_slots = crop_slots[:target_melons]
            carrot_slots = crop_slots[target_melons : target_melons + 6]
            cluster_nw = [shed_nw] + crop_slots[:target_melons + 6]

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

            ranch_active = (cow1_needs or cow2_needs or cow3_needs or (day == 0 and (not cow1_ready or not cow2_ready or not cow3_ready)))

            claimed_targets = set()

            def resolve_farmer_action():
                if day == 0:
                    if step == 0: return ["EAST"]
                    if step == 1: return ["BUILD_PASTURE"]
                    if step == 2: return ["NORTH"]
                    if step == 3: return ["BUILD_PASTURE"]
                    if step == 4: return ["SOUTH"]
                    if step == 5: return ["EAST"]
                    if step == 6: return ["BUILD_PASTURE"]
                    if step == 7: return ["WEST"]
                    if step == 8: return ["PICKUP", "COW", 3]
                    if step == 9: return ["PLACE", "COW"]
                    if step == 10: return ["NORTH"]
                    if step == 11: return ["PLACE", "COW"]
                    if step == 12: return ["SOUTH"]
                    if step == 13: return ["EAST"]
                    if step == 14: return ["PLACE", "COW"]
                    if step == 15: return ["WEST"]
                    if step == 16: return ["PICKUP", "WHEAT", 3]
                    if step == 17: return ["FEED"]
                    if step == 18: return ["CARE"]
                    if step == 19: return ["NORTH"]
                    if step == 20: return ["FEED"]
                    if step == 21: return ["CARE"]
                    if step == 22: return ["SOUTH"]
                    if step == 23: return ["EAST"]
                    return ["PASS"]

                if day == 1 and (fx, fy) == (6, 4) and not pt3.get("fed_today", False):
                    if f_inv.get("WHEAT", 0) > 0: return ["FEED"]

                if ranch_active:
                    has_produce = (f_inv.get("FERTILIZER", 0) > 0 or f_inv.get("MILK", 0) > 0)
                    if (fx, fy) == (4, 4):
                        return ["EAST"]
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
                            return ["NORTH"]
                        if cow3_needs:
                            return ["EAST"]
                        if has_produce:
                            return ["DROP"]
                        return ["WEST"]
                    if (fx, fy) == (5, 3):
                        if pt2 and isinstance(pt2, dict) and pt2.get("fertilizer_available"):
                            return ["COLLECT_FERTILIZER"]
                        if pt2 and isinstance(pt2, dict) and pt2.get("yield_units", 0) > 0:
                            return ["HARVEST"]
                        if pt2 and isinstance(pt2, dict) and not pt2.get("fed_today"):
                            if f_inv.get("WHEAT", 0) > 0:
                                return ["FEED"]
                            else:
                                return ["SOUTH"]
                        if pt2 and isinstance(pt2, dict) and not pt2.get("cared_today"):
                            return ["CARE"]
                        return ["SOUTH"]
                    if (fx, fy) == (6, 4):
                        if pt3 and isinstance(pt3, dict) and pt3.get("fertilizer_available"):
                            return ["COLLECT_FERTILIZER"]
                        if pt3 and isinstance(pt3, dict) and pt3.get("yield_units", 0) > 0:
                            return ["HARVEST"]
                        if pt3 and isinstance(pt3, dict) and not pt3.get("fed_today"):
                            if f_inv.get("WHEAT", 0) > 0:
                                return ["FEED"]
                            else:
                                return ["WEST"]
                        if pt3 and isinstance(pt3, dict) and not pt3.get("cared_today"):
                            return ["CARE"]
                        return ["WEST"]

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

    return agent_variant

if __name__ == "__main__":
    run_experiment("Base 3-Cow (2 hands, 8 melons)", base_3cow)
    run_experiment("Variant A (3 hands, 8 melons)", make_variant(max_hands=3, target_melons=8))
    run_experiment("Variant B (3 hands, 12 melons)", make_variant(max_hands=3, target_melons=12))
    run_experiment("Variant C (2 hands, 12 melons)", make_variant(max_hands=2, target_melons=12))
