"""
Telemetry and bottleneck analysis for FarmBrain v12.
"""
import sys
sys.path.append(".")
import kaggle_environments as ke
import submission_v12_ranch_apex as v12


def analyze():
    env = ke.make("kaggriculture")
    env.reset()
    
    total_sales = {}
    milk_events = 0
    fert_events = 0
    
    for step in range(720):
        obs = env.state[0].observation
        day = obs.get("day", 0)
        hour = obs.get("hour", 0)
        
        act0 = v12.agent(obs)
        for order in act0.get("market", []):
            if order[0] == "SELL":
                item, qty = order[1], order[2]
                total_sales[item] = total_sales.get(item, 0) + qty
                
        env.step([act0, {"farmer": ["PASS"], "hands": [], "market": []}])
        
        if env.done:
            break
            
    farm = env.state[0].observation["farms"][0]
    print("=== V12 PERFORMANCE TELEMETRY ===")
    print(f"Final Cash: ${farm['money']:.2f}")
    print("Total Units Sold:")
    for k, v in sorted(total_sales.items()):
        print(f"  {k}: {v} units")
    print("================================")

if __name__ == "__main__":
    analyze()
