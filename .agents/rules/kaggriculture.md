# Kaggriculture Project Rules & Guidelines

1. **Submission Constraints**:
   - `submission.py` must be completely self-contained. It cannot import project internal modules like `src.kaggriculture.*` because Kaggle's evaluation environment executes only `submission.py`.
   - Use `scripts/build_submission.py` to compile or inline the core policy into `submission.py`.

2. **Performance & Timeout Budget**:
   - Every agent decision must execute under 50ms (actTimeout default is 1.0s, banked overage is 60s).
   - Never perform unbounded loops or expensive BFS without depth limits.
   - Use Manhattan distance heuristics for path planning.

3. **Defensive Programming**:
   - Always wrap agent decision logic in a `try...except` block returning a fallback legal action (e.g. `{"farmer": ["PASS"], "hands": [], "market": []}`) to prevent crash disqualifications.
   - Always verify that the agent has enough money before placing `BUY_SEED` or `HIRE` orders.

4. **Testing and Verification**:
   - Every new agent or policy modification must be benchmarked via `scripts/arena.py` against `starter` before submission.
   - Full test suite in `tests/` must pass cleanly via `uv run pytest`.
