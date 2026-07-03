import math
from collections import defaultdict

from core.equity import EquityCurve
from core.backtest_result import BacktestResult

TRADING_DAYS_PER_YEAR = 252


class Metrics:

    def calculate(self, trades, starting_capital: float = 100_000.0):

        total_trades = len(trades)
        equity = EquityCurve().build(trades)

        winners = [t for t in trades if t.pnl_dollars > 0]
        losers = [t for t in trades if t.pnl_dollars <= 0]

        gross_profit = sum(t.pnl_dollars for t in winners)
        gross_loss = abs(sum(t.pnl_dollars for t in losers))

        gross_profit_points = sum(t.pnl_points for t in winners)
        gross_loss_points = abs(sum(t.pnl_points for t in losers))

        net_profit = gross_profit - gross_loss
        net_profit_points = gross_profit_points - gross_loss_points

        win_rate = (
            len(winners) / total_trades * 100
            if total_trades
            else 0.0
        )

        profit_factor = (
            gross_profit / gross_loss
            if gross_loss > 0
            else float("inf")
        )

        average_trade = (
            net_profit / total_trades
            if total_trades
            else 0.0
        )

        average_win = (
            gross_profit / len(winners)
            if winners
            else 0.0
        )

        average_loss = (
            gross_loss / len(losers)
            if losers
            else 0.0
        )

        expectancy = (
            sum(t.reward for t in trades) / total_trades
            if total_trades
            else 0.0
        )

        max_win = max((t.pnl_dollars for t in trades), default=0.0)
        max_loss = min((t.pnl_dollars for t in trades), default=0.0)

        consecutive_wins = 0
        consecutive_losses = 0

        current_wins = 0
        current_losses = 0

        for trade in trades:

            if trade.pnl_dollars > 0:
                current_wins += 1
                current_losses = 0
            else:
                current_losses += 1
                current_wins = 0

            consecutive_wins = max(consecutive_wins, current_wins)
            consecutive_losses = max(consecutive_losses, current_losses)

        # ---- Timestamped equity / annualized & risk-adjusted metrics ----

        daily_pnl = _daily_pnl_series(trades)
        daily_equity = _build_daily_equity(daily_pnl, starting_capital)
        daily_returns = _daily_returns(daily_equity, starting_capital)

        sharpe = _sharpe(daily_returns)
        sortino = _sortino(daily_returns)
        cagr = _cagr(daily_equity, starting_capital)
        ulcer_index = _ulcer_index(daily_equity)

        recovery_factor = (
            net_profit / equity.max_drawdown
            if equity.max_drawdown > 0
            else None
        )

        calmar = (
            cagr / (equity.max_drawdown_pct / 100)
            if cagr is not None and equity.max_drawdown_pct > 0
            else None
        )

        monthly_returns, yearly_returns = _monthly_yearly_returns(daily_pnl)

        return BacktestResult(
            trades=trades,

            equity_curve=equity.equity_curve,
            drawdown_curve=equity.drawdown_curve,
            drawdown_pct_curve=equity.drawdown_pct_curve,

            final_equity=equity.final_equity,
            peak_equity=equity.peak_equity,

            max_drawdown=equity.max_drawdown,
            max_drawdown_pct=equity.max_drawdown_pct,

            starting_capital=starting_capital,

            total_trades=total_trades,
            winners=len(winners),
            losers=len(losers),
            win_rate=win_rate,

            gross_profit=gross_profit,
            gross_loss=gross_loss,
            net_profit=net_profit,

            gross_profit_points=gross_profit_points,
            gross_loss_points=gross_loss_points,
            net_profit_points=net_profit_points,

            profit_factor=profit_factor,
            expectancy=expectancy,

            average_trade=average_trade,
            average_win=average_win,
            average_loss=average_loss,

            max_win=max_win,
            max_loss=max_loss,

            consecutive_wins=consecutive_wins,
            consecutive_losses=consecutive_losses,

            sharpe=sharpe,
            sortino=sortino,
            calmar=calmar,
            cagr=cagr,
            ulcer_index=ulcer_index,
            recovery_factor=recovery_factor,

            monthly_returns=monthly_returns,
            yearly_returns=yearly_returns,
        )


# ---------------------------------------------------------------------------
# Helpers - timestamped equity + annualized statistics.
# Kept as module-level functions (pure, stateless) rather than methods so
# they're independently testable and reusable by the Optimizer/Monte Carlo
# modules later.
# ---------------------------------------------------------------------------

def _daily_pnl_series(trades):
    daily = defaultdict(float)
    for t in trades:
        if t.exit_time is None:
            continue
        d = t.exit_time.date() if hasattr(t.exit_time, "date") else t.exit_time
        daily[d] += t.pnl_dollars
    return dict(sorted(daily.items()))


def _build_daily_equity(daily_pnl, starting_capital):
    equity = starting_capital
    curve = {}
    for date, pnl in daily_pnl.items():
        equity += pnl
        curve[date] = equity
    return curve


def _daily_returns(daily_equity, starting_capital):
    values = [starting_capital] + list(daily_equity.values())
    returns = []
    for i in range(1, len(values)):
        prev = values[i - 1]
        returns.append((values[i] - prev) / prev if prev != 0 else 0.0)
    return returns


def _sharpe(returns):
    if len(returns) < 2:
        return None
    mean = sum(returns) / len(returns)
    variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
    std = math.sqrt(variance)
    if std == 0:
        return None
    return (mean / std) * math.sqrt(TRADING_DAYS_PER_YEAR)


def _sortino(returns):
    if len(returns) < 2:
        return None
    mean = sum(returns) / len(returns)
    downside = [r for r in returns if r < 0]
    if not downside:
        return None
    downside_std = math.sqrt(sum(r ** 2 for r in downside) / len(downside))
    if downside_std == 0:
        return None
    return (mean / downside_std) * math.sqrt(TRADING_DAYS_PER_YEAR)


def _cagr(daily_equity, starting_capital):
    if not daily_equity:
        return None
    dates = list(daily_equity.keys())
    years = (dates[-1] - dates[0]).days / 365.25
    if years <= 0:
        return None
    final_equity = list(daily_equity.values())[-1]
    if starting_capital <= 0 or final_equity <= 0:
        return None
    return (final_equity / starting_capital) ** (1 / years) - 1


def _ulcer_index(daily_equity):
    values = list(daily_equity.values())
    if not values:
        return None
    peak = values[0]
    squared_dd = []
    for v in values:
        peak = max(peak, v)
        dd_pct = (peak - v) / peak * 100 if peak > 0 else 0.0
        squared_dd.append(dd_pct ** 2)
    return math.sqrt(sum(squared_dd) / len(squared_dd))


def _monthly_yearly_returns(daily_pnl):
    monthly = defaultdict(float)
    yearly = defaultdict(float)
    for date, pnl in daily_pnl.items():
        monthly[f"{date.year}-{date.month:02d}"] += pnl
        yearly[str(date.year)] += pnl
    return dict(monthly), dict(yearly)
