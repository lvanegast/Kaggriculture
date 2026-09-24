import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
from scratch.test_rescue_detailed import a0, custom_a1

env = ke.make('kaggriculture', configuration={'seed': 7})
env.run([a0, custom_a1])
print('Status P0:', env.steps[-1][0]['status'])
print('Status P1:', env.steps[-1][1]['status'])
for s in range(191, 196):
    print(f"Step {s} P1: status={env.steps[s][1].get('status')}, error={env.steps[s][1].get('stderr')}")
