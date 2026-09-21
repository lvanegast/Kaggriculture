"""
Diagnostics for Ranch Hybrid.
"""
import kaggle_environments as ke
from test_ranch_hybrid import agent

def diagnose():
    env = ke.make("kaggriculture")
    env.reset()
    
    # Track daily earnings
    daily_stats = []
    
    for step in range(720):
        obs = env.state[0].observation
        day = obs.get("day", 0)
        hour = obs.get("hour", 0)
        
        # Run step
        act0 = agent(obs)
        act1 = {"farmer": ["PASS"], "hands": [], "market": []}
        env.step([act0, act1])
        
        farm = env.state[0].observation["farms"][0]
        priv = env.state[0].observation["private"]
        
        if hour == 23:
            pt1 = farm["tiles"][4][5]
            pt2 = farm["tiles"][3][5]
            pt1_y = pt1.get("yield_units") if isinstance(pt1, dict) else -1
            pt2_y = pt2.get("yield_units") if isinstance(pt2, dict) else -1
            print(f"Day {day:2d} End: Money=${farm['money']:.0f} | Cow1 yield={pt1_y} fed={pt1.get('fed_today')} | Cow2 yield={pt2_y} fed={pt2.get('fed_today')} | Hands={len(farm['hands'])}")

    print(f"\nFinal Cash: ${farm['money']:.2f}")

if __name__ == "__main__":
    diagnose()
