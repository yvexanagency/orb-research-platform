from dataclasses import dataclass, field

from core.trade import Trade


@dataclass
class BacktestResult:

    # Raw data
    trades: list[Trade]

    # Trade statistics
    total_trades: int
    winners: int
    losers: int
    win_rate: float

    # Profit ($)
    gross_profit: float
    gross_loss: float
    net_profit: float

    # Profit (points)
    gross_profit_points: float
    gross_loss_points: float
    net_profit_points: float

    # Performance
    profit_factor: float
    expectancy: float

    average_trade: float
    average_win: float
    average_loss: float

    max_win: float
    max_loss: float

    consecutive_wins: int
    consecutive_losses: int

    # Filled in later milestones
    equity_curve: list = field(default_factory=list)
    drawdown_curve: list = field(default_factory=list)

    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0

    sharpe: float | None = None
    sortino: float | None = None
    recovery_factor: float | None = None

    yearly_returns: dict = field(default_factory=dict)
    monthly_returns: dict = field(default_factory=dict)

    parameters: dict = field(default_factory=dict)

    robustness_score: float | None = None