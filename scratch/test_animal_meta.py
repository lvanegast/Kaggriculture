import kaggle_environments as ke

def create_cow_agent():
    """Agent implementing Cows + Pasture + Crops near shed."""
    def agent(obs, config=None):
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
        seeds = private.get("seeds", {})
        shed = private.get("shed", {})
        inventories = private.get("inventories", [])
        f_inv = inventories[0] if inventories else {}
        money = farm.get("money", 0)
        unlocked = farm.get("unlocked_quadrants", ["NW"])

        market_orders = []

        # 1. Market Phase: Liquidate Shed Produce & Products
        for item in ["MELON", "STRAWBERRY", "MILK", "FERTILIZER", "TOMATO", "CARROT", "WHEAT"]:
            qty = shed.get(item, 0)
            if qty > 0:
                market_orders.append(["SELL", item, qty])

        # 2. Land Expansion: Unlock NE when rich
        if "NE" not in unlocked and day <= 8 and money >= 1800:
            market_orders.append(["BUY_LAND"])

        # 3. Labor: Hire up to 2 hands
        if day <= 25 and len(hands_pos) < 2 and money >= 25:
            market_orders.append(["HIRE"])

        # 4. Animal purchase: 1 COW on Day 2 if money allows
        has_cow_in_shed = shed.get("COW", 0) > 0
        has_cow_on_board = any(
            isinstance(t, dict) and t.get("animal") == "COW"
            for row in tiles for t in row
        )
        if not has_cow_on_board and not has_cow_in_shed and day <= 4 and money >= 600:
            market_orders.append(["BUY_ANIMAL", "COW", 1])

        # 5. Seeds: Wheat for cow food, Strawberries, Melons, Carrots
        s_seeds = seeds.get("STRAWBERRY", 0)
        m_seeds = seeds.get("MELON", 0)
        c_seeds = seeds.get("CARROT", 0)
        w_seeds = seeds.get("WHEAT", 0)

        # 2 Wheat for feeding cow
        if day <= 20 and w_seeds < 2 and money >= 30:
            market_orders.append(["BUY_SEED", "WHEAT", 2 - w_seeds])

        # 4 Strawberries
        if day <= 2 and s_seeds < 4 and money >= 100:
            ns = min(4 - s_seeds, int(money // 100))
            if ns > 0: market_orders.append(["BUY_SEED", "STRAWBERRY", ns])

        # Melons
        want_melons = (day <= 2 or 12 <= day <= 14) and m_seeds < 10
        if want_melons and money >= 80:
            nm = min(10 - m_seeds, int(money // 80))
            if nm > 0: market_orders.append(["BUY_SEED", "MELON", nm])

        # Carrots
        if day <= 26 and c_seeds < 4 and money >= 20:
            nc = min(4 - c_seeds, int(money // 20))
            if nc > 0: market_orders.append(["BUY_SEED", "CARROT", nc])

        market_orders = market_orders[:10]

        shed_access = (4, 4)
        pasture_tile = (4, 3) # directly adjacent to shed

        # Crops slots around shed
        crop_slots = [
            (3, 4), (3, 3), (2, 4), (4, 2), (2, 3), (3, 2), (2, 2),
            (1, 4), (4, 1), (1, 3), (3, 1), (1, 2), (2, 1), (0, 4), (4, 0)
        ]
        if "NE" in unlocked:
            crop_slots += [(5, 4), (5, 3), (5, 2), (6, 4), (6, 3)]

        def _step_direction(current, target):
            cx, cy = current
            tx, ty = target
            if cx < tx: return "EAST"
            elif cx > tx: return "WEST"
            elif cy < ty: return "SOUTH"
            elif cy > ty: return "NORTH"
            return "PASS"

        claimed_targets = set()

        def resolve_worker_action(wx, wy, worker_inv):
            has_items = any(qty > 0 for qty in worker_inv.values())

            # Shed drop priority
            if (wx, wy) == shed_access and has_items:
                # Keep 1 wheat for feeding if cow is unfed
                return ["DROP"]

            # Current tile actions
            if wy < len(tiles) and wx < len(tiles[0]):
                ct = tiles[wy][wx]
                if (wx, wy) == pasture_tile:
                    if ct is None:
                        claimed_targets.add((wx, wy))
                        return ["BUILD_PASTURE"]
                    elif isinstance(ct, dict):
                        if ct.get("kind") == "PASTURE" and "animal" not in ct:
                            if worker_inv.get("COW", 0) > 0:
                                claimed_targets.add((wx, wy))
                                return ["PLACE", "COW"]
                        elif ct.get("animal") == "COW":
                            if ct.get("yield_units", 0) > 0:
                                claimed_targets.add((wx, wy))
                                return ["HARVEST"]
                            elif ct.get("fertilizer_available", False):
                                claimed_targets.add((wx, wy))
                                return ["COLLECT_FERTILIZER"]
                            elif not ct.get("fed_today", False) and worker_inv.get("WHEAT", 0) > 0:
                                claimed_targets.add((wx, wy))
                                return ["FEED"]
                            elif not ct.get("cared_today", False):
                                claimed_targets.add((wx, wy))
                                return ["CARE"]

                elif isinstance(ct, dict):
                    k = ct.get("kind")
                    if k == "PLANT":
                        crop = ct.get("crop")
                        age = day - ct.get("planted_day", 0)
                        y_units = ct.get("yield_units", 0)
                        if crop == "MELON": mature = (age >= 12 and y_units > 0)
                        elif crop == "STRAWBERRY": mature = (age >= 10 and y_units > 0)
                        elif crop == "WHEAT": mature = (age >= 2 and y_units > 0)
                        else: mature = (age >= 3 and y_units > 0)

                        if mature:
                            claimed_targets.add((wx, wy))
                            return ["HARVEST"]
                        elif not ct.get("watered_today", False) and day <= 28:
                            claimed_targets.add((wx, wy))
                            return ["WATER"]
                    elif k == "WEED":
                        claimed_targets.add((wx, wy))
                        return ["DIG"]

                elif ct is None and (wx, wy) in crop_slots:
                    if (wx, wy) == crop_slots[0] and w_seeds > 0:
                        claimed_targets.add((wx, wy))
                        return ["PLANT", "WHEAT"]
                    elif (wx, wy) in crop_slots[1:5] and s_seeds > 0 and day <= 2:
                        claimed_targets.add((wx, wy))
                        return ["PLANT", "STRAWBERRY"]
                    elif m_seeds > 0 and (day <= 2 or 12 <= day <= 14):
                        claimed_targets.add((wx, wy))
                        return ["PLANT", "MELON"]
                    elif c_seeds > 0 and day <= 26:
                        claimed_targets.add((wx, wy))
                        return ["PLANT", "CARROT"]

            # Pasture needs attention?
            px, py = pasture_tile
            pt = tiles[py][px]
            if (px, py) not in claimed_targets:
                if pt is None:
                    claimed_targets.add((px, py))
                    return [_step_direction((wx, wy), (px, py))]
                elif isinstance(pt, dict) and pt.get("kind") == "PASTURE" and "animal" not in pt:
                    if worker_inv.get("COW", 0) > 0:
                        claimed_targets.add((px, py))
                        return [_step_direction((wx, wy), (px, py))]
                    elif shed.get("COW", 0) > 0 and (wx, wy) == shed_access:
                        return ["PICKUP", "COW", 1]
                    elif shed.get("COW", 0) > 0:
                        return [_step_direction((wx, wy), shed_access)]
                elif isinstance(pt, dict) and pt.get("animal") == "COW":
                    if pt.get("yield_units", 0) > 0 or pt.get("fertilizer_available", False) or not pt.get("cared_today", False):
                        claimed_targets.add((px, py))
                        return [_step_direction((wx, wy), (px, py))]
                    elif not pt.get("fed_today", False) and worker_inv.get("WHEAT", 0) > 0:
                        claimed_targets.add((px, py))
                        return [_step_direction((wx, wy), (px, py))]

            # Crops needing attention
            needed = []
            for cx, cy in crop_slots:
                if (cx, cy) in claimed_targets: continue
                if cy >= len(tiles) or cx >= len(tiles[0]): continue
                t = tiles[cy][cx]
                if isinstance(t, dict):
                    k = t.get("kind")
                    if k == "PLANT":
                        crop = t.get("crop")
                        age = day - t.get("planted_day", 0)
                        y_units = t.get("yield_units", 0)
                        if crop == "MELON": mature = (age >= 12 and y_units > 0)
                        elif crop == "STRAWBERRY": mature = (age >= 10 and y_units > 0)
                        elif crop == "WHEAT": mature = (age >= 2 and y_units > 0)
                        else: mature = (age >= 3 and y_units > 0)

                        if mature: needed.append(((cx, cy), 1))
                        elif not t.get("watered_today", False) and day <= 28: needed.append(((cx, cy), 2))
                    elif k == "WEED": needed.append(((cx, cy), 3))
                elif t is None and day <= 26:
                    needed.append(((cx, cy), 4))

            if day >= 29 and has_items:
                return [_step_direction((wx, wy), shed_access)]

            if needed:
                needed.sort(key=lambda item: (item[1], abs(wx - item[0][0]) + abs(wy - item[0][1])))
                tx, ty = needed[0][0]
                claimed_targets.add((tx, ty))
                return [_step_direction((wx, wy), (tx, ty))]
            elif has_items:
                return [_step_direction((wx, wy), shed_access)]

            return ["PASS"]

        farmer_act = resolve_worker_action(fx, fy, f_inv)
        hands_act = []
        for h_idx, (hx, hy) in enumerate(hands_pos):
            h_inv = inventories[h_idx + 1] if len(inventories) > h_idx + 1 else {}
            h_act = resolve_worker_action(hx, hy, h_inv)
            hands_act.append(h_act)

        return {"farmer": farmer_act, "hands": hands_act, "market": market_orders}
    return agent

def benchmark():
    ag = create_cow_agent()
    print("--- BENCHMARK COW AGENT ---")
    env1 = ke.make("kaggriculture")
    env1.run([ag, "submission_v7_adaptive.py"])
    r_cow = env1.steps[-1][0]["reward"]
    r_v7 = env1.steps[-1][1]["reward"]
    print(f"Cow Agent vs V7: Cow=${r_cow:,.2f} vs V7=${r_v7:,.2f} (diff=${r_cow - r_v7:+,.2f})")

    env2 = ke.make("kaggriculture")
    env2.run([ag, "starter"])
    print(f"Cow Agent vs Starter: ${env2.steps[-1][0]['reward']:,.2f}")

if __name__ == "__main__":
    benchmark()
