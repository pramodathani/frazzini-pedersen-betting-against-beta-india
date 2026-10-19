"""Links a company's symbols across renames and ISIN changes."""

import pandas as pd


class ShareIdentity:
    """Groups symbols and ISINs that belong to the same listed share.

    Two symbols are the same share when one ISIN appears under both, and two
    ISINs are the same share when one symbol carries both, as after a split
    or consolidation. The groups are the connected pieces of that graph.
    """

    def __init__(self) -> None:
        """Starts with no links.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        self.parent = {}

    def find(self, node: str) -> str:
        """Finds a node's group representative.

        Args:
            node: A symbol or an ISIN, as text.

        Returns:
            The representative of the node's group.

        Raises:
            None.
        """
        if node not in self.parent:
            self.parent[node] = node
        root = node
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[node] != root:
            following = self.parent[node]
            self.parent[node] = root
            node = following
        return root

    def link(self, first: str, second: str) -> None:
        """Puts two nodes in the same group.

        Args:
            first: A symbol or ISIN.
            second: A symbol or ISIN.

        Returns:
            None.

        Raises:
            None.
        """
        self.parent[self.find(first)] = self.find(second)

    def symbol_map(self, prices: pd.DataFrame) -> dict[str, str]:
        """Maps every symbol to the latest symbol of its group.

        Args:
            prices: A table with columns date, symbol and isin.

        Returns:
            A dictionary from each symbol to its group's most recently traded
            symbol.

        Raises:
            KeyError: If a column is missing.
        """
        pairs = prices[['symbol', 'isin']].dropna().drop_duplicates()
        for row in pairs.itertuples(index=False):
            self.link('S:' + row.symbol, 'I:' + str(row.isin))
        last_seen = prices.groupby('symbol')['date'].max().sort_values()
        latest = {}
        for symbol in last_seen.index:
            latest[self.find('S:' + symbol)] = symbol
        mapping = {}
        for symbol in last_seen.index:
            mapping[symbol] = latest[self.find('S:' + symbol)]
        return mapping
