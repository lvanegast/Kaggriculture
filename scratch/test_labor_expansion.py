import kaggle_environments as ke

def create_worker_agent(m_count, s_count, c_count, max_hands=3):
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

        market_orders = []

        # 1. Sell produce
        for item in ["MELON", "STRAWBERRY", "TOMATO", "CARROT", "WHEAT"]:
            qty = shed.get(item, 0)
            if qty > 0:
                market_orders.append(["SELL", item, qty])

        # 2. Labor scaling: hire up to max_hands
        if day <= 25 and len(hands_pos) < max_hands and money >= 25:
            market_orders.append(["HIRE"])

        # 3. Seed purchasing
        s_seeds = seeds.get("STRAWBERRY", 0)
        m_seeds = seeds.get("MELON", 0)
        c_seeds = seeds.get("CARROT", 0)

        if day <= 2 and s_seeds < s_count and money >= 100:
            ns = min(s_count - s_seeds, int(money // 100))
            if ns > 0: market_orders.append(["BUY_SEED", "STRAWBERRY", ns])

        want_melons = (day <= 2 or 12 <= day <= 14) and m_seeds < m_count
        if want_melons and money >= 80:
            nm = min(m_count - m_seeds, int(money // 80))
            if nm > 0: market_orders.append(["BUY_SEED", "MELON", nm])

        if day <= 26 and c_seeds < c_count and money >= 20:
            nc = min(c_count - c_seeds, int(money // 20))
            if nc > 0: market_orders.append(["BUY_SEED", "CARROT", nc])

        market_orders = market_orders[:10]

        shed_access = (4, 4)
        candidates = [
            (3, 4), (4, 3), (3, 3), (2, 4), (4, 2), (2, 3), (3, 2), (2, 2),
            (1, 4), (4, 1), (1, 3), (3, 1), (1, 2), (2, 1), (0, 4), (4, 0),
            (0, 3), (3, 0), (0, 2), (2, 0), (0, 1), (1, 0), (1, 1), (0, 0)
        ]

        s_slots = candidates[:s_count]
        m_slots = candidates[s_count : s_count + m_count]
        c_slots = candidates[s_count + m_count : s_count + m_count + c_count]

        cluster = [shed_access] + s_slots + m_slots + c_slots

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

            if (wx, wy) == shed_access and has_items:
                return ["DROP"]

            if wy < len(tiles) and wx < len(tiles[0]):
                ct = tiles[wy][wx]
                if isinstance(ct, dict):
                    k = ct.get("kind")
                    if k == "PLANT":
                        crop = ct.get("crop")
                        age = day - ct.get("planted_day", 0)
                        y_units = ct.get("yield_units", 0)
                        if crop == "MELON":
                            mature = (age >= 12 and y_units > 0)
                        elif crop == "STRAWBERRY":
                            mature = (age >= 10 and y_units > 0)
                        else:
                            mature = (age >= 3 and y_units > 0)

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
                    elif (wx, wy) in c_slots and c_seeds > 0 and day <= 26:
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
                        if crop == "MELON":
                            mature = (age >= 12 and y_units > 0)
                        elif crop == "STRAWBERRY":
                            mature = (age >= 10 and y_units > 0)
                        else:
                            mature = (age >= 3 and y_units > 0)

                        if mature:
                            needed.append(((cx, cy), 1))
                        elif not t.get("watered_today", False) and day <= 28:
                            needed.append(((cx, cy), 2))
                    elif k == "WEED":
                        needed.append(((cx, cy), 3))
                elif t is None and day <= 26:
                    if (cx, cy) in s_slots and s_seeds > 0 and day <= 2:
                        needed.append(((cx, cy), 4))
                    elif (cx, cy) in m_slots and m_seeds > 0 and (day <= 2 or 12 <= day <= 14):
                        needed.append(((cx, cy), 4))
                    elif (cx, cy) in c_slots and c_seeds > 0:
                        needed.append(((cx, cy), 4))

            if day >= 29 and has_items:
                tx, ty = shed_access
                return [_step_direction((wx, wy), (tx, ty))]

            if needed:
                needed.sort(key=lambda item: (item[1], abs(wx - item[0][0]) + abs(wy - item[0][1])))
                tx, ty = needed[0][0]
                claimed_targets.add((tx, ty))
                return [_step_direction((wx, wy), (tx, ty))]
            elif has_items:
                tx, ty = shed_access
                return [_step_direction((wx, wy), (tx, ty))]

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
    configs = [
        ("Balanced_8M_4S_4C_2H", 8, 4, 4, 2),
        ("Balanced_8M_4S_4C_3H", 8, 4, 4, 3),
        ("Expanded_10M_4S_4C_3H", 10, 4, 4, 3),
        ("Expanded_10M_6S_4C_3H", 10, 6, 4, 3),
        ("Expanded_12M_4S_4C_3H", 12, 4, 4, 3),
    ]
    print("--- LABOR & EXPANSION BENCHMARK ---")
    for name, m, s, c, h in configs:
        ag = create_worker_agent(m, s, c, h)
        env = ke.make("kaggriculture")
        env.run([ag, "submission_v4_megacluster.py"])
        r1 = env.steps[-1][0]["reward"]
        v4_r = env.steps[-1][1]["reward"]

        env2 = ke.make("kaggriculture")
        env2.run([ag, "starter"])
        r2 = env2.steps[-1][0]["reward"]
        print(f"{name:25s} | vs V4: Ag=${r1:,.2f} vs V4=${v4_r:,.2f} (diff=${r1-v4_r:+,.2f}) | vs Starter: ${r2:,.2f}")

if __name__ == "__main__":
    benchmark()
