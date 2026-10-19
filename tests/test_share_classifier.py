"""Tests for the share classifier."""

import pandas as pd

from frazzini_pedersen_india.data.share_classifier import ShareClassifier


class TestShareClassifier:
    """Checks on which symbols are left out."""

    def test_funds_and_rights_are_excluded(self) -> None:
        """Fund ISINs, fund names and rights symbols are excluded.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If a symbol is wrongly kept or dropped.
        """
        prices = pd.DataFrame(
            {
                'symbol': ['TCS', 'GOLDBEES', 'XYZFUND', 'ABC-RE', 'OLDETF'],
                'isin': [
                    'INE467B01029',
                    'INF204KB17I5',
                    'INF000A01010',
                    None,
                    None,
                ],
            }
        )
        excluded = ShareClassifier().excluded_symbols(prices)
        assert excluded == {'GOLDBEES', 'XYZFUND', 'ABC-RE', 'OLDETF'}
