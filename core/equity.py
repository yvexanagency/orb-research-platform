from core.equity_result import EquityResult


class EquityCurve:

    def build(self, trades, starting_capital: float = 0.0):
        """
        starting_capital shifts every point on the curve by a constant, so
        it doesn't change $ drawdown, but it fixes % drawdown: measuring
        against cumulative-PnL-from-zero (the old default) let drawdown %
        exceed 100% whenever a loss came before the equity curve had built
        up a meaningful peak. Pass the real starting capital to get a
        drawdown % that's actually bounded and comparable across runs.
        """

        trades = sorted(trades, key=lambda t: t.exit_time)

        equity = starting_capital
        peak = starting_capital

        equity_curve = []
        drawdown_curve = []
        drawdown_pct_curve = []

        max_drawdown = 0.0
        max_drawdown_pct = 0.0

        for trade in trades:

            equity += trade.pnl_dollars

            peak = max(peak, equity)

            drawdown = peak - equity

            if peak > 0:
                drawdown_pct = drawdown / peak * 100
            else:
                drawdown_pct = 0.0

            equity_curve.append(equity)
            drawdown_curve.append(drawdown)
            drawdown_pct_curve.append(drawdown_pct)

            if drawdown > max_drawdown:
                max_drawdown = drawdown
                max_drawdown_pct = drawdown_pct


        return EquityResult(
            trades=trades,

            equity_curve=equity_curve,
            drawdown_curve=drawdown_curve,
            drawdown_pct_curve=drawdown_pct_curve,

            final_equity=equity,
            peak_equity=peak,

            max_drawdown=max_drawdown,
            max_drawdown_pct=max_drawdown_pct,
        )
