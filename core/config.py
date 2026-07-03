"""
Central configuration for the ORB Research Platform.

Replaces the old hardcoded PARAMS dict in main.py. Every tunable knob for
the instrument, session, entry logic, and risk management lives here so the
Optimizer can sample it and every module has a single source of truth.
"""

from __future__ import annotations

import copy
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime


@dataclass
class InstrumentConfig:
    symbol: str = "NQ"
    point_value: float = 20.0      # $ per point, per contract
    tick_size: float = 0.25
    starting_capital: float = 100_000.0  # notional capital, used for % based metrics


@dataclass
class SessionConfig:
    start: str = "09:30"
    end: str = "16:00"
    bar_minutes: int = 1

    @property
    def expected_bars(self) -> int:
        """Number of bars a full session should contain, derived instead of hardcoded."""
        fmt = "%H:%M"
        start = datetime.strptime(self.start, fmt)
        end = datetime.strptime(self.end, fmt)
        minutes = (end - start).total_seconds() / 60
        return int(minutes / self.bar_minutes) + 1


@dataclass
class EntryConfig:
    or_minutes: int = 15

    # breakout       -> fill at OR level (+/- buffer) the instant it's broken (original behavior)
    # close_confirm  -> wait for a candle to CLOSE beyond the OR level, enter at next bar's open
    mode: str = "breakout"
    buffer_points: float = 0.0

    direction: str = "both"  # both | long_only | short_only

    allowed_days: list = field(default_factory=lambda: [0, 1, 2, 3, 4])  # 0=Mon..4=Fri

    ema_filter_enabled: bool = False
    ema_filter_period: int = 50  # must be one of 20/50/100/200


@dataclass
class RiskConfig:
    stop_mode: str = "or"      # or | atr | fixed
    atr_period: int = 14
    atr_mult_stop: float = 1.5
    fixed_stop_points: float = 20.0

    target_mode: str = "r_multiple"  # r_multiple | atr
    r_multiple: float = 1.0
    atr_mult_target: float = 2.0

    breakeven_enabled: bool = False
    breakeven_trigger_r: float = 1.0

    trailing_enabled: bool = False
    trailing_atr_mult: float = 1.0


@dataclass
class BacktestConfig:
    data_path: str = "data/nq_1m.csv"
    instrument: InstrumentConfig = field(default_factory=InstrumentConfig)
    session: SessionConfig = field(default_factory=SessionConfig)
    entry: EntryConfig = field(default_factory=EntryConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)

    # allow N missing bars vs the theoretical session length before a day is dropped
    min_session_bars_tolerance: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "BacktestConfig":
        return BacktestConfig(
            data_path=d.get("data_path", "data/nq_1m.csv"),
            instrument=InstrumentConfig(**d.get("instrument", {})),
            session=SessionConfig(**d.get("session", {})),
            entry=EntryConfig(**d.get("entry", {})),
            risk=RiskConfig(**d.get("risk", {})),
            min_session_bars_tolerance=d.get("min_session_bars_tolerance", 0),
        )

    def save(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @staticmethod
    def load(path: str) -> "BacktestConfig":
        with open(path) as f:
            return BacktestConfig.from_dict(json.load(f))

    def with_overrides(self, overrides: dict) -> "BacktestConfig":
        """
        Return a deep-copied config with dot-path overrides applied, e.g.
        {"entry.or_minutes": 20, "risk.r_multiple": 1.5}

        This is what the Optimizer uses to sample the parameter space without
        mutating the base config.
        """
        cfg = copy.deepcopy(self)
        for dotted_key, value in overrides.items():
            section_name, field_name = dotted_key.split(".", 1)
            section_obj = getattr(cfg, section_name)
            setattr(section_obj, field_name, value)
        return cfg
