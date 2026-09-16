---
name: kaggriculture
description: >-
  Workflows, simulation arena, and agent evaluation tools for the Kaggle Kaggriculture competition.
  Use when running 1v1 matches, benchmarking agents, tuning economic policies, or generating submission.py.
---

# Kaggriculture Competition Skill

This skill provides step-by-step procedures for developing, benchmarking, and packaging competitive agents for the Kaggle **Kaggriculture** simulation challenge.

## Core Workflows

### 1. Run Head-to-Head Tournament (Arena)
To evaluate any two agents against each other over $N$ matches (swapping Player 0 and Player 1):
```bash
uv run python scripts/arena.py --agent1 greedy --agent2 starter --games 20
```
Key metrics reported:
- **Win Rate (%)**: Proportion of games where Agent 1 accumulated higher final cash.
- **Mean Net Worth**: Average money at turn 720.
- **Margin of Victory**: Average score delta.

### 2. Validate and Build Submission
Package the current top policy into a standalone `submission.py` with zero external dependencies and verify it on a complete 720-step episode:
```bash
uv run python scripts/build_submission.py --verify
```

### 3. Run Test Suite
```bash
uv run pytest -v
```

## Game Mechanics Quick Reference
- **Horizon**: 30 in-game days, 24 turns/day = **720 turns**.
- **Board**: 10x10 grid (initial 5x5 quadrant unlocked).
- **Crops**:
  - `WHEAT` (seed: 10, matures day 4, yield: 6, one-off)
  - `CARROT` (seed: 20, matures day 3, yield: 4, one-off)
  - `TOMATO` (seed: 50, first yield day 8, interval 1, yield: 4, multi-harvest)
  - `STRAWBERRY` (seed: 100, first yield day 10, interval 2, yield: 4, multi-harvest)
  - `MELON` (seed: 80, matures day 12, yield: 6, one-off)
- **Market Elasticity**: Selling large batches devalues prices. Sell progressively or diversify products to maximize yield per unit.
- **Labor Scaling**: Hiring hands costs Fibonacci sequence multiplier. Hire early if ROI payback turns < remaining turns.
