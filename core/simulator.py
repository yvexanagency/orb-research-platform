from core.entry_signal import EntrySignal
from core.trade import Trade


POINT_VALUE = 20.0  # NQ: $20 per point


class Simulator:

    def __init__(self, params):
        self.params = params

    def run(self, signal: EntrySignal) -> Trade:

        trade = signal.trade
        day = signal.day_data

        if trade.side == "LONG":
            trade.stop_loss = signal.or_low
            trade.risk = trade.entry_price - trade.stop_loss
            trade.take_profit = trade.entry_price + trade.risk
        else:
            trade.stop_loss = signal.or_high
            trade.risk = trade.stop_loss - trade.entry_price
            trade.take_profit = trade.entry_price - trade.risk

        for _, candle in day.iloc[signal.entry_index + 1:].iterrows():

            high = candle["high"]
            low = candle["low"]

            if trade.side == "LONG":

                stop_hit = low <= trade.stop_loss
                target_hit = high >= trade.take_profit

                if stop_hit and target_hit:
                    trade.exit_price = trade.stop_loss
                    trade.exit_reason = "AMBIGUOUS_STOP"
                elif stop_hit:
                    trade.exit_price = trade.stop_loss
                    trade.exit_reason = "STOP_LOSS"
                elif target_hit:
                    trade.exit_price = trade.take_profit
                    trade.exit_reason = "TAKE_PROFIT"
                else:
                    continue

            else:

                stop_hit = high >= trade.stop_loss
                target_hit = low <= trade.take_profit

                if stop_hit and target_hit:
                    trade.exit_price = trade.stop_loss
                    trade.exit_reason = "AMBIGUOUS_STOP"
                elif stop_hit:
                    trade.exit_price = trade.stop_loss
                    trade.exit_reason = "STOP_LOSS"
                elif target_hit:
                    trade.exit_price = trade.take_profit
                    trade.exit_reason = "TAKE_PROFIT"
                else:
                    continue

            trade.exit_time = candle["timestamp ET"]
            break

        if trade.exit_time is None:

            last = day.iloc[-1]

            trade.exit_time = last["timestamp ET"]
            trade.exit_price = float(last["close"])
            trade.exit_reason = "END_OF_DAY"

        if trade.side == "LONG":
            trade.pnl_points = trade.exit_price - trade.entry_price
        else:
            trade.pnl_points = trade.entry_price - trade.exit_price

        trade.pnl_dollars = trade.pnl_points * POINT_VALUE

        if trade.risk > 0:
            trade.reward = trade.pnl_points / trade.risk

        return trade