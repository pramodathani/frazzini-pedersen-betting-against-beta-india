"""Tests for the monthly weight schedule."""

import numpy as np
import pandas as pd
import pytest

from frazzini_pedersen_india.bab.weight_schedule import WeightSchedule


class TestWeightSchedule:
    """Checks on the target weights."""

    def make_inputs(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Makes betas and traded values for 200 shares on two dates.

        Args:
            None.

        Returns:
            The betas and the median traded values.

        Raises:
            None.
        """
        names = [f'S{number}' for number in range(200)]
        dates = pd.DatetimeIndex(['2020-01-31', '2020-02-28'])
        betas = pd.DataFrame(
            [0.5 + 0.005 * np.arange(200)] * 2, index=dates, columns=names
        )
        values = pd.DataFrame(
            [np.arange(200, 0, -1.0)] * 2, index=dates, columns=names
        )
        return betas, values

    def test_labels_are_the_next_month(self) -> None:
        """Weights formed in January are labelled February.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If the labels are wrong.
        """
        betas, values = self.make_inputs()
        schedule = WeightSchedule(liquid_count=100)
        result = schedule.build(betas, values, list(betas.index))
        table = result['full_D1']
        assert list(table.index) == [
            pd.Period('2020-02'),
            pd.Period('2020-03'),
        ]

    def test_liquid_universe_is_most_traded(self) -> None:
        """Only the 100 most traded shares carry liquid weights.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If another share has weight.
        """
        betas, values = self.make_inputs()
        schedule = WeightSchedule(liquid_count=100)
        result = schedule.build(betas, values, list(betas.index))
        liquid = result['liquid_D1'].iloc[0]
        assert (liquid[liquid > 0].index.str[1:].astype(int) < 100).all()
        assert result['liquid_D1'].iloc[0].sum() == pytest.approx(1.0)

    def test_bab_has_zero_beta_and_levered_low_leg_has_beta_one(self) -> None:
        """BAB nets to zero beta and the levered low leg to beta one.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If a beta is wrong.
        """
        betas, values = self.make_inputs()
        schedule = WeightSchedule(liquid_count=100)
        result = schedule.build(betas, values, list(betas.index))
        row = betas.iloc[0]
        for name in ('bab_full', 'bab_liquid'):
            weights = result[name].iloc[0]
            net = (weights * row.reindex(weights.index)).sum()
            assert net == pytest.approx(0.0, abs=1e-9)
        levered = result['bab_low_leg_levered'].iloc[0]
        beta = (levered * row.reindex(levered.index)).sum()
        assert beta == pytest.approx(1.0)
