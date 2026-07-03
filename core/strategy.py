from core.entry_signal import EntrySignal
from core.trade import Trade


class ORBStrategy:
    """
    Detects entries only. Never manages exits (that's the Simulator's job).

    Entry modes:
      - "breakout"      original behavior: fill the instant price trades
                         beyond the OR level (+/- buffer_points).
      - "close_confirm": wait for a candle to CLOSE beyond the OR level,
                          then enter at the next bar's open.
    """

    def __init__(self, config):
        self.config = config
        self.entry_cfg = config.entry

    def run(self, df):
        signals = []

        or_minutes = self.entry_cfg.or_minutes
        expected_bars = self.config.session.expected_bars
        tolerance = self.config.min_session_bars_tolerance

        for date, day in df.groupby(df["timestamp ET"].dt.date):

            day = day.reset_index(drop=True)

            if len(day) < expected_bars - tolerance:
                continue

            if date.weekday() not in self.entry_cfg.allowed_days:
                continue

            opening_range = day.iloc[:or_minutes]

            or_high = float(opening_range["high"].max())
            or_low = float(opening_range["low"].min())

            signal = self._find_entry(date, day, or_minutes, or_high, or_low)

            if signal is not None:
                signals.append(signal)

        return signals

    def _find_entry(self, date, day, or_minutes, or_high, or_low):
        direction = self.entry_cfg.direction
        buffer = self.entry_cfg.buffer_points
        mode = self.entry_cfg.mode

        long_ok = direction in ("both", "long_only")
        short_ok = direction in ("both", "short_only")

        pending_break = None  # (side,) set by close_confirm mode, entered on the next bar

        for idx, candle in day.iloc[or_minutes:].iterrows():

            if mode == "close_confirm" and pending_break is not None:
                side = pending_break
                entry_price = float(candle["open"])

                if self._passes_ema_filter(candle, side):
                    return self._make_signal(date, day, idx, side, entry_price, or_high, or_low)

                pending_break = None
                continue

            if mode == "breakout":

                if long_ok and candle["high"] > or_high + buffer:
                    entry_price = or_high + buffer
                    if self._passes_ema_filter(candle, "LONG"):
                        return self._make_signal(date, day, idx, "LONG", entry_price, or_high, or_low)

                elif short_ok and candle["low"] < or_low - buffer:
                    entry_price = or_low - buffer
                    if self._passes_ema_filter(candle, "SHORT"):
                        return self._make_signal(date, day, idx, "SHORT", entry_price, or_high, or_low)

            elif mode == "close_confirm":

                if long_ok and candle["close"] > or_high + buffer:
                    pending_break = "LONG"
                elif short_ok and candle["close"] < or_low - buffer:
                    pending_break = "SHORT"

        return None

    def _passes_ema_filter(self, candle, side):
        if not self.entry_cfg.ema_filter_enabled:
            return True

        col = f"EMA_{self.entry_cfg.ema_filter_period}"
        if col not in candle:
            return True

        if side == "LONG":
            return candle["close"] > candle[col]
        return candle["close"] < candle[col]

    def _make_signal(self, date, day, idx, side, entry_price, or_high, or_low):
        trade = Trade(
            date=date,
            side=side,
            entry_time=day.loc[idx, "timestamp ET"],
            entry_price=entry_price,
        )

        return EntrySignal(
            trade=trade,
            day_data=day,
            entry_index=idx,
            or_high=or_high,
            or_low=or_low,
        )
