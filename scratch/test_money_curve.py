import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
from scratch.test_rescue_detailed import a0, custom_a1
env = ke.make('kaggriculture', configuration={'seed': 7})
env.run([a0, custom_a1])
for step in (190, 195, 200, 205, 210, 220, 250, 300, 500, 719):
    s = env.steps[step]
    m0 = s[0]['observation']['farms'][0]['money']
    m1 = s[1]['observation']['farms'][1]['money']
    print(f"Step {step}: P0=${m0:.0f}, P1=${m1:.0f}")
