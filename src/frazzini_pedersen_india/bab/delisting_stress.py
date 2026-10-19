"""Charges a loss in the month after a share's last return."""

import pandas as pd


class DelistingStress:
    """Adds a terminal loss to shares that stop trading.

    The bhavcopies hold shares while they traded but not what holders got
    when a share was delisted, so the study tests how much the results lean
    on that.
    """

    def apply(
        self,
        excess_returns: pd.DataFrame,
        terminal_return: float,
        risk_free: pd.Series,
    ) -> pd.DataFrame:
        """Inserts a terminal return after each share's last return.

        Args:
            excess_returns: Monthly returns in excess of the risk-free rate,
                months by shares.
            terminal_return: The total return charged, for example -1.0 for
                a total loss.
            risk_free: The monthly risk-free rate by month.

        Returns:
            A copy of the table in which each share that has no return in the
            final month gets terminal_return minus the risk-free rate in the
            month after its last return.

        Raises:
            None.
        """
        stressed = excess_returns.copy()
        has_return = excess_returns.notna()
        for symbol in excess_returns.columns:
            present = has_return[symbol]
            if not present.any():
                continue
            last_position = excess_returns.index.get_loc(
                present[present].index[-1]
            )
            if present.iloc[-1] or last_position + 1 >= len(excess_returns):
                continue
            month = excess_returns.index[last_position + 1]
            stressed.loc[month, symbol] = terminal_return - risk_free[month]
        return stressed
