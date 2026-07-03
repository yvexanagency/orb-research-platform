# ORB Research Platform — Roadmap

This maps where the platform is, what just shipped, and what's next. Phases
are ordered by dependency, not by difficulty — each one unlocks the next.

---

## Phase 0 — Original Baseline (inherited)

- CSV → DataLoader → Indicators → Strategy → Simulator → Trade → Equity →
  Metrics → BacktestResult → Backtester pipeline, all working.
- Fixed OR-stop / 1R-target / EOD-exit ORB strategy.
- `core/optimizer.py` was an empty placeholder.
- `PARAMS` hardcoded in `main.py`, `requirements.txt` empty.

**Status: superseded by Phase 1.**

---

## Phase 1 — Foundation Fixes ✅ Done

- `requirements.txt` now pins `pandas` / `numpy`.
- New `core/config.py`: `BacktestConfig` (+ `InstrumentConfig`,
  `SessionConfig`, `EntryConfig`, `RiskConfig`) replaces the hardcoded
  `PARAMS` dict. Supports JSON save/load and `with_overrides()` for
  dot-path parameter overrides (`"risk.r_multiple": 2.0`).
- `SessionConfig.expected_bars` derives the "full trading day" bar count
  from session start/end instead of the old hardcoded `391`. A
  `min_session_bars_tolerance` knob allows partial/holiday sessions.
- `data_loader.load_data()` takes session start/end as parameters instead
  of hardcoding RTH bounds.
- `main.py` rewritten with `argparse`: `--config`, `--data`, `--optimize`,
  `--iterations`, `--rank-metric`, `--seed`.
- `POINT_VALUE` moved off the Simulator and into `InstrumentConfig`
  (per-instrument, not hardcoded to NQ).

---

## Phase 2 — Entry & Risk Variety ✅ Done

**Strategy (`core/strategy.py`)**
- `entry.mode`: `"breakout"` (original, fill at OR level) or
  `"close_confirm"` (wait for a candle to *close* beyond the OR level,
  enter next bar's open — removes some of the optimistic-fill assumption
  the original breakout fill had).
- `entry.buffer_points`: require price to clear the OR level by a buffer
  before triggering (reduces noise-driven false breaks).
- `entry.direction`: `both` / `long_only` / `short_only`.
- `entry.allowed_days`: day-of-week filter.
- `entry.ema_filter_enabled` + `entry.ema_filter_period`: only take LONGs
  above / SHORTs below the chosen EMA — this is the first of the
  README's "Filters" section actually wired up (EMA20/50/100/200 were
  computed but unused before).

**Simulator (`core/simulator.py`)**
- `risk.stop_mode`: `"or"` (original), `"atr"`, or `"fixed"`.
- `risk.target_mode`: `"r_multiple"` (original, default 1R) or `"atr"`.
- `risk.breakeven_enabled` / `breakeven_trigger_r`: move stop to entry
  once price has moved N·R in favor.
- `risk.trailing_enabled` / `trailing_atr_mult`: ATR-based trailing stop.
- New `ATR` column added in `core/indicators.py` to support all of the above.

All new behavior defaults to the *original* logic (`stop_mode="or"`,
`target_mode="r_multiple"`, `r_multiple=1.0`, filters/management off), so
existing results are reproducible unless you opt into the new features.

---

## Phase 3 — Extended Metrics ✅ Done

`core/metrics.py` now builds a **timestamped daily equity curve** (grouping
trades by `exit_time.date()`), which was needed for anything annualized —
previously equity only existed as a trade-sequence, not a calendar-aware
series.

