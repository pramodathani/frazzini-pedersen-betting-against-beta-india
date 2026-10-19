"""Tests for beta-sorted portfolios."""

import numpy as np
import pandas as pd
import pytest

from frazzini_pedersen_india.bab.portfolio_builder import PortfolioBuilder


class TestPortfolioBuilder:
    """Checks on decile and BAB weights."""

    def make_betas(self, count: int) -> pd.Series:
        """Makes betas rising evenly from 0.5.

        Args:
            count: Number of shares.

        Returns:
            Betas indexed S0, S1 and so on.

        Raises:
            None.
        """
        names = [f'S{number}' for number in range(count)]
        return pd.Series(0.5 + 0.01 * np.arange(count), index=names)

    def test_deciles_are_equal_sized_and_sum_to_one(self) -> None:
        """With every share a breakpoint, deciles hold ten shares each.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If a decile is wrong.
        """
        betas = self.make_betas(100)
        flags = pd.Series(True, index=betas.index)
        weights = PortfolioBuilder().decile_weights(betas, flags)
        assert weights.sum().to_numpy() == pytest.approx(np.ones(10))
        assert (weights[1] > 0).sum() == 10
        assert weights.loc['S0', 1] == pytest.approx(0.1)
        assert weights.loc['S99', 10] == pytest.approx(0.1)

    def test_breakpoints_from_a_subset(self) -> None:
        """Cut points from the low-beta half push shares into top deciles.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If the top decile is not the top shares.
        """
        betas = self.make_betas(100)
        flags = pd.Series(False, index=betas.index)
        flags.iloc[:50] = True
        weights = PortfolioBuilder().decile_weights(betas, flags)
        assert (weights[10] > 0).sum() == 55

    def test_bab_legs_sum_to_one_and_split_by_median(self) -> None:
        """Each BAB leg adds to one and low shares sit below the median.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If a leg is wrong.
        """
        betas = self.make_betas(10)
        flags = pd.Series(True, index=betas.index)
        low, high, _, _ = PortfolioBuilder().bab_weights(betas, flags)
        assert low.sum() == pytest.approx(1.0)
        assert high.sum() == pytest.approx(1.0)
        assert (low[5:] == 0).all()
        assert (high[:5] == 0).all()
        assert low['S0'] > low['S4']

    def test_bab_matches_paper_formula_by_hand(self) -> None:
        """Four shares give weights 1.5 and 0.5 over 2 on each side.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If a weight is wrong.
        """
        betas = pd.Series([0.6, 0.8, 1.2, 1.6], index=list('ABCD'))
        flags = pd.Series(True, index=betas.index)
        low, high, low_beta, high_beta = PortfolioBuilder().bab_weights(
            betas, flags
        )
        assert low['A'] == pytest.approx(0.75)
        assert low['B'] == pytest.approx(0.25)
        assert high['D'] == pytest.approx(0.75)
        assert high['C'] == pytest.approx(0.25)
        assert low_beta == pytest.approx(0.75 * 0.6 + 0.25 * 0.8)
        assert high_beta == pytest.approx(0.75 * 1.6 + 0.25 * 1.2)

    def test_bab_target_has_zero_ex_ante_beta(self) -> None:
        """The scaled BAB weights have a beta of zero.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If the net beta is not zero.
        """
        betas = self.make_betas(40)
        flags = pd.Series(True, index=betas.index)
        builder = PortfolioBuilder()
        low, high, low_beta, high_beta = builder.bab_weights(betas, flags)
        target = builder.bab_target(low, high, low_beta, high_beta)
        assert (target * betas).sum() == pytest.approx(0.0, abs=1e-12)
        assert target.clip(lower=0).sum() == pytest.approx(1.0 / low_beta)
        assert (-target).clip(lower=0).sum() == pytest.approx(1.0 / high_beta)

    def test_legs_add_to_one_when_split_is_off_the_mean_rank(self) -> None:
        """A breakpoint set that splits unevenly still gives unit legs.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If a leg does not add to one.
        """
        betas = self.make_betas(11)
        flags = pd.Series(False, index=betas.index)
        flags.iloc[:4] = True
        low, high, _, _ = PortfolioBuilder().bab_weights(betas, flags)
        assert low.sum() == pytest.approx(1.0)
        assert high.sum() == pytest.approx(1.0)

    def test_value_weighted_bab_has_zero_beta(self) -> None:
        """The two-by-three BAB nets to zero ex-ante beta.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If the beta is not zero.
        """
        betas = self.make_betas(200)
        generator = np.random.default_rng(2)
        values = pd.Series(
            generator.permutation(np.arange(1.0, 201.0)), index=betas.index
        )
        flags = pd.Series(True, index=betas.index)
        target = PortfolioBuilder().value_weighted_bab(betas, values, flags)
        assert (target * betas).sum() == pytest.approx(0.0, abs=1e-9)
        assert target.clip(lower=0).sum() > 1.0

    def test_equal_weighted_bab_has_zero_beta(self) -> None:
        """The equal-weighted BAB nets to zero ex-ante beta.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If the beta is not zero or weights unequal.
        """
        betas = self.make_betas(10)
        flags = pd.Series(True, index=betas.index)
        target = PortfolioBuilder().equal_weighted_bab(betas, flags)
        assert (target * betas).sum() == pytest.approx(0.0, abs=1e-12)
        assert target['S0'] == pytest.approx(target['S1'])
