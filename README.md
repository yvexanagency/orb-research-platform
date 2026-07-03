# ORB Research Platform

A professional quantitative research framework for researching and optimizing Opening Range Breakout (ORB) strategies on Nasdaq Futures (NQ).

This project is designed as a modular quantitative research platform rather than a simple backtester. Every component has a single responsibility and is intended to support large-scale optimization, statistical analysis, robustness testing, and AI-assisted research.

> **Status:** Config system, extended risk-adjusted metrics, entry/risk
> variety (ATR stops, EMA filters, breakeven, trailing, close-confirm
> entries), and a working Random Search Optimizer have been added on top
> of the original baseline. See **[ROADMAP.md](ROADMAP.md)** for what's
> done, what's next, and known limitations.

---

# Goals

The long-term objective is to automatically discover robust ORB strategies using:

- Massive Random Search
- Bayesian Optimization
- Walk Forward Optimization
- Out-of-Sample Validation
- Monte Carlo Analysis
- Sensitivity Analysis
- Robustness Analysis
- Automatic Strategy Ranking

The architecture is intentionally designed so each module can be reused independently.

---

# Project Architecture

```
CSV

↓

Data Loader

↓

Indicators

↓

Strategy

↓

Entry Signals

↓

Simulator

↓

Completed Trades

↓

Equity Engine

↓

Metrics

↓

Backtest Result

↓

Optimizer
```

---

# Current Folder Structure

```
core/

    config.py
    data_loader.py
    indicators.py
    strategy.py
    entry_signal.py
    simulator.py
    trade.py
    equity.py
    equity_result.py
    metrics.py
    backtest_result.py
    backtester.py
    optimizer.py

main.py
ROADMAP.md
```

---

# Quickstart

```bash
pip install -r requirements.txt

# Single backtest using defaults (data/nq_1m.csv)
python main.py

# Single backtest with a custom config and data file
python main.py --config my_config.json --data data/nq_1m.csv

# Random search optimizer
python main.py --optimize --iterations 200 --rank-metric profit_factor
```

All tunables now live in `core/config.py` (`BacktestConfig`) instead of a
hardcoded `PARAMS` dict — see `ROADMAP.md` Phase 1 for details, and
`BacktestConfig.save()` / `.load()` for persisting a config to JSON.

---

# Module Responsibilities

## Data Loader

Responsible for:

- Loading CSV data
- Parsing timestamps
- Filtering Regular Trading Hours (configurable session window)
- Grouping candles by trading day

---

## Indicators

Computes all technical indicators.

Current indicators:

- EMA20
- EMA50
- EMA100
- EMA200
- ATR

Future indicators:

- VWAP
- Volume
- Daily statistics

---

## Strategy

Responsible only for detecting entries.

Responsibilities:

- Compute Opening Range
- Detect breakout (or close-confirmed breakout)
- Apply entry rules (direction, day-of-week, EMA filter, buffer)
- Return EntrySignal objects

Never manages exits.

---

## EntrySignal

Contains all information required to simulate a trade.

Includes:

- Trade
- Trading day dataframe
- Entry index
- Opening Range High
- Opening Range Low

---

## Simulator

Responsible only for trade execution.

Current features:

- Configurable Stop: OR Stop / ATR Stop / Fixed Stop
- Configurable Target: R-Multiple / ATR Target
- Break-even management
- ATR-based trailing stop
- End-of-Day Exit
- Conservative ambiguous candle handling

Computes:

- Exit price
- Exit time
- Exit reason
- Risk
- Reward
- PnL (points)
- PnL (USD)

---

## Trade

Represents a completed trade.

Stores:

- Entry
- Exit
- Stop
- Target
- Risk
- Reward
- PnL
- Exit reason

---

## Equity Engine

Builds the equity timeline.

Current responsibilities:

- Sort trades
- Build cumulative equity
- Compute drawdown
- Compute drawdown percentage

`core/metrics.py` additionally builds a calendar-aware daily equity series
for annualized statistics (Sharpe, CAGR, etc.) — see ROADMAP Phase 3.

---

## Metrics

Consumes the Equity Engine.

Current metrics:

- Total Trades
- Winners
- Losers
- Win Rate
- Gross Profit
- Gross Loss
- Net Profit
- Gross Profit Points
- Gross Loss Points
- Net Profit Points
- Profit Factor
- Average Trade
- Average Win
- Average Loss
- Expectancy
- Max Win
- Max Loss
- Consecutive Wins
- Consecutive Losses
- Sharpe Ratio
- Sortino Ratio
- CAGR
- Calmar Ratio
- Ulcer Index
- Recovery Factor
- Monthly Returns
- Yearly Returns

---

## Backtester

Coordinates the entire pipeline.

No business logic should live here.

Pipeline:

Strategy

↓

Simulator

↓

Metrics

↓

BacktestResult

---

## BacktestResult

Central result object.

Future modules should consume BacktestResult instead of raw trades whenever possible.

---

## Optimizer

Implemented: **Random Search** (`RandomSearchOptimizer` + `ParamSpace`).

Planned (stubbed in code, see ROADMAP Phase 5):

- Walk Forward
- Monte Carlo
- Bayesian Optimization
- Robustness Ranking

---

# Baseline Results (original dataset)

Dataset:

- NQ 1-minute data

Results:

- Trades: 729
- Win Rate: 53.22%
- Profit Factor: 1.13
- Net Profit: $66,760

Current execution model:

- OR Stop
- 1R Target
- End-of-Day Exit

> Note: `data/sample_synthetic.csv` in this repo is randomly generated for
> pipeline testing only — it does **not** reproduce the numbers above. Use
> your real NQ 1-minute CSV to reproduce or improve on this baseline.

---

# Design Principles

Every module must have one responsibility.

Strategy

Only finds entries.

Simulator

Only executes trades.

Equity

Only builds equity history.

Metrics

Only computes statistics.

Backtester

Only orchestrates.

Optimizer

Only searches parameter space.

---

# Long-Term Vision

See `ROADMAP.md` for the phased build-out. Summary of remaining scope:

## Entry

- ~~Opening Range Duration~~ ✅
- Touch Entry
- ~~Close Entry~~ ✅ (`close_confirm` mode)
- ~~Entry Buffer~~ ✅
- ~~Long Only~~ ✅
- ~~Short Only~~ ✅
- ~~Both Directions~~ ✅

## Filters

- ~~EMA20/50/100/200~~ ✅
- VWAP
- Volume
- ~~Day of Week~~ ✅
- Trading Session
- News Filter

## Risk Management

- ~~OR Stop~~ ✅
- ~~Fixed Stop~~ ✅
- ~~ATR Stop~~ ✅
- ~~Trailing Stop~~ ✅
- ~~Break Even~~ ✅
- Partial Exits
- Time Exit

## Optimization

- ~~Random Search~~ ✅
- Bayesian Optimization
- Walk Forward
- Monte Carlo
- Robustness Analysis

## Reporting

- Equity Curve
- Drawdown Curve
- ~~Monthly Returns~~ ✅ (raw data, no viz yet)
- ~~Annual Returns~~ ✅ (raw data, no viz yet)
- Heatmaps
- Trade Distribution
- Risk Metrics
- Export Reports
