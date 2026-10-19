"""Tests for idiosyncratic volatility."""

import numpy as np
import pandas as pd
import pytest

from frazzini_pedersen_india.bab.idiosyncratic_volatility import (
    IdiosyncraticVolatility,
)


class TestIdiosyncraticVolatility:
    """Checks on residual volatility."""

    def test_recovers_noise_volatility(self) -> None:
        """The residual volatility is close to the noise's.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If the estimate is far from 0.005.
        """
        generator = np.random.default_rng(5)
        index = pd.bdate_range('2020-01-01', periods=400)
        market = pd.Series(generator.normal(0, 0.01, 400), index=index)
        stock = 1.3 * market + generator.normal(0, 0.005, 400)
        table = pd.DataFrame({'A': stock}, index=index)
        result = IdiosyncraticVolatility().estimate(table, market, [index[-1]])
        assert result.iloc[0, 0] == pytest.approx(0.005, abs=0.0007)

    def test_few_observations_give_nan(self) -> None:
        """Under the minimum number of returns there is no estimate.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If a value is returned.
        """
        index = pd.bdate_range('2020-01-01', periods=50)
        market = pd.Series(np.linspace(-0.01, 0.01, 50), index=index)
        table = pd.DataFrame({'A': market * 2.0}, index=index)
        result = IdiosyncraticVolatility().estimate(table, market, [index[-1]])
        assert np.isnan(result.iloc[0, 0])
