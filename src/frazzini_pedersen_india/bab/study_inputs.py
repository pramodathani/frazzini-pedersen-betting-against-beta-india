"""Loads the study's inputs once and serves them to the runners."""

import pathlib

import pandas as pd

from frazzini_pedersen_india.bab.beta_estimator import BetaEstimator
from frazzini_pedersen_india.bab.return_panel import ReturnPanel
from frazzini_pedersen_india.data.market_data import MarketData


class StudyInputs:
    """The return panel, market, risk-free rate and factors.

    Attributes:
        data_folder: The study's data folder.
        panel: The daily and monthly return matrices.
        market: Daily NIFTY 500 total returns on the sessions.
        month_ends: The last session of each month.
        risk_free: Monthly risk-free returns.
        factors: IIMA's monthly factors.
        first_formation: First formation date of the main sample.
        last_formation: Last formation date of the main sample.
    """

    first_formation = pd.Timestamp('2008-01-01')
    last_formation = pd.Timestamp('2026-08-31')

    def __init__(self, data_folder: pathlib.Path) -> None:
        """Reads the returns and the market series.

        Args:
            data_folder: The study's data folder.

        Returns:
            None.

        Raises:
            FileNotFoundError: If an input file is missing.
        """
        self.data_folder = data_folder
        returns = pd.read_parquet(
            data_folder / 'derived/daily_returns.parquet'
        )
        counts = returns.groupby('date')['symbol'].count()
        sessions = pd.DatetimeIndex(counts[counts >= 100].index)
        self.panel = ReturnPanel(returns, sessions)
        market_data = MarketData(data_folder)
        self.market = market_data.index_returns_on(
            'nifty500_tri.json', sessions
        ).fillna(0.0)
        self.month_ends = self.panel.month_ends()
        self.risk_free = market_data.monthly_risk_free()
        self.factors = market_data.factors()
        self.market_data = market_data

    def formation_dates(self) -> list[pd.Timestamp]:
        """Lists the month-ends at which the main sample forms portfolios.

        Args:
            None.

        Returns:
            Month-end sessions from the first to the last formation date.

        Raises:
            None.
        """
        dates = []
        for date in self.month_ends:
            if self.first_formation <= date <= self.last_formation:
                dates.append(date)
        return dates

    def betas(self, estimator: BetaEstimator) -> pd.DataFrame:
        """Estimates month-end betas with the given estimator.

        Args:
            estimator: The beta estimator to use.

        Returns:
            Betas by month-end and share.

        Raises:
            None.
        """
        return estimator.estimate(
            self.panel.daily_clean, self.market, self.month_ends
        )

    def monthly_excess(self, skip_first_session: bool = False) -> pd.DataFrame:
        """Gives monthly returns in excess of the risk-free rate.

        Args:
            skip_first_session: Leave out each month's first session.

        Returns:
            Months by shares, restricted to the main holding months.

        Raises:
            None.
        """
        monthly = self.panel.monthly_returns(skip_first_session)
        free = self.risk_free.reindex(monthly.index)
        excess = monthly.sub(free, axis=0)
        dates = self.formation_dates()
        first = dates[0].to_period('M') + 1
        last = dates[-1].to_period('M') + 1
        return excess.loc[first:last]

    def market_excess(self) -> pd.Series:
        """Gives the NIFTY 500's monthly excess return.

        Args:
            None.

        Returns:
            Monthly NIFTY 500 total return minus the risk-free rate.

        Raises:
            None.
        """
        months = self.market.index.to_period('M')
        monthly = (1.0 + self.market).groupby(months).prod() - 1.0
        return monthly - self.risk_free.reindex(monthly.index)
