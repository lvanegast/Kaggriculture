import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaggle_environments as ke
import submission_v21_apex_sovereign_prime as s21

env = ke.make("kaggriculture", configuration={"seed": 42})
env.run([s21.agent, s21.agent])

# Inspect animal tiles on Day 15 (step 360)
obs = env.steps[360][0]["observation"]
farm = obs["farms"][obs["player"]]
tiles = farm["tiles"]

print("=== ANIMAL TILES AT STEP 360 (Seed 42) ===")
animal_tiles = []
for r in range(len(tiles)):
    for c in range(len(tiles[r])):
        t = tiles[r][c]
        if isinstance(t, dict) and "animal" in t:
            animal_tiles.append((r, c, t["animal"], t.get("fertilizer_available", False)))
            print(f"({r}, {c}): {t['animal']} | FertAvailable={t.get('fertilizer_available')} | YieldUnits={t.get('yield_units')}")

print(f"\nTotal Animals: {len(animal_tiles)}")

# Let's count how many times fertilizer_available is True across the entire game
total_fert_opportunities = 0
for step in range(len(env.steps)):
    o = env.steps[step][0]["observation"]
    f = o["farms"][o["player"]]
    for row in f["tiles"]:
        for tile in row:
            if isinstance(tile, dict) and "animal" in tile and tile.get("fertilizer_available"):
                total_fert_opportunities += 1

print(f"Total tile-steps where fertilizer_available was True: {total_fert_opportunities}")
