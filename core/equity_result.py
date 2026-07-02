from dataclasses import dataclass, field

from core.trade import Trade


@dataclass
class EquityResult:
    trades: list[Trade]

    equity_curve: list[float] = field(default_factory=list)
    drawdown_curve: list[float] = field(default_factory=list)
    drawdown_pct_curve: list[float] = field(default_factory=list)

    final_equity: float = 0.0
    peak_equity: float = 0.0

    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0