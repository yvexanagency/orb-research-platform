from core.entry_signal import EntrySignal
from core.trade import Trade


class Simulator:
    """
    Responsible only for trade execution. Given an EntrySignal, walks
    forward candle by candle applying the configured stop/target/management
    rules until an exit condition is hit (or End-of-Day).
    """

    def __init__(self, config):
        self.config = config
        self.risk_cfg = config.risk
        self.point_value = config.instrument.point_value

    def run(self, signal: EntrySignal) -> Trade:
        trade = signal.trade
        day = signal.day_data

        atr = self._get_atr(day, signal.entry_index)

        self._set_initial_stop_and_target(trade, signal, atr)
        self._simulate_path(trade, day, signal.entry_index, atr)
        self._finalize_pnl(trade)

        return trade

    def _get_atr(self, day, idx):
        if "ATR" not in day.columns:
            return 0.0
        value = day.loc[idx, "ATR"]
        return float(value) if value == value else 0.0  # NaN check

    def _set_initial_stop_and_target(self, trade, signal, atr):
        risk_cfg = self.risk_cfg
        is_long = trade.side == "LONG"

        stop_distance = None

        if risk_cfg.stop_mode == "atr" and atr > 0:
            stop_distance = atr * risk_cfg.atr_mult_stop
        elif risk_cfg.stop_mode == "fixed":
            stop_distance = risk_cfg.fixed_stop_points

        if stop_distance is None:
            # "or" mode (default / original behavior): stop at the opposite OR level
            trade.stop_loss = signal.or_low if is_long else signal.or_high
        else:
            trade.stop_loss = (
                trade.entry_price - stop_distance if is_long
                else trade.entry_price + stop_distance
            )

        trade.risk = (
            trade.entry_price - trade.stop_loss if is_long
            else trade.stop_loss - trade.entry_price
        )
        trade.risk = max(trade.risk, 1e-9)  # guard against zero/negative risk

        if risk_cfg.target_mode == "atr" and atr > 0:
            target_distance = atr * risk_cfg.atr_mult_target
        else:
            # "r_multiple" mode (default / original behavior: 1R)
            target_distance = trade.risk * risk_cfg.r_multiple

        trade.take_profit = (
            trade.entry_price + target_distance if is_long
            else trade.entry_price - target_distance
        )

    def _simulate_path(self, trade, day, entry_index, atr):
        is_long = trade.side == "LONG"
        breakeven_applied = False

        for _, candle in day.iloc[entry_index + 1:].iterrows():

            high = candle["high"]
            low = candle["low"]

            if self.risk_cfg.breakeven_enabled and not breakeven_applied:
                favorable_move = (high - trade.entry_price) if is_long else (trade.entry_price - low)
                if favorable_move / trade.risk >= self.risk_cfg.breakeven_trigger_r:
                    trade.stop_loss = trade.entry_price
                    breakeven_applied = True

            if self.risk_cfg.trailing_enabled and atr > 0:
                if is_long:
                    candidate_stop = high - atr * self.risk_cfg.trailing_atr_mult
                    trade.stop_loss = max(trade.stop_loss, candidate_stop)
                else:
                    candidate_stop = low + atr * self.risk_cfg.trailing_atr_mult
                    trade.stop_loss = min(trade.stop_loss, candidate_stop)

            if is_long:
                stop_hit = low <= trade.stop_loss
                target_hit = high >= trade.take_profit
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

    def _finalize_pnl(self, trade):
        if trade.side == "LONG":
            trade.pnl_points = trade.exit_price - trade.entry_price
        else:
            trade.pnl_points = trade.entry_price - trade.exit_price

        trade.pnl_dollars = trade.pnl_points * self.point_value

        if trade.risk > 0:
            trade.reward = trade.pnl_points / trade.risk
