"""Tests for the return panel."""

import pandas as pd
import pytest

from frazzini_pedersen_india.bab.return_panel import ReturnPanel


class TestReturnPanel:
    """Checks on the daily and monthly matrices."""

    def make_panel(self) -> ReturnPanel:
        """Builds a panel of one share that misses a session.

        Args:
            None.

        Returns:
            A panel over six sessions in two months.

        Raises:
            None.
        """
        sessions = pd.DatetimeIndex(
            [
                '2020-01-29',
                '2020-01-30',
                '2020-01-31',
                '2020-02-03',
                '2020-02-04',
                '2020-02-05',
            ]
        )
        rows = []
        for date, value in (
            ('2020-01-30', 0.10),
            ('2020-01-31', 0.10),
            ('2020-02-05', 0.21),
        ):
            rows.append(
                {
                    'date': pd.Timestamp(date),
                    'symbol': 'ABC',
                    'return': value,
                    'traded_value': 100.0,
                }
            )
        return ReturnPanel(pd.DataFrame(rows), sessions)

    def test_gap_return_is_cleaned_but_kept_in_full(self) -> None:
        """A return over a missed session is NaN in the clean matrix.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If a matrix is wrong.
        """
        panel = self.make_panel()
        date = pd.Timestamp('2020-02-05')
        assert panel.daily_full.loc[date, 'ABC'] == pytest.approx(0.21)
        assert pd.isna(panel.daily_clean.loc[date, 'ABC'])
        assert panel.daily_clean.loc['2020-01-31', 'ABC'] == pytest.approx(
            0.10
        )

    def test_monthly_return_compounds_days(self) -> None:
        """Daily returns compound within each month.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If a monthly return is wrong.
        """
        monthly = self.make_panel().monthly_returns()
        assert monthly.loc['2020-01', 'ABC'] == pytest.approx(1.1 * 1.1 - 1.0)
        assert monthly.loc['2020-02', 'ABC'] == pytest.approx(0.21)

    def test_month_ends(self) -> None:
        """The month-end dates are each month's last session.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If the dates are wrong.
        """
        ends = self.make_panel().month_ends()
        assert ends == [
            pd.Timestamp('2020-01-31'),
            pd.Timestamp('2020-02-05'),
        ]
