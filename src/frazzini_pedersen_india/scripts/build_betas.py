"""Estimates each share's ex-ante beta at every month-end."""

import pathlib
import sys

import pandas as pd

from frazzini_pedersen_india.bab.beta_estimator import BetaEstimator
from frazzini_pedersen_india.bab.return_panel import ReturnPanel
from frazzini_pedersen_india.data.market_data import MarketData
from frazzini_pedersen_india.data.share_classifier import ShareClassifier


class BuildBetasApplication:
    """Command-line step that writes the month-end betas and liquidity."""

    def run(self, data_folder: pathlib.Path) -> None:
        """Builds betas, monthly returns and median traded values.

        Args:
            data_folder: The study's data folder.

        Returns:
            None.

        Raises:
            FileNotFoundError: If an input file is missing.
        """
        derived = data_folder / 'derived'
        prices = pd.read_parquet(
            derived / 'prices_2003.parquet', columns=['symbol', 'isin']
        )
        excluded = ShareClassifier().excluded_symbols(prices)
        returns = pd.read_parquet(derived / 'daily_returns.parquet')
        returns = returns[~returns['symbol'].isin(excluded)]
        counts = returns.groupby('date')['symbol'].count()
        sessions = pd.DatetimeIndex(counts[counts >= 100].index)
        panel = ReturnPanel(returns, sessions)
        market = MarketData(data_folder).index_returns_on(
            'nifty500_tri.json', sessions
        )
        market = market.fillna(0.0)
        month_ends = panel.month_ends()
        estimator = BetaEstimator()
        betas = estimator.estimate(panel.daily_clean, market, month_ends)
        betas.to_parquet(derived / 'betas_month_end.parquet')
        panel.monthly_returns().to_parquet(derived / 'monthly_returns.parquet')
        median_value = panel.median_traded_value(month_ends)
        median_value.to_parquet(derived / 'median_traded_value.parquet')
        market.to_frame('market').to_parquet(derived / 'market_daily.parquet')
        print('sessions', len(sessions), 'shares', betas.shape[1])
        print('month ends', len(month_ends))
        print('betas present', int(betas.notna().sum().sum()))


if __name__ == '__main__':
    BuildBetasApplication().run(pathlib.Path(sys.argv[1]))
