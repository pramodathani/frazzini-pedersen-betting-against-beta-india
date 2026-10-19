"""Tests for linking symbols across renames."""

import pandas as pd

from frazzini_pedersen_india.data.share_identity import ShareIdentity


class TestShareIdentity:
    """Checks on symbol groups."""

    def test_rename_and_isin_change_are_linked(self) -> None:
        """A rename and a split ISIN change end in one group.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If the mapping is wrong.
        """
        prices = pd.DataFrame(
            {
                'date': pd.to_datetime(
                    ['2015-01-01', '2016-01-01', '2017-01-01', '2017-01-01']
                ),
                'symbol': ['OLD', 'NEW', 'NEW', 'OTHER'],
                'isin': ['INE001', 'INE001', 'INE002', 'INE900'],
            }
        )
        mapping = ShareIdentity().symbol_map(prices)
        assert mapping['OLD'] == 'NEW'
        assert mapping['NEW'] == 'NEW'
        assert mapping['OTHER'] == 'OTHER'

    def test_symbol_without_isin_stays_alone(self) -> None:
        """A symbol that never has an ISIN maps to itself.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If it is linked to another share.
        """
        prices = pd.DataFrame(
            {
                'date': pd.to_datetime(['2005-01-01', '2020-01-01']),
                'symbol': ['ANCIENT', 'TCS'],
                'isin': [None, 'INE467'],
            }
        )
        mapping = ShareIdentity().symbol_map(prices)
        assert mapping['ANCIENT'] == 'ANCIENT'
