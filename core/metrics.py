from core.equity import EquityCurve
from core.backtest_result import BacktestResult


class Metrics:

    def calculate(self, trades):

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

        return BacktestResult(
            trades=trades,
            
            equity_curve=equity.equity_curve,
            drawdown_curve=equity.drawdown_curve,
            drawdown_pct_curve=equity.drawdown_pct_curve,

            final_equity=equity.final_equity,
            peak_equity=equity.peak_equity,

            max_drawdown=equity.max_drawdown,
            max_drawdown_pct=equity.max_drawdown_pct,

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
        )