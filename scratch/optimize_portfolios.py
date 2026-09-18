import kaggle_environments as ke
import numpy as np

def create_agent(num_melons, num_strawberries, num_carrots, hire_limit=2):
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

        # 1. Market Phase: Liquidate Shed Produce by Value Priority
        for item in ["MELON", "STRAWBERRY", "TOMATO", "CARROT", "WHEAT"]:
            qty = shed.get(item, 0)
            if qty > 0:
                market_orders.append(["SELL", item, qty])

        # 2. Market Phase: Labor Scaling
        if day <= 25 and len(hands_pos) < hire_limit and money >= 25:
            market_orders.append(["HIRE"])

        # 3. Market Phase: Seed Purchasing
        s_seeds = seeds.get("STRAWBERRY", 0)
        m_seeds = seeds.get("MELON", 0)
        c_seeds = seeds.get("CARROT", 0)

        # Strawberries: planted once on Days 0-2
        if day <= 2 and s_seeds < num_strawberries and money >= 100:
            needed_s = min(num_strawberries - s_seeds, int(money // 100))
            if needed_s > 0:
                market_orders.append(["BUY_SEED", "STRAWBERRY", needed_s])

        # Melons: 2 batches (Days 0-2 & Days 12-14)
        want_melons = (day <= 2 or 12 <= day <= 14) and m_seeds < num_melons
        if want_melons and money >= 80:
            needed_m = min(num_melons - m_seeds, int(money // 80))
            if needed_m > 0:
                market_orders.append(["BUY_SEED", "MELON", needed_m])

        # Carrots: continuous
        if day <= 26 and c_seeds < num_carrots and money >= 20:
            needed_c = min(num_carrots - c_seeds, int(money // 20))
            if needed_c > 0:
                market_orders.append(["BUY_SEED", "CARROT", needed_c])

        market_orders = market_orders[:10]

        shed_access = (4, 4)

        # Build dynamic cluster tiles based on allocation
        # We place strawberries closest to shed (since harvested multiple times every 2 days!)
        # Next melons, next carrots.
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
            if cx < tx:
                return "EAST"
            elif cx > tx:
                return "WEST"
            elif cy < ty:
                return "SOUTH"
            elif cy > ty:
                return "NORTH"
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
                    if (wx, wy) in strawberry_slots and s_seeds > 0 and day <= 2:
                        claimed_targets.add((wx, wy))
                        return ["PLANT", "STRAWBERRY"]
                    elif (wx, wy) in melon_slots and m_seeds > 0 and (day <= 2 or 12 <= day <= 14):
                        claimed_targets.add((wx, wy))
                        return ["PLANT", "MELON"]
                    elif (wx, wy) in carrot_slots and c_seeds > 0 and day <= 26:
                        claimed_targets.add((wx, wy))
                        return ["PLANT", "CARROT"]

            needed = []
            for cx, cy in cluster:
                if (cx, cy) in claimed_targets:
                    continue
                if cy >= len(tiles) or cx >= len(tiles[0]):
                    continue
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
                    if (cx, cy) in strawberry_slots and s_seeds > 0 and day <= 2:
                        needed.append(((cx, cy), 4))
                    elif (cx, cy) in melon_slots and m_seeds > 0 and (day <= 2 or 12 <= day <= 14):
                        needed.append(((cx, cy), 4))
                    elif (cx, cy) in carrot_slots and c_seeds > 0:
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
        ("Balanced_8M_4S_4C", 8, 4, 4),
        ("StrawHeavy_6M_8S_4C", 6, 8, 4),
        ("UltraStraw_4M_10S_4C", 4, 10, 4),
        ("PureStraw_0M_14S_4C", 0, 14, 4),
    ]

    print("--- BENCHMARK VS V4 MEGACLUSTER (Melon Rusher) ---")
    for name, m, s, c in configs:
        ag = create_agent(m, s, c)
        env = ke.make("kaggriculture")
        env.run([ag, "submission_v4_megacluster.py"])
        r_ag = env.steps[-1][0]["reward"]
        r_v4 = env.steps[-1][1]["reward"]
        print(f"{name:20s}: Ag=${r_ag:,.2f} | V4=${r_v4:,.2f} | Diff=${(r_ag-r_v4):+,.2f}")

    print("\n--- BENCHMARK VS STARTER (Baseline Non-disruptive) ---")
    for name, m, s, c in configs:
        ag = create_agent(m, s, c)
        env = ke.make("kaggriculture")
        env.run([ag, "starter"])
        r_ag = env.steps[-1][0]["reward"]
        print(f"{name:20s}: Ag=${r_ag:,.2f}")

if __name__ == "__main__":
    benchmark()
