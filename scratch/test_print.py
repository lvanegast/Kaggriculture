import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
from scratch.eval_10seeds import load_agent

a1 = load_agent("submission_v16_apex_titan.py")
def debug_a1(obs, config=None):
    step = obs.get("step") if isinstance(obs, dict) else getattr(obs, "step", None)
    act = a1(obs, config)
    if step in (192, 193, 194):
        sys.stderr.write(f"P1 Step {step} Act: {act.get('farmer')}\n")
    return act

env = ke.make("kaggriculture", configuration={"seed": 7})
env.run([load_agent("submission_v16_apex_titan.py"), debug_a1])
