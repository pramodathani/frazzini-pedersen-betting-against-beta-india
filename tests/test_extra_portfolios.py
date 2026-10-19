"""Tests for the robustness portfolios."""

import numpy as np
import pandas as pd
import pytest

from frazzini_pedersen_india.bab.extra_portfolios import ExtraPortfolios


class TestExtraPortfolios:
    """Checks on the extra portfolios' weights."""

    def make_inputs(
        self,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Makes inputs for 300 shares on one date.

        Args:
            None.

        Returns:
            Betas, traded values, trading flags and volatilities.

        Raises:
            None.
        """
        generator = np.random.default_rng(4)
        names = [f'S{number}' for number in range(300)]
        dates = pd.DatetimeIndex(['2020-01-31'])
        betas = pd.DataFrame(
            [generator.uniform(0.5, 1.6, 300)], index=dates, columns=names
        )
        values = pd.DataFrame(
            [generator.uniform(1.0, 100.0, 300)], index=dates, columns=names
        )
        traded = pd.DataFrame(True, index=dates, columns=names)
        volatility = pd.DataFrame(
            [generator.uniform(0.01, 0.05, 300)], index=dates, columns=names
        )
        return betas, values, traded, volatility

    def test_every_bab_variant_has_zero_beta(self) -> None:
        """Each BAB-type portfolio nets to zero ex-ante beta.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If a net beta is not zero.
        """
        betas, values, traded, volatility = self.make_inputs()
        builder = ExtraPortfolios(liquid_count=150)
        result = builder.build(
            betas, values, traded, volatility, list(betas.index)
        )
        row = betas.iloc[0]
        for name, table in result.items():
            if 'leg' in name:
                continue
            weights = table.iloc[0]
            net = (weights * row.reindex(weights.index)).sum()
            assert net == pytest.approx(0.0, abs=1e-9), name

    def test_scaled_legs_have_beta_one(self) -> None:
        """A scaled leg has an ex-ante beta of one.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If a leg's beta is not one.
        """
        betas, values, traded, volatility = self.make_inputs()
        builder = ExtraPortfolios(liquid_count=150)
        result = builder.build(
            betas, values, traded, volatility, list(betas.index)
        )
        row = betas.iloc[0]
        for name in ('full_low_leg_scaled', 'liquid_high_leg_scaled'):
            weights = result[name].iloc[0]
            beta = (weights * row.reindex(weights.index)).sum()
            assert beta == pytest.approx(1.0)

    def test_groups_exist(self) -> None:
        """Five size groups and five volatility groups are built.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If a group is missing.
        """
        betas, values, traded, volatility = self.make_inputs()
        builder = ExtraPortfolios(liquid_count=150)
        result = builder.build(
            betas, values, traded, volatility, list(betas.index)
        )
        for group in range(1, 6):
            assert f'bab_size_Q{group}' in result
            assert f'bab_ivol_Q{group}' in result
