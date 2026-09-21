import kaggle_environments as ke

def run_test():
    # Test step-by-step cow lifecycle in kaggle-environments
    env = ke.make("kaggriculture")

    # Let's inspect how BUY_PRODUCT, BUY_ANIMAL, BUILD_PASTURE, PLACE work
    def test_agent(obs, config=None):
        step = obs.get("step", 0)
        day = obs.get("day", 0)
        hour = obs.get("hour", 0)
        farm = obs["farms"][obs["player"]]
        private = obs["private"]
        shed = private.get("shed", {})
        fx, fy = farm["farmer"]
        inv = private["inventories"][0]

        market_orders = []
        farmer_action = ["PASS"]

        # Step 0: Build Pasture at (3, 4)
        if step == 0:
            farmer_action = ["WEST"] # move to (3,4)
            market_orders = [
                ["BUY_LAND"], # Buy NE
                ["BUY_ANIMAL", "COW", 1],
                ["BUY_PRODUCT", "WHEAT", 5]
            ]
        elif step == 1:
            farmer_action = ["BUILD_PASTURE"]
        elif step == 2:
            farmer_action = ["EAST"] # move to (4,4) shed
        elif step == 3:
            farmer_action = ["PICKUP", "COW", 1]
        elif step == 4:
            farmer_action = ["WEST"] # move to (3,4) pasture
        elif step == 5:
            farmer_action = ["PLACE", "COW"]
        elif step == 6:
            farmer_action = ["EAST"] # move to (4,4) shed
        elif step == 7:
            farmer_action = ["PICKUP", "WHEAT", 1]
        elif step == 8:
            farmer_action = ["WEST"] # move to pasture
        elif step == 9:
            farmer_action = ["FEED"]
        elif step == 10:
            farmer_action = ["CARE"]
        else:
            # Check pasture tile state
            pt = farm["tiles"][4][3]
            if step == 11:
                print(f"Pasture tile at step 11: {pt}")
                print(f"Farm money: {farm['money']}")
                print(f"Shed: {shed}")
                print(f"Unlocked: {farm.get('unlocked_quadrants')}")

        return {"farmer": farmer_action, "hands": [], "market": market_orders}

    env.step([test_agent(env.state[0].observation), {"farmer": ["PASS"], "hands": [], "market": []}])
    for _ in range(12):
        obs = env.state[0].observation
        act = test_agent(obs)
        env.step([act, {"farmer": ["PASS"], "hands": [], "market": []}])

if __name__ == "__main__":
    run_test()
