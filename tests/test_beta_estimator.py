"""Tests for the beta estimator."""

import numpy as np
import pandas as pd
import pytest

from frazzini_pedersen_india.bab.beta_estimator import BetaEstimator


class TestBetaEstimator:
    """Checks on shrunk beta estimates."""

    def make_returns(
        self, sessions: int, true_betas: list[float], seed: int = 1
    ) -> tuple[pd.DataFrame, pd.Series]:
        """Simulates a market and shares with known betas.

        Args:
            sessions: Number of daily sessions.
            true_betas: Each share's true beta.
            seed: Seed for the random numbers.

        Returns:
            The share returns and the market returns.

        Raises:
            None.
        """
        generator = np.random.default_rng(seed)
        index = pd.bdate_range('2010-01-01', periods=sessions)
        market = pd.Series(generator.normal(0.0, 0.01, sessions), index=index)
        columns = {}
        for number, beta in enumerate(true_betas):
            noise = generator.normal(0.0, 0.005, sessions)
            columns[f'S{number}'] = beta * market.to_numpy() + noise
        return pd.DataFrame(columns, index=index), market

    def test_recovers_known_betas(self) -> None:
        """Without shrinkage the estimate is close to the true beta.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If an estimate is far from its true beta.
        """
        stocks, market = self.make_returns(1500, [0.5, 1.0, 1.5])
        estimator = BetaEstimator(shrinkage_weight=1.0)
        result = estimator.estimate(stocks, market, [stocks.index[-1]])
        estimates = result.iloc[0].to_numpy()
        assert estimates == pytest.approx([0.5, 1.0, 1.5], abs=0.12)

    def test_shrinkage_pulls_toward_one(self) -> None:
        """A weight of 0.6 gives 0.6 x own beta + 0.4.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If shrinkage is wrong.
        """
        stocks, market = self.make_returns(1500, [0.5])
        date = stocks.index[-1]
        raw = BetaEstimator(shrinkage_weight=1.0).estimate(
            stocks, market, [date]
        )
        shrunk = BetaEstimator().estimate(stocks, market, [date])
        expected = 0.6 * raw.iloc[0, 0] + 0.4
        assert shrunk.iloc[0, 0] == pytest.approx(expected)

    def test_too_little_history_gives_nan(self) -> None:
        """A share with under 750 three-day returns has no beta.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If a beta is returned.
        """
        stocks, market = self.make_returns(600, [1.0])
        result = BetaEstimator().estimate(stocks, market, [stocks.index[-1]])
        assert np.isnan(result.iloc[0, 0])

    def test_no_look_ahead(self) -> None:
        """Changing returns after the formation date leaves the beta alone.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If the beta changes.
        """
        stocks, market = self.make_returns(1500, [1.2, 0.7])
        date = stocks.index[1200]
        first = BetaEstimator().estimate(stocks, market, [date])
        changed_stocks = stocks.copy()
        changed_market = market.copy()
        changed_stocks.iloc[1201:] = 0.5
        changed_market.iloc[1201:] = -0.3
        second = BetaEstimator().estimate(
            changed_stocks, changed_market, [date]
        )
        assert first.to_numpy() == pytest.approx(second.to_numpy())

    def test_three_day_returns_need_three_clean_days(self) -> None:
        """A missing day blanks the three three-day windows that use it.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If the windows are wrong.
        """
        daily = np.array([[0.1], [0.1], [np.nan], [0.1], [0.1], [0.1]])
        result = BetaEstimator().three_day_log_returns(daily)
        assert np.isnan(result[:5, 0]).all()
        assert result[5, 0] == pytest.approx(0.3)
