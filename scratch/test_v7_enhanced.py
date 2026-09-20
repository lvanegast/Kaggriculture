import kaggle_environments as ke

def create_v7_enhanced():
    """FarmBrain v7.2 Apex: Evolution of the 431-Elo v7 architecture.
    Refinements:
    - Retains proven 2-farmhand labor structure (0 congestion, max efficiency).
    - Retains the high-yield 14 Melons + 4 Carrots core engine.
    - Day 2 Opponent Detection: pivots to Strawberries if opponent is rushing melons.
    - Zero-Waste Seed Cutoffs: No melons after Day 14, no carrots after Day 25.
    - Day 29 Emergency Shed Evacuation: ensures 100% backpack liquidation into cash.
    - Multi-worker collision-free target reservation.
    """
    def agent(obs, config=None):
        try:
            farms = obs.get("farms", [])
            player = obs.get("player", 0)
            opp_player = 1 - player
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

            # 1. Opponent Profiling
            opp_farm = farms[opp_player] if len(farms) > opp_player else {}
            opp_tiles = opp_farm.get("tiles", [])
            opp_melons = 0
            for row in opp_tiles:
                for t in row:
                    if isinstance(t, dict) and t.get("crop") == "MELON":
                        opp_melons += 1

            # Dynamic Portfolio:
            # If opponent has planted >= 4 melons by Day 2+, activate 4 Strawberries
            # If opponent is passive, maximize 14 Melons + 4 Carrots
            if day >= 2 and opp_melons >= 4:
                num_melons = 8
                num_strawberries = 4
                num_carrots = 4
            else:
                num_melons = 14
                num_strawberries = 0
                num_carrots = 4

            market_orders = []

            # 2. Market Phase: Liquidate Shed Produce by Value Priority
            for item in ["MELON", "STRAWBERRY", "TOMATO", "CARROT", "WHEAT"]:
                qty = shed.get(item, 0)
                if qty > 0:
                    market_orders.append(["SELL", item, qty])

            # 3. Labor Scaling: 2 Farmhands (proven sweet spot on Kaggle ladder)
            if day <= 25 and len(hands_pos) < 2 and money >= 25:
                market_orders.append(["HIRE"])

            # 4. Seed Purchasing with Zero-Waste Cutoffs
            s_seeds = seeds.get("STRAWBERRY", 0)
            m_seeds = seeds.get("MELON", 0)
            c_seeds = seeds.get("CARROT", 0)

            if num_strawberries > 0 and day <= 2 and s_seeds < num_strawberries and money >= 100:
                needed_s = min(num_strawberries - s_seeds, int(money // 100))
                if needed_s > 0:
                    market_orders.append(["BUY_SEED", "STRAWBERRY", needed_s])

            # Melon batches: Batch 1 (Days 0-2), Batch 2 (Days 12-14). Never after Day 14!
            want_melons = (day <= 2 or 12 <= day <= 14) and m_seeds < num_melons
            if want_melons and money >= 80:
                needed_m = min(num_melons - m_seeds, int(money // 80))
                if needed_m > 0:
                    market_orders.append(["BUY_SEED", "MELON", needed_m])

            # Carrots: only until Day 25 (take 3 days to mature). Never after Day 25!
            if day <= 25 and c_seeds < num_carrots and money >= 20:
                needed_c = min(num_carrots - c_seeds, int(money // 20))
                if needed_c > 0:
                    market_orders.append(["BUY_SEED", "CARROT", needed_c])

            market_orders = market_orders[:10]

            shed_access = (4, 4)
            candidates = [
                (3, 4), (4, 3), (3, 3), (2, 4), (4, 2), (2, 3), (3, 2), (2, 2),
                (1, 4), (4, 1), (1, 3), (3, 1), (1, 2), (2, 1), (0, 4), (4, 0),
                (0, 3), (3, 0), (0, 2), (2, 0)
            ]

            strawberry_slots = candidates[:num_strawberries]
            melon_slots = candidates[num_strawberries : num_strawberries + num_melons]
            carrot_slots = candidates[num_strawberries + num_melons : num_strawberries + num_melons + num_carrots]

            cluster = [shed_access] + strawberry_slots + melon_slots + carrot_slots

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

                # Shed drop
                if (wx, wy) == shed_access and has_items:
                    return ["DROP"]

                # Current tile actions
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
                        if (wx, wy) in strawberry_slots and s_seeds > 0 and day <= 2:
                            claimed_targets.add((wx, wy))
                            return ["PLANT", "STRAWBERRY"]
                        elif (wx, wy) in melon_slots and m_seeds > 0 and (day <= 2 or 12 <= day <= 14):
                            claimed_targets.add((wx, wy))
                            return ["PLANT", "MELON"]
                        elif (wx, wy) in carrot_slots and c_seeds > 0 and day <= 25:
                            claimed_targets.add((wx, wy))
                            return ["PLANT", "CARROT"]

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
                        if (cx, cy) in strawberry_slots and s_seeds > 0 and day <= 2: needed.append(((cx, cy), 4))
                        elif (cx, cy) in melon_slots and m_seeds > 0 and (day <= 2 or 12 <= day <= 14): needed.append(((cx, cy), 4))
                        elif (cx, cy) in carrot_slots and c_seeds > 0: needed.append(((cx, cy), 4))

                # Day 29 Emergency Evacuation: drop all backpack items into shed before season ends
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

        except Exception:
            return {"farmer": ["PASS"], "hands": [], "market": []}
    return agent

def benchmark():
    enh = create_v7_enhanced()

    print("--- BENCHMARK V7 ENHANCED VS CURRENT BEST (V7 - 431 ELO) ---")
    env1 = ke.make("kaggriculture")
    env1.run([enh, "submission_v7_adaptive.py"])
    r_enh = env1.steps[-1][0]["reward"]
    r_v7 = env1.steps[-1][1]["reward"]
    print(f"Duel 1: Enh P0=${r_enh:,.2f} vs V7 P1=${r_v7:,.2f} (diff=${r_enh - r_v7:+,.2f})")

    env2 = ke.make("kaggriculture")
    env2.run(["submission_v7_adaptive.py", enh])
    r_v7_2 = env2.steps[-1][0]["reward"]
    r_enh_2 = env2.steps[-1][1]["reward"]
    print(f"Duel 2: V7 P0=${r_v7_2:,.2f} vs Enh P1=${r_enh_2:,.2f} (diff=${r_enh_2 - r_v7_2:+,.2f})")

    env3 = ke.make("kaggriculture")
    env3.run([enh, "starter"])
    print(f"Enh vs Starter: ${env3.steps[-1][0]['reward']:,.2f}")

if __name__ == "__main__":
    benchmark()
