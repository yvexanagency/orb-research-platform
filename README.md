# ORB Research Platform

A professional quantitative research framework for researching and optimizing Opening Range Breakout (ORB) strategies on Nasdaq Futures (NQ).

This project is designed as a modular quantitative research platform rather than a simple backtester. Every component has a single responsibility and is intended to support large-scale optimization, statistical analysis, robustness testing, and AI-assisted research.

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
```

---

# Module Responsibilities

## Data Loader

Responsible for:

- Loading CSV data
- Parsing timestamps
- Filtering Regular Trading Hours
- Grouping candles by trading day

---

## Indicators

Computes all technical indicators.

Current indicators:

- EMA20
- EMA50
- EMA100
- EMA200

Future indicators:

- VWAP
- ATR
- Volume
- Daily statistics

---

## Strategy

Responsible only for detecting entries.

Responsibilities:

- Compute Opening Range
- Detect breakout
- Apply entry rules
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

- OR Stop
- 1R Target
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

Future versions will support timestamped equity points.

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

Future metrics:

- CAGR
- Sharpe Ratio
- Sortino Ratio
- Calmar Ratio
- Recovery Factor
- MAR Ratio
- Ulcer Index
- Annual Returns
- Monthly Returns

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

Not yet implemented.

Will support:

- Random Search
- Bayesian Optimization
- Walk Forward
- Monte Carlo
- Robustness Ranking

---

# Current Baseline Results

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

The final platform will support:

## Entry

- Opening Range Duration
- Touch Entry
- Close Entry
- Entry Buffer
- Long Only
- Short Only
- Both Directions

## Filters

- EMA20
- EMA50
- EMA100
- EMA200
- VWAP
- Volume
- Day of Week
- Trading Session
- News Filter

## Risk Management

- OR Stop
- Fixed Stop
- ATR Stop
- Trailing Stop
- Break Even
- Partial Exits
- Time Exit

## Optimization

- Random Search
- Bayesian Optimization
- Walk Forward
- Monte Carlo
- Robustness Analysis

## Reporting

- Equity Curve
- Drawdown Curve
- Monthly Returns
- Annual Returns
- Heatmaps
- Trade Distribution
- Risk Metrics
- Export Reports