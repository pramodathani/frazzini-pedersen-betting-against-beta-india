"""Arranges daily share returns into the matrices the study works on."""

import numpy as np
import pandas as pd


class ReturnPanel:
    """Daily and monthly return matrices on a common session calendar.

    Attributes:
        sessions: The trading dates, oldest first.
        daily_full: Every daily return, sessions by shares, including
            returns that span sessions the share did not trade.
        daily_clean: The same, but with returns that span missed sessions
            set to NaN, for estimating betas.
        traded_value: Daily traded value, sessions by shares.
    """

    def __init__(
        self,
        returns: pd.DataFrame,
        sessions: pd.DatetimeIndex,
    ) -> None:
        """Pivots the long return table onto the calendar.

        Args:
            returns: A table with columns date, symbol, return and
                traded_value, one row per share and session.
            sessions: The market's trading dates.

        Returns:
            None.

        Raises:
            KeyError: If a column is missing.
        """
        frame = returns[returns['date'].isin(sessions)].copy()
        frame = frame.sort_values(['symbol', 'date'])
        frame['position'] = sessions.get_indexer(frame['date'])
        step = frame.groupby('symbol')['position'].diff()
        frame['clean_return'] = frame['return'].where(step == 1)
        self.sessions = sessions
        self.daily_full = frame.pivot(
            index='date', columns='symbol', values='return'
        ).reindex(sessions)
        self.daily_clean = frame.pivot(
            index='date', columns='symbol', values='clean_return'
        ).reindex(sessions)
        self.traded_value = frame.pivot(
            index='date', columns='symbol', values='traded_value'
        ).reindex(sessions)

    def month_ends(self) -> list[pd.Timestamp]:
        """Finds the last session of each calendar month.

        Args:
            None.

        Returns:
            The month-end session dates, oldest first.

        Raises:
            None.
        """
        series = pd.Series(self.sessions, index=self.sessions)
        last = series.groupby(self.sessions.to_period('M')).max()
        return list(last)

    def monthly_returns(self) -> pd.DataFrame:
        """Compounds each share's daily returns within each month.

        Args:
            None.

        Returns:
            A table with one row per month, labelled by period, and one
            column per share. A share with no return in a month is NaN.

        Raises:
            None.
        """
        logs = np.log1p(self.daily_full)
        months = logs.index.to_period('M')
        summed = logs.groupby(months).sum(min_count=1)
        return np.expm1(summed)

    def median_traded_value(
        self, formation_dates: list[pd.Timestamp], window: int = 252
    ) -> pd.DataFrame:
        """Finds each share's median daily traded value before each date.

        Args:
            formation_dates: Dates, each a session, up to which to look.
            window: The number of sessions in the look-back.

        Returns:
            A table of formation dates by shares.

        Raises:
            KeyError: If a date is not a session.
        """
        rows = []
        for date in formation_dates:
            position = self.sessions.get_loc(date)
            start = max(0, position - window + 1)
            block = self.traded_value.iloc[start : position + 1]
            rows.append(block.median(skipna=True))
        return pd.DataFrame(rows, index=pd.DatetimeIndex(formation_dates))

    def traded_in_month(
        self, formation_dates: list[pd.Timestamp]
    ) -> pd.DataFrame:
        """Says whether each share traded at all in each formation month.

        Args:
            formation_dates: Month-end sessions.

        Returns:
            A True or False table of formation dates by shares.

        Raises:
            None.
        """
        months = self.traded_value.index.to_period('M')
        traded = self.traded_value.notna().groupby(months).any()
        periods = pd.PeriodIndex(
            [date.to_period('M') for date in formation_dates]
        )
        table = traded.loc[periods]
        table.index = pd.DatetimeIndex(formation_dates)
        return table
