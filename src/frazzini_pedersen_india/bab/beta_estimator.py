"""Estimates ex-ante betas the way Frazzini and Pedersen (2014) do."""

import numpy as np
import pandas as pd


class BetaEstimator:
    """Computes shrunk betas from daily returns, one month-end at a time.

    The beta is correlation x stock volatility / market volatility. The
    volatilities use one year of daily log returns and the correlation uses
    five years of overlapping three-day log returns (paper eq. 14, p.17). The
    estimate is shrunk to one with a weight of 0.6 (paper eq. 15, p.17).

    Attributes:
        volatility_days: Sessions in the volatility window.
        correlation_days: Sessions in the correlation window.
        minimum_volatility_days: Fewest returns needed for volatility.
        minimum_correlation_days: Fewest three-day returns for correlation.
        shrinkage_weight: Weight on the share's own estimate.
    """

    def __init__(
        self,
        volatility_days: int = 252,
        correlation_days: int = 1260,
        minimum_volatility_days: int = 120,
        minimum_correlation_days: int = 750,
        shrinkage_weight: float = 0.6,
    ) -> None:
        """Stores the window lengths and the shrinkage weight.

        Args:
            volatility_days: Sessions in the volatility window.
            correlation_days: Sessions in the correlation window.
            minimum_volatility_days: Fewest returns needed for volatility.
            minimum_correlation_days: Fewest three-day returns needed.
            shrinkage_weight: Weight on the share's own estimate.

        Returns:
            None.

        Raises:
            None.
        """
        self.volatility_days = volatility_days
        self.correlation_days = correlation_days
        self.minimum_volatility_days = minimum_volatility_days
        self.minimum_correlation_days = minimum_correlation_days
        self.shrinkage_weight = shrinkage_weight

    def three_day_log_returns(self, log_returns: np.ndarray) -> np.ndarray:
        """Sums log returns over three consecutive sessions.

        Args:
            log_returns: Array of sessions by shares, with NaN where a share
                has no clean return.

        Returns:
            An array of the same shape. Row t holds the sum of rows t-2 to
            t, and is NaN when any of the three is NaN or t is below 2.

        Raises:
            None.
        """
        result = np.full(log_returns.shape, np.nan)
        result[2:] = log_returns[2:] + log_returns[1:-1] + log_returns[:-2]
        return result

    def estimate(
        self,
        stock_returns: pd.DataFrame,
        market_returns: pd.Series,
        formation_dates: list[pd.Timestamp],
    ) -> pd.DataFrame:
        """Computes shrunk betas at each formation date.

        Only returns up to and including a formation date are used for the
        beta at that date.

        Args:
            stock_returns: Simple daily returns, sessions by shares, with NaN
                where a return is missing.
            market_returns: Simple daily market returns on the same sessions.
            formation_dates: Dates at which to estimate, all in the index.

        Returns:
            A table of formation dates by shares holding the shrunk betas,
            NaN where the data minimums are not met.

        Raises:
            KeyError: If a formation date is not a session in the index.
        """
        stock_log = np.log1p(stock_returns.to_numpy(dtype=float))
        market_log = np.log1p(market_returns.to_numpy(dtype=float))
        stock_three = self.three_day_log_returns(stock_log)
        market_three = self.three_day_log_returns(market_log[:, None])[:, 0]
        betas = np.full((len(formation_dates), stock_log.shape[1]), np.nan)
        for row, date in enumerate(formation_dates):
            position = stock_returns.index.get_loc(date)
            betas[row] = self.beta_at(
                stock_log, market_log, stock_three, market_three, position
            )
        return pd.DataFrame(
            betas,
            index=pd.DatetimeIndex(formation_dates),
            columns=stock_returns.columns,
        )

    def beta_at(
        self,
        stock_log: np.ndarray,
        market_log: np.ndarray,
        stock_three: np.ndarray,
        market_three: np.ndarray,
        position: int,
    ) -> np.ndarray:
        """Computes every share's shrunk beta at one session.

        Args:
            stock_log: Daily log returns, sessions by shares.
            market_log: Daily market log returns.
            stock_three: Three-day log returns, sessions by shares.
            market_three: Three-day market log returns.
            position: Row of the formation session.

        Returns:
            An array with one shrunk beta per share, NaN where data are too
            few.

        Raises:
            None.
        """
        vol_start = max(0, position - self.volatility_days + 1)
        daily = stock_log[vol_start : position + 1]
        valid_days = np.sum(~np.isnan(daily), axis=0)
        stock_vol = np.nanstd(daily, axis=0, ddof=1)
        market_vol = np.std(market_log[vol_start : position + 1], ddof=1)
        stock_vol[valid_days < self.minimum_volatility_days] = np.nan
        corr_start = max(0, position - self.correlation_days + 1)
        correlation = self.masked_correlation(
            market_three[corr_start : position + 1],
            stock_three[corr_start : position + 1],
        )
        own_beta = correlation * stock_vol / market_vol
        weight = self.shrinkage_weight
        return weight * own_beta + (1.0 - weight) * 1.0

    def masked_correlation(
        self, market: np.ndarray, stocks: np.ndarray
    ) -> np.ndarray:
        """Correlates a market series with each share over shared sessions.

        Args:
            market: Market values, one per session, possibly with NaN.
            stocks: Share values, sessions by shares, possibly with NaN.

        Returns:
            One correlation per share, NaN where fewer than the minimum
            number of shared sessions exist.

        Raises:
            None.
        """
        present = ~np.isnan(stocks) & ~np.isnan(market)[:, None]
        mask = present.astype(float)
        count = mask.sum(axis=0)
        x = np.where(np.isnan(market), 0.0, market)
        y = np.where(present, stocks, 0.0)
        sum_x = x @ mask
        sum_y = y.sum(axis=0)
        sum_xy = x @ y
        sum_xx = (x * x) @ mask
        sum_yy = (y * y).sum(axis=0)
        with np.errstate(divide='ignore', invalid='ignore'):
            covariance = sum_xy - sum_x * sum_y / count
            variance_x = sum_xx - sum_x * sum_x / count
            variance_y = sum_yy - sum_y * sum_y / count
            correlation = covariance / np.sqrt(variance_x * variance_y)
        correlation[count < self.minimum_correlation_days] = np.nan
        return correlation
