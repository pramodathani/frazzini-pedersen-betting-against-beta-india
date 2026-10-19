"""Tests for the delisting stress."""

import numpy as np
import pandas as pd
import pytest

from frazzini_pedersen_india.bab.delisting_stress import DelistingStress


class TestDelistingStress:
    """Checks on terminal losses."""

    def test_loss_is_charged_in_the_month_after_the_last_return(self) -> None:
        """A share that stops gets the loss; a live share does not.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If a return is wrong.
        """
        index = pd.period_range('2020-01', periods=4, freq='M')
        table = pd.DataFrame(
            {
                'GONE': [0.01, 0.02, np.nan, np.nan],
                'LIVE': [0.01, 0.02, 0.03, 0.04],
            },
            index=index,
        )
        free = pd.Series(0.005, index=index)
        stressed = DelistingStress().apply(table, -1.0, free)
        assert stressed.loc['2020-03', 'GONE'] == pytest.approx(-1.005)
        assert np.isnan(stressed.loc['2020-04', 'GONE'])
        assert stressed['LIVE'].tolist() == table['LIVE'].tolist()
