import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from submission_v16_apex_titan import _V43_ROUTES
route = _V43_ROUTES['default']
for s in range(215, 255):
    print(f"Step {s:3d}: Farmer={route[s].get('farmer')}")
