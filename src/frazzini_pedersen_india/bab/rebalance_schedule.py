"""Holds portfolios between rebalances instead of resetting monthly."""

import pandas as pd


class RebalanceSchedule:
    """Turns monthly target weights into targets that rebalance less often."""

    def hold_between(
        self,
        weights: pd.DataFrame,
        excess_returns: pd.DataFrame,
        every: int,
    ) -> pd.DataFrame:
        """Rebalances every few months and lets weights drift in between.

        In a month that is not a rebalance month the target is the previous
        month's weights after they drift with that month's returns, so the
        engine sees no trading.

        Args:
            weights: Monthly target weights, months by shares.
            excess_returns: Monthly returns used for the drift, with at least
                the same months and shares.
            every: Rebalance every this many months, starting with the first.

        Returns:
            A table of the same shape with the drifted weights in the months
            between rebalances.

        Raises:
            ValueError: If every is below one.
        """
        if every < 1:
            raise ValueError('every must be at least one')
        returns = excess_returns.reindex(
            index=weights.index, columns=weights.columns
        ).fillna(0.0)
        result = weights.copy()
        for position in range(1, len(weights)):
            if position % every == 0:
                continue
            previous = result.iloc[position - 1]
            grown = previous * (1.0 + returns.iloc[position - 1])
            value = (1.0 - previous.sum()) + grown.sum()
            result.iloc[position] = grown / value
        return result
