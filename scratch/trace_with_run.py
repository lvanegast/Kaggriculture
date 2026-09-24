import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
from scratch.eval_10seeds import load_agent

def trace_run(seed=7):
    a0_raw = load_agent("submission_v16_apex_titan.py")
    a1_raw = load_agent("submission_v16_apex_titan.py")
    
    divergences = []
    
    def agent0(obs, config=None):
        act = a0_raw(obs, config)
        step = obs.get("step", 0)
        return act
        
    def agent1(obs, config=None):
        act = a1_raw(obs, config)
        step = obs.get("step", 0)
        return act

    env = ke.make("kaggriculture", configuration={"seed": seed})
    env.run([a0_raw, a1_raw])
    
    # Now inspect all steps from env.steps
    print(f"Total steps in replay: {len(env.steps)}")
    diff_count = 0
    for i, s in enumerate(env.steps):
        act0 = s[0].get("action")
        act1 = s[1].get("action")
        # Compare actions
        if act0 != act1:
            diff_count += 1
            if diff_count <= 10:
                print(f"Step {i:3d} Diff:")
                print(f"  P0: {act0}")
                print(f"  P1: {act1}")
    print(f"Total step action differences: {diff_count}")

if __name__ == "__main__":
    trace_run(7)
