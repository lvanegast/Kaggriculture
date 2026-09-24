import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scratch.find_exception import env
print("Final step P0:", env.steps[-1][0].get('reward'), env.steps[-1][0]['observation']['farms'][0]['money'])
print("Final step P1:", env.steps[-1][1].get('reward'), env.steps[-1][1]['observation']['farms'][1]['money'])
