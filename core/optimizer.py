"""
Optimizer module.

Implemented:
  - RandomSearchOptimizer: samples the parameter space uniformly at random,
    runs a full backtest per sample, ranks by a chosen metric.

Planned (see ROADMAP.md, Phase 5) — stubbed so the intended architecture is
visible even before they're built:
  - BayesianOptimizer
  - WalkForwardOptimizer
  - MonteCarloAnalyzer
"""

import random

from core.backtester import Backtester
from core.metrics import Metrics


class ParamSpace:
    """
    Defines a random-search parameter space over dot-path config keys.

    Each entry maps a config key (e.g. "entry.or_minutes") to a sampler spec:
      ("choice", [v1, v2, ...])   -> random.choice
      ("uniform", low, high)      -> random.uniform  (float)
      ("randint", low, high)      -> random.randint  (int, inclusive)

    Example:
        ParamSpace({
            "entry.or_minutes":  ("randint", 5, 30),
            "risk.r_multiple":   ("uniform", 0.5, 3.0),
            "risk.stop_mode":    ("choice", ["or", "atr"]),
        })
    """

    def __init__(self, spec: dict):
        self.spec = spec

    def sample(self, rng: random.Random) -> dict:
        sampled = {}
        for key, definition in self.spec.items():
            kind = definition[0]
            if kind == "choice":
                sampled[key] = rng.choice(definition[1])
            elif kind == "uniform":
                sampled[key] = rng.uniform(definition[1], definition[2])
            elif kind == "randint":
                sampled[key] = rng.randint(definition[1], definition[2])
            else:
                raise ValueError(f"Unknown sampler kind: {kind!r}")
        return sampled


class RandomSearchOptimizer:
    """
    Massive Random Search over a BacktestConfig.

    Runs `n_iter` independent backtests with randomly sampled parameter
    overrides, discards runs with too few trades to be statistically
    meaningful, and returns the top N ranked by `rank_metric`.
    """

    def __init__(
        self,
        df,
        base_config,
        param_space: ParamSpace,
        rank_metric: str = "profit_factor",
        minimize: bool = False,
        seed: int | None = None,
    ):
        self.df = df
        self.base_config = base_config
        self.param_space = param_space
        self.rank_metric = rank_metric
        self.minimize = minimize
        self.rng = random.Random(seed)

    def run(self, n_iter: int = 100, min_trades: int = 30, keep_top_n: int = 20, verbose: bool = False):
        results = []

        for i in range(n_iter):

            overrides = self.param_space.sample(self.rng)
            config = self.base_config.with_overrides(overrides)

            trades = Backtester(self.df, config).run()

            if len(trades) < min_trades:
                if verbose:
                    print(f"[{i + 1}/{n_iter}] skipped (only {len(trades)} trades) params={overrides}")
                continue

            result = Metrics().calculate(trades, starting_capital=config.instrument.starting_capital)
            result.parameters = overrides

            score = getattr(result, self.rank_metric, None)

            if score is None or score != score:  # None or NaN
                continue

            if score == float("inf"):
                score = 1e18  # keep sortable without breaking ranking

            results.append((score, overrides, result))

            if verbose:
                print(f"[{i + 1}/{n_iter}] {self.rank_metric}={score:.4f} trades={len(trades)} params={overrides}")

        results.sort(key=lambda r: r[0], reverse=not self.minimize)

        return [
            {"rank": idx + 1, "score": score, "parameters": params, "result": result}
            for idx, (score, params, result) in enumerate(results[:keep_top_n])
        ]


# ---------------------------------------------------------------------------
# Planned optimizers — not yet implemented. Kept as explicit stubs (rather
# than silently absent) so the module's public surface matches the README's
# stated architecture. See ROADMAP.md Phase 5 for design notes.
# ---------------------------------------------------------------------------

class BayesianOptimizer:
    """Planned: Gaussian-Process / TPE-guided search over the parameter space."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "BayesianOptimizer is planned for Phase 5 — see ROADMAP.md"
        )


class WalkForwardOptimizer:
    """Planned: rolling in-sample optimization + out-of-sample validation windows."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "WalkForwardOptimizer is planned for Phase 5 — see ROADMAP.md"
        )


class MonteCarloAnalyzer:
    """Planned: trade-resampling / bootstrap robustness analysis on a BacktestResult."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "MonteCarloAnalyzer is planned for Phase 5 — see ROADMAP.md"
        )
