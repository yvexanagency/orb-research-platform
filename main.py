from core.data_loader import load_data
from core.indicators import add_indicators
from core.backtester import Backtester

PARAMS = {
    "or_minutes": 15,
}

df = load_data("data/nq_1m.csv")
df = add_indicators(df)

backtester = Backtester(df, PARAMS)
trades = backtester.run()

print(f"\nTotal Trades: {len(trades)}")

for trade in trades[:20]:
    print(trade)