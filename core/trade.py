from dataclasses import dataclass
from datetime import datetime


@dataclass
class Trade:
    date: object

    side: str

    entry_time: datetime
    entry_price: float

    exit_time: datetime = None
    exit_price: float = None

    stop_loss: float = None
    take_profit: float = None

    exit_reason: str = None

    pnl_points: float = 0.0
    pnl_dollars: float = 0.0

    risk: float = 0.0
    reward: float = 0.0
