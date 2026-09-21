import kaggle_environments as ke

def create_dual_quadrant_agent():
    """Dual-Quadrant Expansion Engine (NW + NE).
    - Starts with $3,000.
    - Buys NE quadrant ($1,000) on Day 0, expanding farm to 10x5 (50 tiles!).
    - Still has $2,000 for seeds and labor.
    - Two independent shed drop points:
        * NW workers drop at (4, 4)
        * NE workers drop at (5, 4)
    - 3 Farmhands (4 workers total: 2 for NW, 2 for NE).
    - Multiplies crop yield by 2x:
        * NW: 12 Melons + 4 Carrots
        * NE: 6 Strawberries + 12 Melons
    """
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
            seeds = private.get("seeds", {})
            shed = private.get("shed", {})
            inventories = private.get("inventories", [])
            f_inv = inventories[0] if inventories else {}
            money = farm.get("money", 0)
            unlocked = farm.get("unlocked_quadrants", ["NW"])

            market_orders = []

            # 1. Market Phase: Liquidate Shed Produce by Value Priority
            for item in ["MELON", "STRAWBERRY", "TOMATO", "CARROT", "WHEAT"]:
                qty = shed.get(item, 0)
                if qty > 0:
                    market_orders.append(["SELL", item, qty])

            # 2. Land Expansion: Buy NE immediately on Day 0 ($1,000)
            if "NE" not in unlocked and money >= 1200 and day <= 2:
                market_orders.append(["BUY_LAND"])

            # 3. Labor Scaling: 3 Farmhands (96 actions/day to cover 2 quadrants)
            if day <= 25 and len(hands_pos) < 3 and money >= 25:
                market_orders.append(["HIRE"])

            # 4. Seeds Purchasing
            s_seeds = seeds.get("STRAWBERRY", 0)
            m_seeds = seeds.get("MELON", 0)
            c_seeds = seeds.get("CARROT", 0)

            # Target crop capacities across 2 quadrants:
            # 6 Strawberries (permanent yield into town shops)
            # 20 Melons (massive wealth generation)
            # 6 Carrots (continuous fast liquidity)
            target_s = 6 if "NE" in unlocked else 4
            target_m = 20 if "NE" in unlocked else 12
            target_c = 6 if "NE" in unlocked else 4

            if day <= 2 and s_seeds < target_s and money >= 100:
                ns = min(target_s - s_seeds, int(money // 100))
                if ns > 0: market_orders.append(["BUY_SEED", "STRAWBERRY", ns])

            want_melons = (day <= 2 or 12 <= day <= 14) and m_seeds < target_m
            if want_melons and money >= 80:
                nm = min(target_m - m_seeds, int(money // 80))
                if nm > 0: market_orders.append(["BUY_SEED", "MELON", nm])

            if day <= 25 and c_seeds < target_c and money >= 20:
                nc = min(target_c - c_seeds, int(money // 20))
                if nc > 0: market_orders.append(["BUY_SEED", "CARROT", nc])

            market_orders = market_orders[:10]

            # Shed drop points: NW drops at (4,4), NE drops at (5,4)
            shed_access_nw = (4, 4)
            shed_access_ne = (5, 4)

            # Cluster layout in NW (x <= 4, y <= 4)
            nw_slots = [
                (3, 4), (4, 3), (3, 3), (2, 4), (4, 2), (2, 3), (3, 2), (2, 2),
                (1, 4), (4, 1), (1, 3), (3, 1), (1, 2), (2, 1), (0, 4), (4, 0),
                (0, 3), (3, 0), (0, 2), (2, 0)
            ]

            # Cluster layout in NE (x >= 5, y <= 4) - mirrored right around shed access (5,4)
            ne_slots = []
            if "NE" in unlocked:
                ne_slots = [
                    (6, 4), (5, 3), (6, 3), (7, 4), (5, 2), (7, 3), (6, 2), (7, 2),
                    (8, 4), (5, 1), (8, 3), (6, 1), (8, 2), (7, 1), (9, 4), (5, 0),
                    (9, 3), (6, 0), (9, 2), (7, 0)
                ]

            all_slots = nw_slots + ne_slots
            # Assign strawberries (6 closest to both shed sides: 3 in NW, 3 in NE)
            s_slots = [(3, 4), (4, 3), (3, 3)] + ([(6, 4), (5, 3), (6, 3)] if "NE" in unlocked else [(2, 4)])
            remaining_slots = [p for p in all_slots if p not in s_slots]
            c_slots = remaining_slots[-target_c:]
            m_slots = [p for p in remaining_slots if p not in c_slots][:target_m]

            cluster = [shed_access_nw] + ([shed_access_ne] if "NE" in unlocked else []) + s_slots + m_slots + c_slots

            def _step_direction(current, target):
                cx, cy = current
                tx, ty = target
                if cx < tx: return "EAST"
                elif cx > tx: return "WEST"
                elif cy < ty: return "SOUTH"
                elif cy > ty: return "NORTH"
                return "PASS"

            claimed_targets = set()

            def get_closest_shed(wx, wy):
                if "NE" in unlocked and wx >= 5:
                    return shed_access_ne
                return shed_access_nw

            def resolve_worker_action(wx, wy, worker_inv):
                has_items = any(qty > 0 for qty in worker_inv.values())
                shed_drop = get_closest_shed(wx, wy)

                # Shed drop
                if (wx, wy) in (shed_access_nw, shed_access_ne) and has_items:
                    return ["DROP"]

                # Current tile
                if wy < len(tiles) and wx < len(tiles[0]):
                    ct = tiles[wy][wx]
                    if isinstance(ct, dict):
                        k = ct.get("kind")
                        if k == "PLANT":
                            crop = ct.get("crop")
                            age = day - ct.get("planted_day", 0)
                            y_units = ct.get("yield_units", 0)
                            if crop == "MELON": mature = (age >= 12 and y_units > 0)
                            elif crop == "STRAWBERRY": mature = (age >= 10 and y_units > 0)
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
                    elif ct is None and (wx, wy) in cluster:
                        if (wx, wy) in s_slots and s_seeds > 0 and day <= 2:
                            claimed_targets.add((wx, wy))
                            return ["PLANT", "STRAWBERRY"]
                        elif (wx, wy) in m_slots and m_seeds > 0 and (day <= 2 or 12 <= day <= 14):
                            claimed_targets.add((wx, wy))
                            return ["PLANT", "MELON"]
                        elif (wx, wy) in c_slots and c_seeds > 0 and day <= 25:
                            claimed_targets.add((wx, wy))
                            return ["PLANT", "CARROT"]

                # Find nearest tile needing attention
                needed = []
                for cx, cy in cluster:
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
                            else: mature = (age >= 3 and y_units > 0)

                            if mature: needed.append(((cx, cy), 1))
                            elif not t.get("watered_today", False) and day <= 28: needed.append(((cx, cy), 2))
                        elif k == "WEED": needed.append(((cx, cy), 3))
                    elif t is None and day <= 25:
                        if (cx, cy) in s_slots and s_seeds > 0 and day <= 2: needed.append(((cx, cy), 4))
                        elif (cx, cy) in m_slots and m_seeds > 0 and (day <= 2 or 12 <= day <= 14): needed.append(((cx, cy), 4))
                        elif (cx, cy) in c_slots and c_seeds > 0: needed.append(((cx, cy), 4))

                if day >= 29 and has_items:
                    return [_step_direction((wx, wy), shed_drop)]

                if needed:
                    # Preference: prioritize tiles in the same quadrant as the worker to minimize cross-travel
                    def tile_distance_cost(item):
                        prio, (tx, ty) = item[1], item[0]
                        dist = abs(wx - tx) + abs(wy - ty)
                        cross_penalty = 10 if (wx < 5 and tx >= 5) or (wx >= 5 and tx < 5) else 0
                        return (prio, dist + cross_penalty)

                    needed.sort(key=tile_distance_cost)
                    tx, ty = needed[0][0]
                    claimed_targets.add((tx, ty))
                    return [_step_direction((wx, wy), (tx, ty))]
                elif has_items:
                    return [_step_direction((wx, wy), shed_drop)]

                return ["PASS"]

            farmer_act = resolve_worker_action(fx, fy, f_inv)
            hands_act = []
            for h_idx, (hx, hy) in enumerate(hands_pos):
                h_inv = inventories[h_idx + 1] if len(inventories) > h_idx + 1 else {}
                h_act = resolve_worker_action(hx, hy, h_inv)
                hands_act.append(h_act)

            return {"farmer": farmer_act, "hands": hands_act, "market": market_orders}

        except Exception:
            return {"farmer": ["PASS"], "hands": [], "market": []}
    return agent

def benchmark():
    dual = create_dual_quadrant_agent()

    print("--- BENCHMARK DUAL-QUADRANT VS STARTER ---")
    env_s = ke.make("kaggriculture")
    env_s.run([dual, "starter"])
    r_dual_s = env_s.steps[-1][0]["reward"]
    print(f"Dual-Quadrant vs Starter: ${r_dual_s:,.2f}")

    print("\n--- BENCHMARK DUAL-QUADRANT VS V11 (Single Quadrant Champion) ---")
    # Dual P0 vs V11 P1
    env_v11 = ke.make("kaggriculture")
    env_v11.run([dual, "submission_v11_apex_master.py"])
    r_dual = env_v11.steps[-1][0]["reward"]
    r_v11 = env_v11.steps[-1][1]["reward"]
    print(f"Duel 1: Dual P0=${r_dual:,.2f} vs V11 P1=${r_v11:,.2f} (Dual diff=${r_dual - r_v11:+,.2f})")

    # V11 P0 vs Dual P1
    env_v11_2 = ke.make("kaggriculture")
    env_v11_2.run(["submission_v11_apex_master.py", dual])
    r_v11_2 = env_v11_2.steps[-1][0]["reward"]
    r_dual_2 = env_v11_2.steps[-1][1]["reward"]
    print(f"Duel 2: V11 P0=${r_v11_2:,.2f} vs Dual P1=${r_dual_2:,.2f} (Dual diff=${r_dual_2 - r_v11_2:+,.2f})")

if __name__ == "__main__":
    benchmark()
