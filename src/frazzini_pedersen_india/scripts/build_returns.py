"""Builds the daily adjusted return table from bhavcopies and actions."""

import pathlib
import sys

import pandas as pd

from frazzini_pedersen_india.data.corporate_actions import (
    CorporateActionTable,
)
from frazzini_pedersen_india.data.daily_returns import DailyReturnBuilder


class BuildReturnsApplication:
    """Command-line step that writes data/derived/daily_returns.parquet."""

    def run(self, data_folder: pathlib.Path) -> None:
        """Builds and saves daily returns from 2005.

        Args:
            data_folder: The study's data folder.

        Returns:
            None.

        Raises:
            FileNotFoundError: If an input file is missing.
        """
        prices = pd.read_parquet(data_folder / 'derived/prices_2003.parquet')
        paths = []
        action_folder = data_folder / 'external/earlier_corporate_actions'
        for year in range(2003, 2026):
            paths.append(action_folder / f'{year}.json')
        paths.append(data_folder / 'nse/corporate_actions/2026.json')
        actions = CorporateActionTable().load(paths)
        returns, errors = DailyReturnBuilder().build(prices, actions)
        returns = returns[returns['date'] >= '2005-01-01']
        errors = errors[errors['date'] >= '2005-01-01']
        returns.to_parquet(data_folder / 'derived/daily_returns.parquet')
        errors.to_csv(data_folder / 'derived/data_errors.csv', index=False)
        print('actions', len(actions))
        print('returns', len(returns), 'symbols', returns['symbol'].nunique())
        print('errors', len(errors))


if __name__ == '__main__':
    BuildReturnsApplication().run(pathlib.Path(sys.argv[1]))
