"""Idiosyncratic volatility of shares, as a market-model residual."""

import numpy as np
import pandas as pd


class IdiosyncraticVolatility:
    """Estimates each share's residual volatility from daily returns.

    The residual variance is the share's variance minus beta squared times
    the market variance over one year, with beta the plain regression slope.
    This approximates the paper's rolling residual volatility (p.61).

    Attributes:
        window: Sessions in the look-back.
        minimum_days: Fewest returns needed.
    """

    def __init__(self, window: int = 252, minimum_days: int = 120) -> None:
        """Stores the window.

        Args:
            window: Sessions in the look-back.
            minimum_days: Fewest returns needed.

        Returns:
            None.

        Raises:
            None.
        """
        self.window = window
        self.minimum_days = minimum_days

    def estimate(
        self,
        stock_returns: pd.DataFrame,
        market_returns: pd.Series,
        dates: list[pd.Timestamp],
    ) -> pd.DataFrame:
        """Computes residual volatility at each date.

        Args:
            stock_returns: Daily returns, sessions by shares.
            market_returns: Daily market returns on the same sessions.
            dates: Sessions at which to estimate.

        Returns:
            A table of dates by shares, NaN where data are too few.

        Raises:
            KeyError: If a date is not a session.
        """
        rows = []
        market_all = market_returns.to_numpy(dtype=float)
        stocks_all = stock_returns.to_numpy(dtype=float)
        for date in dates:
            position = stock_returns.index.get_loc(date)
            start = max(0, position - self.window + 1)
            stocks = stocks_all[start : position + 1]
            market = market_all[start : position + 1]
            present = ~np.isnan(stocks)
            count = present.sum(axis=0)
            filled = np.where(present, stocks, 0.0)
            mask = present.astype(float)
            with np.errstate(divide='ignore', invalid='ignore'):
                sum_x = market @ mask
                sum_xx = (market * market) @ mask
                sum_y = filled.sum(axis=0)
                sum_yy = (filled * filled).sum(axis=0)
                sum_xy = market @ filled
                var_x = sum_xx - sum_x * sum_x / count
                var_y = sum_yy - sum_y * sum_y / count
                cov = sum_xy - sum_x * sum_y / count
                residual = (var_y - cov * cov / var_x) / (count - 2)
            residual[count < self.minimum_days] = np.nan
            residual[residual < 0] = 0.0
            rows.append(np.sqrt(residual))
        return pd.DataFrame(
            rows,
            index=pd.DatetimeIndex(dates),
            columns=stock_returns.columns,
        )
