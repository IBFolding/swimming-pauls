# OpenClaw Self-Apply Fix Pack (Swimming Pauls)

This file is a handoff package you can give OpenClaw so it can apply/verify the same reliability fixes automatically.

---

## 1) What was fixed

### A. Pytest/import stability
- Added root-level `conftest.py` to ignore non-unit operational scripts:
  - `pre_launch_test.py`
  - `test_batch_prediction.py`
  - `test_capacity.py`
  - `test_client.py`
- Added top-level import compatibility in `__init__.py` so relative imports work when pytest imports `__init__` directly.

### B. Batch prediction source metadata + fallback hardening
- `skill_bridge.py`
  - Tracks `last_source_mode` for each batch:
    - `openclaw_cli`
    - `openrouter_kimi`
    - `mock`
    - `rule_fallback`
  - Added `batch_predict_with_meta(question, pauls)` returning:
    ```json
    {
      "predictions": [...],
      "source_mode": "..."
    }
    ```
  - Skill discovery fallback now returns `False` if checks fail.
- `local_agent.py`
  - Uses `batch_predict_with_meta`.
  - Returns `source_mode` in response payload.
  - Adds warning for fallback modes (`mock`, `rule_fallback`, `local_fallback`).
  - Saves structured `paul_votes` and consensus payload to prediction history DB.
  - Uses deterministic fallback generation when batch call fails.

### C. Portability fixes for pricing/resolution tools
- `resolve_predictions.py`
  - Removed hardcoded local path inserts.
  - Uses `PriceTracker.fetch_price(...)` instead of hardcoded script path subprocess calls.
- `price_tracker.py`
  - Script path resolution now uses:
    1. `CRYPTO_PRICE_SCRIPT` env var
    2. `~/.openclaw/workspace/skills/crypto-price/scripts/get_price_chart.py`
    3. `/opt/openclaw/skills/crypto-price/scripts/get_price_chart.py`
  - Emits clear warning if no script path is found.

### D. Test quality improvements
- `smoke_test.py`
  - Converted to pytest-friendly assertions.
  - Added helper checks for CLI run mode.
  - Version check now validates semantic version format (`x.y.z`) instead of hardcoded `2.1.0`.
  - Config check tolerates missing optional PyYAML.
- `test_report_agent.py`
  - Converted async test classes to `unittest.IsolatedAsyncioTestCase`.
  - Replaced manual loop plumbing with direct `await` usage.
- `rem_backfill.py`
  - Thought backfill timestamps constrained to `0..29` days to avoid timeline-window flakiness.

---

## 2) Commands OpenClaw should run after applying

```bash
python -m py_compile resolve_predictions.py price_tracker.py smoke_test.py test_report_agent.py
pytest -q
python smoke_test.py
```

Expected:
- `pytest -q` => pass (warnings may remain for optional libs).
- `python smoke_test.py` => pass (config may show optional PyYAML skip warning).

---

## 3) Runtime env OpenClaw should set

```bash
export CRYPTO_PRICE_SCRIPT=/absolute/path/to/get_price_chart.py
```

Optional (if using Kimi/OpenRouter):

```bash
export OPENROUTER_API_KEY=...
# or
export KIMI_API_KEY=...
```

---

## 4) Verification checklist

- [ ] API responses include `source_mode`.
- [ ] Fallback responses include `warning`.
- [ ] History records include `paul_votes` and structured consensus.
- [ ] No hardcoded machine-local script paths remain in resolver flow.
- [ ] Full pytest suite runs cleanly in CI.

---

## 5) Notes for deployment

- Keep Vercel for landing/static pages.
- Run backend workers (WebSocket agent, tracker, resolver) on persistent compute (VM/container).
- Track per-request token usage to estimate Gemini/Kimi cost accurately.

