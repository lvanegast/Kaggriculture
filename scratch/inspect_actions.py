import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from submission_v16_apex_titan import _V43_POLICY

child = _V43_POLICY.children['default']
closures = [c.cell_contents for c in child.__closure__]
for c in closures:
    if callable(c) and hasattr(c, '__closure__') and c.__closure__:
        sub = [s.cell_contents for s in c.__closure__]
        for item in sub:
            if isinstance(item, list) and len(item) > 100:
                print('Found actions list length:', len(item))
                for s in range(180, 215):
                    act = item[s]
                    print(f"Step {s:3d}: Farmer={act.get('farmer')} | Market={act.get('market')}")
                break
