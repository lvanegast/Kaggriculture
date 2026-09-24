import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scratch.find_exception import env
print("Total steps:", len(env.steps))
for s in range(190, 200):
    st0 = env.steps[s][0]['status']
    st1 = env.steps[s][1]['status']
    r0 = env.steps[s][0].get('reward')
    r1 = env.steps[s][1].get('reward')
    print(f"Step {s:3d}: P0 status={st0} reward={r0} | P1 status={st1} reward={r1}")
