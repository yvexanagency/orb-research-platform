from core.data_loader import load_data
from core.indicators import add_indicators
from core.backtester import Backtester

PARAMS = {
    "or_minutes": 15,
    "entry_type": "close",
    "entry_buffer": 0,
    "sl_type": "or",
    "sl_value": 1.0,
    "tp_rr": 2.0,
    "max_trades": 1,
    "vwap_filter": "none",
    "ema_filter": 0,
    "trade_side": "both",
}

df = load_data("data/nq_1m.csv")
df = add_indicators(df)

backtester = Backtester(df, PARAMS)
trades = backtester.run()

print(f"\nTrades: {len(trades)}")