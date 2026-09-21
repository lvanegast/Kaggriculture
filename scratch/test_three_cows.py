"""
Prototype for 3 Cows in NE:
- Pasture 1 at (5, 4) [Shed Door]
- Pasture 2 at (5, 3) [North of door]
- Pasture 3 at (6, 4) [East of door]
"""
import sys
sys.path.append(".")
import kaggle_environments as ke

def agent(obs, config=None):
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

        # 1. Market Phase: Liquidate Produce & Maintain Wheat
        for item in ["MILK", "FERTILIZER", "MELON", "STRAWBERRY", "TOMATO", "CARROT", "WHEAT"]:
            qty = shed.get(item, 0)
            if item == "WHEAT" and day < 28:
                continue # preserve wheat for cows until season end
            if qty > 0:
                market_orders.append(["SELL", item, qty])

        # Day 0 Opening Purchases: NE Land + 3 Cows + Feed + Crop Seeds + Farmhand
        if day == 0 and step == 0:
            market_orders.append(["BUY_LAND"])                # Unlock NE ($1000)
            market_orders.append(["BUY_ANIMAL", "COW", 3])     # 3 Cows ($1200)
            market_orders.append(["BUY_PRODUCT", "WHEAT", 15]) # Initial Feed ($375)
            market_orders.append(["BUY_SEED", "MELON", 4])     # 4 Melons ($320)
            market_orders.append(["BUY_SEED", "CARROT", 4])    # 4 Carrots ($80)
            market_orders.append(["HIRE"])                     # 1 Farmhand ($25)
        else:
            # Wheat replenishment for 3 cows (days 1-27)
            if day <= 27 and shed.get("WHEAT", 0) < 8 and money >= 200:
                market_orders.append(["BUY_PRODUCT", "WHEAT", 8])

            # Maintain 2 farmhands (3 total workers)
            if day <= 26 and len(hands_pos) < 2 and money >= 25:
                market_orders.append(["HIRE"])

            # Regular Crop Seeds: Melons until Day 14, Carrots until Day 25
            m_seeds = seeds.get("MELON", 0)
            c_seeds = seeds.get("CARROT", 0)
            if (day <= 2 or 12 <= day <= 14) and m_seeds < 8 and money >= 80:
                needed_m = min(8 - m_seeds, int(money // 80))
                if needed_m > 0:
                    market_orders.append(["BUY_SEED", "MELON", needed_m])
            if day <= 25 and c_seeds < 6 and money >= 20:
                needed_c = min(6 - c_seeds, int(money // 20))
                if needed_c > 0:
                    market_orders.append(["BUY_SEED", "CARROT", needed_c])

        market_orders = market_orders[:10]

        # 2. Quadrant Layout
        # NW Crop cluster around (4,4)
        shed_nw = (4, 4)
        crop_slots = [
            (3, 4), (4, 3), (3, 3), (2, 4), (4, 2), (2, 3), (3, 2), (2, 2),
            (1, 4), (4, 1), (1, 3), (3, 1), (1, 2), (2, 1), (0, 4), (4, 0)
        ]
        melon_slots = crop_slots[:8]
        carrot_slots = crop_slots[8:16]
        cluster_nw = [shed_nw] + crop_slots

        # NE Ranch cluster
        shed_ne = (5, 4)   # Pasture 1 & NE Shed Door
        pasture_2 = (5, 3) # Pasture 2 (North of door)
        pasture_3 = (6, 4) # Pasture 3 (East of door)

        def _step_direction(current, target):
            cx, cy = current
            tx, ty = target
            if cx < tx: return "EAST"
            elif cx > tx: return "WEST"
            elif cy < ty: return "SOUTH"
            elif cy > ty: return "NORTH"
            return "PASS"

        # 3. Ranch State Inspection
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

        # 4. Farmer Action (3-Cow Rancher in morning, crop helper in afternoon)
        def resolve_farmer_action():
            # Day 0 Deterministic 3-Cow Setup Sequence
            if day == 0:
                if step == 0: return ["EAST"]           # to (5,4)
                if step == 1: return ["BUILD_PASTURE"]  # at (5,4)
                if step == 2: return ["NORTH"]          # to (5,3)
                if step == 3: return ["BUILD_PASTURE"]  # at (5,3)
                if step == 4: return ["SOUTH"]          # to (5,4)
                if step == 5: return ["EAST"]           # to (6,4)
                if step == 6: return ["BUILD_PASTURE"]  # at (6,4)
                if step == 7: return ["WEST"]           # to (5,4)
                if step == 8: return ["PICKUP", "COW", 3]
                if step == 9: return ["PLACE", "COW"]   # Cow 1 at (5,4)
                if step == 10: return ["NORTH"]         # to (5,3)
                if step == 11: return ["PLACE", "COW"]  # Cow 2 at (5,3)
                if step == 12: return ["SOUTH"]         # to (5,4)
                if step == 13: return ["EAST"]          # to (6,4)
                if step == 14: return ["PLACE", "COW"]  # Cow 3 at (6,4)
                if step == 15: return ["WEST"]          # to (5,4)
                if step == 16: return ["PICKUP", "WHEAT", 3]
                if step == 17: return ["FEED"]          # feed Cow 1
                if step == 18: return ["CARE"]          # care Cow 1
                if step == 19: return ["NORTH"]         # to (5,3)
                if step == 20: return ["FEED"]          # feed Cow 2
                if step == 21: return ["CARE"]          # care Cow 2
                if step == 22: return ["SOUTH"]         # to (5,4)
                if step == 23: return ["EAST"]          # to (6,4)
                return ["PASS"]

            # Day 1 step 0 finish Cow 3 feeding if needed
            if day == 1 and (fx, fy) == (6, 4) and not pt3.get("fed_today", False):
                if f_inv.get("WHEAT", 0) > 0: return ["FEED"]

            # Days 1+: Morning Ranch Routine for 3 Cows
            if ranch_active:
                has_produce = (f_inv.get("FERTILIZER", 0) > 0 or f_inv.get("MILK", 0) > 0)
                if (fx, fy) == (4, 4):
                    return ["EAST"] # go to (5,4)
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
                        return ["NORTH"] # tend cow 2 at (5,3)
                    if cow3_needs:
                        return ["EAST"]  # tend cow 3 at (6,4)
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

            # Afternoon: Farmer helps in NW crops!
            return resolve_crop_worker_action(fx, fy, f_inv)

        # 5. Crop Worker Action (Farmhands + Farmer in afternoon)
        def resolve_crop_worker_action(wx, wy, worker_inv):
            has_items = any(qty > 0 for qty in worker_inv.values())

            # Shed drop priority at (4,4)
            if (wx, wy) == shed_nw and has_items:
                return ["DROP"]

            # Current tile action
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

            # Tile search in NW
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

            # Day 29 emergency evacuation to shed
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

def run():
    env = ke.make("kaggriculture")
    env.reset()
    env.run([agent, "starter"])
    p0 = env.state[0].observation["farms"][0]["money"]
    p1 = env.state[0].observation["farms"][1]["money"]
    print(f"3-Cow Score: ${p0:.2f} vs Starter: ${p1:.2f}")

if __name__ == "__main__":
    run()
