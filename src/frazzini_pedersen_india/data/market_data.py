"""Loads the market index, the risk-free rate and the Indian factors."""

import json
import pathlib

import pandas as pd


class MarketData:
    """Reads the study's market-wide series from the data folder.

    Attributes:
        data_folder: The study's data folder.
    """

    def __init__(self, data_folder: pathlib.Path) -> None:
        """Stores the data folder.

        Args:
            data_folder: The study's data folder.

        Returns:
            None.

        Raises:
            None.
        """
        self.data_folder = data_folder

    def index_levels(self, file_name: str) -> pd.Series:
        """Reads a total return index file.

        Args:
            file_name: A file under data/nse/indices, such as
                'nifty500_tri.json'.

        Returns:
            Daily index levels indexed by date, oldest first.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        path = self.data_folder / 'nse/indices' / file_name
        frame = pd.DataFrame(json.loads(path.read_text()))
        frame['date'] = pd.to_datetime(frame['Date'], format='%d %b %Y')
        frame['level'] = pd.to_numeric(
            frame['TotalReturnsIndex'], errors='coerce'
        )
        frame = frame.dropna(subset=['level'])
        frame = frame.drop_duplicates('date').sort_values('date')
        return frame.set_index('date')['level']

    def index_returns_on(
        self, file_name: str, sessions: pd.DatetimeIndex
    ) -> pd.Series:
        """Gives an index's return from each session to the next.

        A session missing from the index, or an index day that is not a
        session, is bridged by compounding.

        Args:
            file_name: An index file under data/nse/indices.
            sessions: The share market's sessions.

        Returns:
            Returns indexed by session, NaN for the first session.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        levels = self.index_levels(file_name)
        on_sessions = levels.reindex(sessions)
        on_sessions = on_sessions.ffill()
        return on_sessions.pct_change()

    def monthly_risk_free(self) -> pd.Series:
        """Joins IIMA's risk-free rate with the 2026 T-bill estimate.

        IIMA's series is used to December 2025. After that the mean of each
        month's 91-day T-bill cut-off yields is converted to a monthly rate
        as (1 + y) ** (1 / 12) - 1.

        Args:
            None.

        Returns:
            Monthly risk-free returns as decimals, indexed by month.

        Raises:
            FileNotFoundError: If an input file does not exist.
        """
        factors = self.factors()
        rate = factors['RF'].dropna()
        auctions = pd.read_csv(self.data_folder / 'nse/tbill_auctions.csv')
        auctions['date'] = pd.to_datetime(auctions['date'], format='%b %d, %Y')
        month = auctions['date'].dt.to_period('M')
        yields = auctions.groupby(month)['yield_91_day_ytm'].mean() / 100.0
        monthly = (1.0 + yields) ** (1.0 / 12.0) - 1.0
        later = monthly[monthly.index > rate.index.max()]
        return pd.concat([rate, later]).sort_index()

    def factors(self) -> pd.DataFrame:
        """Reads IIMA's monthly factors.

        Args:
            None.

        Returns:
            A table indexed by month with decimal columns SMB, HML, WML, MF
            and RF.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        paths = sorted((self.data_folder / 'nse/iima').glob('*.csv'))
        frame = pd.read_csv(paths[-1], na_values=['NA'])
        frame.index = pd.PeriodIndex(frame.pop('Date'), freq='M')
        return frame / 100.0
