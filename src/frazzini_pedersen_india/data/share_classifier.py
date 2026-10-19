"""Separates company shares from funds, rights and other instruments."""

import re

import pandas as pd


class ShareClassifier:
    """Finds symbols that are not ordinary company shares.

    Attributes:
        name_pattern: Matches symbols of exchange traded funds and rights.
    """

    name_pattern = re.compile(
        r'(BEES|ETF|IETF|-RE\d*$|^LIQUID|^GILT|^NIFTY\d|^SETF|^FTCPO)',
        re.IGNORECASE,
    )

    def excluded_symbols(self, prices: pd.DataFrame) -> set[str]:
        """Lists the symbols to leave out of the share universe.

        A symbol is left out if it ever carried an ISIN that does not start
        with INE, which marks funds and bonds, or if its name matches a fund
        or rights pattern.

        Args:
            prices: A table with columns symbol and isin.

        Returns:
            The set of symbols to exclude.

        Raises:
            KeyError: If a column is missing.
        """
        excluded = set()
        isins = prices[['symbol', 'isin']].dropna().drop_duplicates()
        for row in isins.itertuples(index=False):
            if not str(row.isin).startswith('INE'):
                excluded.add(row.symbol)
        for symbol in prices['symbol'].unique():
            if self.name_pattern.search(symbol):
                excluded.add(symbol)
        return excluded
