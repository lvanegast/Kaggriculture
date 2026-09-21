import kaggle_environments as ke

def run():
    env = ke.make("kaggriculture")
    def test_agent(obs, config=None):
        step = obs.get("step", 0)
        day = obs.get("day", 0)
        hour = obs.get("hour", 0)
        farm = obs["farms"][obs["player"]]
        fx, fy = farm["farmer"]
        private = obs["private"]
        inv = private["inventories"][0]
        shed = private["shed"]
        money = farm["money"]
        
        market = []
        farmer = ["PASS"]
        
        pt1 = farm["tiles"][4][5] # (5, 4)
        pt2 = farm["tiles"][3][5] # (5, 3)
        
        # Day 0: Setup NE land + Cow 1 at (5,4) + Cow 2 at (5,3)
        if day == 0:
            if step == 0:
                market = [["BUY_LAND"], ["BUY_ANIMAL", "COW", 2], ["BUY_PRODUCT", "WHEAT", 15]]
                farmer = ["EAST"] # move to (5,4)
            elif step == 1:
                farmer = ["BUILD_PASTURE"] # at (5,4)
            elif step == 2:
                farmer = ["NORTH"] # move to (5,3)
            elif step == 3:
                farmer = ["BUILD_PASTURE"] # at (5,3)
            elif step == 4:
                farmer = ["SOUTH"] # move to (5,4)
            elif step == 5:
                farmer = ["PICKUP", "COW", 2]
            elif step == 6:
                farmer = ["PLACE", "COW"] # Cow 1 placed at (5,4)
            elif step == 7:
                farmer = ["NORTH"] # move to (5,3)
            elif step == 8:
                farmer = ["PLACE", "COW"] # Cow 2 placed at (5,3)
            elif step == 9:
                farmer = ["SOUTH"] # return to (5,4)
            elif step == 10:
                farmer = ["PICKUP", "WHEAT", 2]
            elif step == 11:
                farmer = ["FEED"] # feed Cow 1 at (5,4)
            elif step == 12:
                farmer = ["CARE"] # care Cow 1 at (5,4)
            elif step == 13:
                farmer = ["NORTH"] # move to (5,3)
            elif step == 14:
                farmer = ["FEED"] # feed Cow 2 at (5,3)
            elif step == 15:
                farmer = ["CARE"] # care Cow 2 at (5,3)
            elif step == 16:
                farmer = ["SOUTH"] # return to (5,4)
            elif step == 17:
                farmer = ["WEST"] # return to (4,4)
        else:
            # Daily routine for farmer:
            if hour == 0 and shed.get("WHEAT", 0) < 10 and money > 300:
                market.append(["BUY_PRODUCT", "WHEAT", 10])
            
            # Sell milk / fertilizer
            if shed.get("MILK", 0) > 0:
                market.append(["SELL", "MILK", shed["MILK"]])
            if shed.get("FERTILIZER", 0) > 0:
                market.append(["SELL", "FERTILIZER", shed["FERTILIZER"]])
                
            # Cow care routine:
            cow1_needs = pt1 and isinstance(pt1, dict) and "animal" in pt1 and (
                not pt1.get("fed_today") or not pt1.get("cared_today") or pt1.get("fertilizer_available") or pt1.get("yield_units", 0) > 0
            )
            cow2_needs = pt2 and isinstance(pt2, dict) and "animal" in pt2 and (
                not pt2.get("fed_today") or not pt2.get("cared_today") or pt2.get("fertilizer_available") or pt2.get("yield_units", 0) > 0
            )
            
            if (fx, fy) == (4, 4) and (cow1_needs or cow2_needs):
                farmer = ["EAST"] # go to (5,4)
            elif (fx, fy) == (5, 4):
                if pt1.get("fertilizer_available"):
                    farmer = ["COLLECT_FERTILIZER"]
                elif pt1.get("yield_units", 0) > 0:
                    farmer = ["HARVEST"]
                elif not pt1.get("fed_today"):
                    if inv.get("WHEAT", 0) > 0:
                        farmer = ["FEED"]
                    elif shed.get("WHEAT", 0) > 0:
                        # Pickup 2 wheat for both cows!
                        farmer = ["PICKUP", "WHEAT", 2 if cow2_needs else 1]
                elif not pt1.get("cared_today"):
                    farmer = ["CARE"]
                elif cow2_needs:
                    farmer = ["NORTH"] # go to (5,3)
                elif any(v > 0 for v in inv.values()):
                    farmer = ["DROP"]
                else:
                    farmer = ["WEST"] # return to (4,4)
            elif (fx, fy) == (5, 3):
                if pt2.get("fertilizer_available"):
                    farmer = ["COLLECT_FERTILIZER"]
                elif pt2.get("yield_units", 0) > 0:
                    farmer = ["HARVEST"]
                elif not pt2.get("fed_today"):
                    if inv.get("WHEAT", 0) > 0:
                        farmer = ["FEED"]
                    else:
                        farmer = ["SOUTH"] # go back to get wheat
                elif not pt2.get("cared_today"):
                    farmer = ["CARE"]
                else:
                    farmer = ["SOUTH"] # return to (5,4) to drop

        if hour == 23:
            print(f"Day {day:2d} End: Money=${farm['money']:.0f}, Shed Milk={shed.get('MILK',0)}, Fert={shed.get('FERTILIZER',0)}")

        return {"farmer": farmer, "hands": [], "market": market}

    env.step([test_agent(env.state[0].observation), {"farmer": ["PASS"], "hands": [], "market": []}])
    for _ in range(718):
        obs = env.state[0].observation
        if env.done:
            break
        env.step([test_agent(obs), {"farmer": ["PASS"], "hands": [], "market": []}])

    print(f"\nFinal Farm Money: ${env.state[0].observation['farms'][0]['money']:.2f}")

if __name__ == "__main__":
    run()
