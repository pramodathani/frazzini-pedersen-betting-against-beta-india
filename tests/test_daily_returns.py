"""Tests for daily returns with corporate actions."""

import pandas as pd
import pytest

from frazzini_pedersen_india.data.daily_returns import DailyReturnBuilder


class TestDailyReturnBuilder:
    """Checks on adjusted daily returns."""

    def make_prices(self, closes: list[float]) -> pd.DataFrame:
        """Makes one share's closes on consecutive weekdays.

        Args:
            closes: The closes, oldest first.

        Returns:
            A price table for the share ABC.

        Raises:
            None.
        """
        dates = pd.bdate_range('2020-01-01', periods=len(closes))
        return pd.DataFrame(
            {
                'date': dates,
                'symbol': 'ABC',
                'close': closes,
                'traded_value': 1000.0,
            }
        )

    def make_actions(
        self, ex_date: str, factor: float, dividend: float
    ) -> pd.DataFrame:
        """Makes a one-row action table for ABC.

        Args:
            ex_date: The ex-date as text.
            factor: The price factor.
            dividend: The cash dividend.

        Returns:
            The action table.

        Raises:
            None.
        """
        return pd.DataFrame(
            {
                'symbol': ['ABC'],
                'ex_date': [pd.Timestamp(ex_date)],
                'price_factor': [factor],
                'dividend': [dividend],
            }
        )

    def test_plain_return(self) -> None:
        """Without actions the return is close over previous close.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If a return is wrong.
        """
        prices = self.make_prices([100.0, 110.0, 99.0])
        empty = self.make_actions('2020-01-01', 1.0, 0.0).iloc[0:0]
        returns, errors = DailyReturnBuilder().build(prices, empty)
        assert returns['return'].tolist() == pytest.approx([0.1, -0.1])
        assert len(errors) == 0

    def test_bonus_is_not_a_loss(self) -> None:
        """A 1:1 bonus halves the price but the return stays flat.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If the return is not zero.
        """
        prices = self.make_prices([100.0, 50.0, 51.0])
        actions = self.make_actions('2020-01-02', 0.5, 0.0)
        returns, errors = DailyReturnBuilder().build(prices, actions)
        assert len(errors) == 0
        assert returns['return'].iloc[0] == pytest.approx(0.0)
        assert returns['return'].iloc[1] == pytest.approx(0.02)

    def test_dividend_adds_to_return(self) -> None:
        """A dividend on the ex-date is part of the return.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If the return is wrong.
        """
        prices = self.make_prices([100.0, 98.0])
        actions = self.make_actions('2020-01-02', 1.0, 3.0)
        returns, errors = DailyReturnBuilder().build(prices, actions)
        assert len(errors) == 0
        assert returns['return'].iloc[0] == pytest.approx(0.01)

    def test_action_on_holiday_moves_to_next_session(self) -> None:
        """An ex-date on a weekend applies to the next session.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If the split is not applied on Monday.
        """
        prices = self.make_prices([100.0, 100.0, 100.0, 20.0])
        actions = self.make_actions('2020-01-04', 0.2, 0.0)
        returns, errors = DailyReturnBuilder().build(prices, actions)
        assert len(errors) == 0
        assert returns['return'].iloc[2] == pytest.approx(0.0)

    def test_missed_split_is_zeroed_and_logged(self) -> None:
        """An unexplained 80 percent fall is set to zero and recorded.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If the error is not logged.
        """
        prices = self.make_prices([100.0, 20.0, 21.0])
        empty = self.make_actions('2020-01-01', 1.0, 0.0).iloc[0:0]
        returns, errors = DailyReturnBuilder().build(prices, empty)
        assert returns['return'].iloc[0] == 0.0
        assert len(errors) == 1
        assert errors['return'].iloc[0] == pytest.approx(-0.8)

    def test_no_return_uses_other_shares_close(self) -> None:
        """Two shares do not mix their previous closes.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If the second share's return is wrong.
        """
        first = self.make_prices([100.0, 101.0])
        second = self.make_prices([50.0, 55.0])
        second['symbol'] = 'XYZ'
        prices = pd.concat([first, second], ignore_index=True)
        empty = self.make_actions('2020-01-01', 1.0, 0.0).iloc[0:0]
        returns, _ = DailyReturnBuilder().build(prices, empty)
        by_symbol = returns.set_index('symbol')['return']
        assert by_symbol['XYZ'] == pytest.approx(0.1)
        assert by_symbol['ABC'] == pytest.approx(0.01)
