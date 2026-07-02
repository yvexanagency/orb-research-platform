from core.backtester import Backtester
from core.data_loader import load_data
from core.indicators import add_indicators
from core.metrics import Metrics

PARAMS = {
    "or_minutes": 15
}

df = load_data("data/nq_1m.csv")
df = add_indicators(df)

backtester = Backtester(df, PARAMS)
trades = backtester.run()

result = Metrics().calculate(trades)

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

