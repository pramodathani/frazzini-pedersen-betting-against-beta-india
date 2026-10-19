"""Builds daily total returns for shares from closes and corporate actions."""

import pandas as pd


class DailyReturnBuilder:
    """Adjusts closes for corporate actions and computes daily returns.

    Attributes:
        lowest_return: Daily returns at or below this are data errors.
        highest_return: Daily returns at or above this are data errors.
    """

    lowest_return = -0.5
    highest_return = 1.0

    def build(
        self, prices: pd.DataFrame, actions: pd.DataFrame
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Computes each share's return from one session to its next.

        On the first session on or after an ex-date the return is
        (close x price factor + dividend) / previous close - 1, where the
        previous close is the share's own last close in the data.

        Args:
            prices: A table with columns date, symbol and close.
            actions: A table with columns symbol, ex_date, price_factor and
                dividend, as CorporateActionTable.load returns.

        Returns:
            A pair. The first is a table with columns date, symbol, return,
            gap_days (calendar days since the share's previous session) and
            traded_value. The second lists the returns set to zero as data
            errors, with the raw return and the symbol and date.

        Raises:
            KeyError: If a table lacks a required column.
        """
        frame = prices.sort_values(['symbol', 'date']).reset_index(drop=True)
        frame['price_factor'] = 1.0
        frame['dividend'] = 0.0
        if len(actions) > 0:
            frame = self.attach_actions(frame, actions)
        grouped = frame.groupby('symbol')
        frame['previous_close'] = grouped['close'].shift(1)
        frame['previous_date'] = grouped['date'].shift(1)
        adjusted = frame['close'] * frame['price_factor'] + frame['dividend']
        frame['return'] = adjusted / frame['previous_close'] - 1.0
        frame['gap_days'] = (frame['date'] - frame['previous_date']).dt.days
        frame = frame.dropna(subset=['return'])
        invalid = (frame['return'] <= self.lowest_return) | (
            frame['return'] >= self.highest_return
        )
        errors = frame.loc[invalid, ['date', 'symbol', 'return']].copy()
        frame.loc[invalid, 'return'] = 0.0
        columns = ['date', 'symbol', 'return', 'gap_days', 'traded_value']
        return frame[columns].reset_index(drop=True), errors

    def attach_actions(
        self, frame: pd.DataFrame, actions: pd.DataFrame
    ) -> pd.DataFrame:
        """Moves each action onto the share's first session on or after it.

        Args:
            frame: Prices sorted by symbol and date.
            actions: The corporate action table.

        Returns:
            The prices with price_factor and dividend filled in on the
            sessions where actions take effect. Several actions landing on
            one session are combined.

        Raises:
            KeyError: If a column is missing.
        """
        sessions = frame[['symbol', 'date']].copy()
        sessions['session_date'] = sessions['date']
        sessions = sessions.sort_values('date')
        ordered = actions.sort_values('ex_date')
        matched = pd.merge_asof(
            ordered,
            sessions,
            left_on='ex_date',
            right_on='date',
            by='symbol',
            direction='forward',
        )
        matched = matched.dropna(subset=['session_date'])
        combined = matched.groupby(['symbol', 'session_date']).agg(
            price_factor=('price_factor', 'prod'),
            dividend=('dividend', 'sum'),
        )
        combined = combined.reset_index().rename(
            columns={'session_date': 'date'}
        )
        frame = frame.drop(columns=['price_factor', 'dividend'])
        frame = frame.merge(combined, on=['symbol', 'date'], how='left')
        frame['price_factor'] = frame['price_factor'].fillna(1.0)
        frame['dividend'] = frame['dividend'].fillna(0.0)
        return frame
