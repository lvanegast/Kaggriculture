import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
from scratch.eval_10seeds import load_agent

def trace_cows():
    env = ke.make("kaggriculture", configuration={"seed": 7})
    a0 = load_agent("submission_v16_apex_titan.py")
    a1 = load_agent("submission_v16_apex_titan.py")
    
    # We step turn by turn
    obs0 = env.reset()[0]["observation"]
    obs1 = env.state[1]["observation"]
    
    for step in range(215):
        act0 = a0(obs0)
        act1 = a1(obs1)
        
        env.step([act0, act1])
        obs0 = env.state[0]["observation"]
        obs1 = env.state[1]["observation"]
        
        p0_shed = obs0["private"]["shed"].get("COW", 0)
        p1_shed = obs1["private"]["shed"].get("COW", 0)
        
        if 185 <= step <= 205:
            print(f"Step {step:3d}:")
            print(f"  P0 Farmer={act0.get('farmer')} | Shed Cows={p0_shed} | Hands={len(act0.get('hands', []))}")
            print(f"  P1 Farmer={act1.get('farmer')} | Shed Cows={p1_shed} | Hands={len(act1.get('hands', []))}")
            if act0.get('farmer') != act1.get('farmer'):
                print(f"  *** DIVERGENCE at Step {step} ***")

if __name__ == "__main__":
    trace_cows()
