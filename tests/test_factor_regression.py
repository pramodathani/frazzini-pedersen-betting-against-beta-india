"""Tests for the factor regression."""

import numpy as np
import pandas as pd
import pytest

from frazzini_pedersen_india.bab.factor_regression import FactorRegression


class TestFactorRegression:
    """Checks on alpha and loadings."""

    def test_recovers_alpha_and_loading(self) -> None:
        """A series built from a known alpha and loading is recovered.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If an estimate is far from the truth.
        """
        generator = np.random.default_rng(3)
        index = pd.period_range('2010-01', periods=240, freq='M')
        factor = pd.Series(generator.normal(0.0, 0.04, 240), index=index)
        noise = generator.normal(0.0, 0.002, 240)
        returns = 0.01 + 0.8 * factor + noise
        result = FactorRegression().alpha(returns, factor.to_frame('MF'))
        assert result['alpha'] == pytest.approx(0.01, abs=0.001)
        assert result['loading_MF'] == pytest.approx(0.8, abs=0.02)
        assert result['periods'] == 240.0
        assert result['alpha_t'] > 10.0

    def test_too_few_months_gives_nan(self) -> None:
        """Under ten months there is no estimate.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If an estimate is returned.
        """
        index = pd.period_range('2010-01', periods=5, freq='M')
        returns = pd.Series(0.01, index=index)
        factors = pd.DataFrame({'MF': np.arange(5.0)}, index=index)
        result = FactorRegression().alpha(returns, factors)
        assert np.isnan(result['alpha'])
