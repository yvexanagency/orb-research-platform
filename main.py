import argparse

from core.backtester import Backtester
from core.config import BacktestConfig
from core.data_loader import load_data
from core.indicators import add_indicators
from core.metrics import Metrics
from core.optimizer import ParamSpace, RandomSearchOptimizer


def parse_args():
    parser = argparse.ArgumentParser(description="ORB Research Platform")
    parser.add_argument("--config", type=str, default=None, help="Path to a JSON config file")
    parser.add_argument("--data", type=str, default=None, help="Override the data CSV path")
    parser.add_argument("--optimize", action="store_true", help="Run the random search optimizer instead of a single backtest")
    parser.add_argument("--iterations", type=int, default=100, help="Random search iterations")
    parser.add_argument("--rank-metric", type=str, default="profit_factor", help="BacktestResult field to rank optimizer runs by")
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def fmt(value, suffix=""):
    return "n/a" if value is None else f"{value:.2f}{suffix}"


def print_summary(result):
    print("\n===== BACKTEST SUMMARY =====\n")

    print(f"Trades               : {result.total_trades}")
    print(f"Winners              : {result.winners}")
    print(f"Losers               : {result.losers}")
    print(f"Win Rate             : {result.win_rate:.2f}%")

    print()

    print(f"Net Profit ($)       : {result.net_profit:.2f}")
    print(f"Gross Profit ($)     : {result.gross_profit:.2f}")
    print(f"Gross Loss ($)       : {result.gross_loss:.2f}")

    print()

    print(f"Net Profit (pts)     : {result.net_profit_points:.2f}")
    print(f"Profit Factor        : {result.profit_factor:.2f}")
    print(f"Expectancy (R)       : {result.expectancy:.3f}")

    print()

    print(f"Average Trade ($)    : {result.average_trade:.2f}")
    print(f"Average Win ($)      : {result.average_win:.2f}")
    print(f"Average Loss ($)     : {result.average_loss:.2f}")

    print()

    print(f"Max Win ($)          : {result.max_win:.2f}")
    print(f"Max Loss ($)         : {result.max_loss:.2f}")

    print()

    print(f"Max Consecutive Wins : {result.consecutive_wins}")
    print(f"Max Consecutive Loss : {result.consecutive_losses}")

    print()

    print(f"Max Drawdown ($)     : {result.max_drawdown:.2f}")
    print(f"Max Drawdown (%)     : {result.max_drawdown_pct:.2f}%")
    print(f"Sharpe Ratio         : {fmt(result.sharpe)}")
    print(f"Sortino Ratio        : {fmt(result.sortino)}")
    print(f"CAGR                 : {fmt(result.cagr * 100 if result.cagr is not None else None, '%')}")
    print(f"Calmar Ratio         : {fmt(result.calmar)}")
    print(f"Ulcer Index          : {fmt(result.ulcer_index)}")
    print(f"Recovery Factor      : {fmt(result.recovery_factor)}")


def run_optimizer(df, config, args):
    # Default search space — reasonable starting ranges across entry timing,
    # stop/target mode, and R multiple. Edit freely or load a custom
    # ParamSpace; this is meant as a sane out-of-the-box example.
    param_space = ParamSpace({
        "entry.or_minutes": ("randint", 5, 30),
        "entry.buffer_points": ("uniform", 0.0, 5.0),
        "risk.stop_mode": ("choice", ["or", "atr", "fixed"]),
        "risk.r_multiple": ("uniform", 0.5, 3.0),
        "risk.atr_mult_stop": ("uniform", 0.5, 3.0),
    })

    optimizer = RandomSearchOptimizer(
        df, config, param_space,
        rank_metric=args.rank_metric,
        seed=args.seed,
    )

    top_results = optimizer.run(n_iter=args.iterations, verbose=True)

    print(f"\n===== TOP RESULTS (ranked by {args.rank_metric}) =====\n")

    for r in top_results[:10]:
        result = r["result"]
        print(
            f"#{r['rank']:>2}  score={r['score']:.3f}  "
            f"trades={result.total_trades}  net=${result.net_profit:,.0f}  "
            f"win_rate={result.win_rate:.1f}%  params={r['parameters']}"
        )


def main():
    args = parse_args()

    config = BacktestConfig.load(args.config) if args.config else BacktestConfig()
    if args.data:
        config.data_path = args.data

    df = load_data(config.data_path, config.session.start, config.session.end)
    df = add_indicators(df, atr_period=config.risk.atr_period)

    if args.optimize:
        run_optimizer(df, config, args)
        return

    trades = Backtester(df, config).run()
    result = Metrics().calculate(trades, starting_capital=config.instrument.starting_capital)
    print_summary(result)


if __name__ == "__main__":
    main()