Added to `BacktestResult`:
- `sharpe`, `sortino` (annualized, 252 trading days)
- `cagr` (from the daily equity curve's start/end dates)
- `calmar` (`cagr / max_drawdown_pct`)
- `ulcer_index`
- `recovery_factor` (`net_profit / max_drawdown`)
- `monthly_returns`, `yearly_returns` (dicts, dollar PnL bucketed by
  calendar period)

All of these return `None` gracefully on insufficient data (e.g. Sharpe
needs ≥2 daily observations) instead of raising or returning bogus zeros.

---

## Phase 4 — Optimizer: Random Search ✅ Done

`core/optimizer.py`:
- `ParamSpace`: declarative parameter space over dot-path config keys
  (`choice` / `uniform` / `randint` samplers).
- `RandomSearchOptimizer`: samples `n_iter` configs, runs a full backtest
  per sample via the existing `Backtester`, filters out runs with too few
  trades (`min_trades`) to avoid ranking noise, ranks by any
  `BacktestResult` field (`profit_factor`, `sharpe`, `net_profit`, ...),
  returns the top N with full metrics attached.
- Wired into `main.py` via `--optimize --iterations N --rank-metric X`.

This is the "Massive Random Search" goal from the README — the first of
the five optimization methods it lists.

Stubbed (raise `NotImplementedError` with a pointer here) so the intended
architecture is visible in the module even before they exist:
`BayesianOptimizer`, `WalkForwardOptimizer`, `MonteCarloAnalyzer`.

---

## Phase 5 — Planned Next (not yet built)

Roughly in priority order:

1. **Walk-Forward Optimization** — the highest-value next step. Split the
   date range into rolling in-sample/out-of-sample windows, optimize on
   IS, validate on OOS, and report the OOS-only aggregate metrics. This is
   what turns "we found good parameters" into "these parameters generalize."
   Depends on: `RandomSearchOptimizer` (done) + a date-range slicer on `df`.

2. **Monte Carlo Analysis** — trade-sequence resampling (bootstrap) on a
   given `BacktestResult.trades` list to get a distribution of possible
   equity curves / drawdowns / final-equity outcomes, not just one path.
   Useful for answering "how lucky was this backtest?"

3. **Bayesian Optimization** — replace/augment Random Search with a
   surrogate-model-guided search (e.g. Optuna's TPE) once the search space
   grows large enough that random sampling becomes inefficient.

4. **Robustness / Sensitivity Analysis + Ranking** — perturb each winning
   parameter set by small amounts and check metric stability across the
   neighborhood; penalize fragile peaks. Natural home:
   `BacktestResult.robustness_score` (field already exists, unused).

5. **More entry logic**: touch-entry (limit order at OR level rather than
   stop-style breakout), entry timeout (cancel if no breakout within N
   minutes), volume filter, VWAP filter, news/econ-calendar filter.

6. **More risk management**: partial exits / scale-outs, time-based exit
   (close after N minutes regardless of P&L), multiple concurrent
   stop-loss models blended.

7. **Reporting layer**: equity curve / drawdown curve plots, monthly
   returns heatmap, trade distribution histograms, HTML/PDF report export.
   Currently `monthly_returns` / `yearly_returns` are computed but only
   consumable as raw dicts — no visualization yet.

8. **Multi-instrument support**: `InstrumentConfig` already generalizes
   point value / tick size, but `data_loader` and `strategy` haven't been
   tested against anything but NQ-shaped 1-minute data.

9. **Test suite**: no automated tests exist yet for `core/`. Given the
   platform's entire value is trustworthy statistics feeding an optimizer,
   this should probably happen before Phase 5.1 (Walk-Forward), not after —
   an optimizer will happily overfit to a Simulator bug if nothing catches it.

---

## Known limitations to keep in mind

- **Fill assumption**: `entry.mode="breakout"` fills exactly at the OR
  level with no slippage — optimistic. `close_confirm` mode is more
  conservative (waits for a confirmed close + next-bar-open fill) but
  still has no slippage/commission model. Worth adding a
  `slippage_ticks` / `commission_per_trade` config field before trusting
  net-profit numbers at scale.
- **Random search validity**: results in this phase are found via
  in-sample optimization only — no out-of-sample validation yet
  (that's Phase 5.1). Treat "top result" tables as candidates to validate,
  not conclusions.
- **Synthetic test data**: the current `data/nq_1m.csv` used to validate
  this round of changes is randomly generated for testing purposes — it is
  NOT the real dataset behind the README's "729 trades, $66,760 net
  profit" baseline. Drop your real NQ 1-minute CSV in `data/` before
  drawing conclusions from any run.


