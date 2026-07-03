from dataclasses import dataclass

import pandas as pd

from core.trade import Trade


@dataclass
class EntrySignal:
    trade: Trade
    day_data: pd.DataFrame
    entry_index: int
    or_high: float
    or_low: float
