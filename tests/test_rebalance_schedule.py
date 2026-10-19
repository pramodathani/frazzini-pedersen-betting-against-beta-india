"""Tests for holding portfolios between rebalances."""

import pandas as pd
import pytest

from frazzini_pedersen_india.bab.rebalance_schedule import RebalanceSchedule


class TestRebalanceSchedule:
    """Checks on drifted weights."""

    def test_weights_drift_then_reset(self) -> None:
        """Weights drift for two months and reset in the third.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If a weight is wrong.
        """
        index = pd.period_range('2020-01', periods=4, freq='M')
        weights = pd.DataFrame({'A': [0.5] * 4, 'B': [0.5] * 4}, index=index)
        returns = pd.DataFrame(
            {'A': [0.2, 0.0, 0.0, 0.0], 'B': [0.0, 0.0, 0.0, 0.0]},
            index=index,
        )
        held = RebalanceSchedule().hold_between(weights, returns, 3)
        assert held.iloc[0]['A'] == pytest.approx(0.5)
        assert held.iloc[1]['A'] == pytest.approx(0.6 / 1.1)
        assert held.iloc[2]['A'] == pytest.approx(0.6 / 1.1)
        assert held.iloc[3]['A'] == pytest.approx(0.5)
        assert held.iloc[1].sum() == pytest.approx(1.0)
