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
        
        pt = farm["tiles"][4][5]
        
        # Day 0 setup
        if day == 0:
            if step == 0:
                market = [["BUY_LAND"], ["BUY_ANIMAL", "COW", 1], ["BUY_PRODUCT", "WHEAT", 10]]
                farmer = ["EAST"] # move to (5,4)
            elif step == 1:
                farmer = ["BUILD_PASTURE"] # at (5,4)
            elif step == 2:
                farmer = ["PICKUP", "COW", 1]
            elif step == 3:
                farmer = ["PLACE", "COW"]
            elif step == 4:
                farmer = ["PICKUP", "WHEAT", 1]
            elif step == 5:
                farmer = ["FEED"]
            elif step == 6:
                farmer = ["CARE"]
            elif step == 7:
                farmer = ["WEST"] # return to (4,4)
        else:
            # Daily routine for farmer:
            # Morning: if wheat < 5 in shed, buy wheat
            if hour == 0 and shed.get("WHEAT", 0) < 5 and money > 150:
                market.append(["BUY_PRODUCT", "WHEAT", 5])
            
            # Sell any milk or fertilizer in shed
            if shed.get("MILK", 0) > 0:
                market.append(["SELL", "MILK", shed["MILK"]])
            if shed.get("FERTILIZER", 0) > 0:
                market.append(["SELL", "FERTILIZER", shed["FERTILIZER"]])
                
            # Farmer tasks:
            # If at (4,4) and cow needs attention today:
            cow_needs_attention = pt and isinstance(pt, dict) and "animal" in pt and (
                not pt.get("fed_today") or not pt.get("cared_today") or pt.get("fertilizer_available") or pt.get("yield_units", 0) > 0
            )
            
            if (fx, fy) == (4, 4) and cow_needs_attention:
                farmer = ["EAST"] # move to pasture at (5,4)
            elif (fx, fy) == (5, 4):
                if pt.get("fertilizer_available"):
                    farmer = ["COLLECT_FERTILIZER"]
                elif pt.get("yield_units", 0) > 0:
                    farmer = ["HARVEST"]
                elif not pt.get("fed_today"):
                    if inv.get("WHEAT", 0) > 0:
                        farmer = ["FEED"]
                    elif shed.get("WHEAT", 0) > 0:
                        farmer = ["PICKUP", "WHEAT", 1]
                elif not pt.get("cared_today"):
                    farmer = ["CARE"]
                elif any(v > 0 for v in inv.values()):
                    farmer = ["DROP"]
                else:
                    # Cow is fully tended today! Move back to (4,4)
                    farmer = ["WEST"]

        if hour == 23:
            print(f"Day {day:2d} End: Money=${farm['money']:.0f}, Shed Milk={shed.get('MILK',0)}, Fert={shed.get('FERTILIZER',0)}, Pt yield={pt.get('yield_units',0) if pt and isinstance(pt,dict) else 0}")

        return {"farmer": farmer, "hands": [], "market": market}

    env.step([test_agent(env.state[0].observation), {"farmer": ["PASS"], "hands": [], "market": []}])
    for _ in range(719):
        obs = env.state[0].observation
        env.step([test_agent(obs), {"farmer": ["PASS"], "hands": [], "market": []}])

    print(f"\nFinal Farm Money: ${env.state[0].observation['farms'][0]['money']:.2f}")



if __name__ == "__main__":
    run()
