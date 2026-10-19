"""Builds the monthly target weights of every portfolio in the study."""

import pandas as pd

from frazzini_pedersen_india.bab.portfolio_builder import PortfolioBuilder


class WeightSchedule:
    """Turns month-end betas into target weights for the next month.

    Attributes:
        liquid_count: How many of the most traded shares form the liquid
            universe.
        builder: The portfolio builder.
    """

    def __init__(self, liquid_count: int = 500) -> None:
        """Stores the size of the liquid universe.

        Args:
            liquid_count: Number of most traded shares in the liquid
                universe.

        Returns:
            None.

        Raises:
            None.
        """
        self.liquid_count = liquid_count
        self.builder = PortfolioBuilder()

    def liquid_flags(
        self, betas: pd.Series, median_value: pd.Series
    ) -> pd.Series:
        """Flags the most traded of the shares that have a beta.

        Args:
            betas: Betas of the eligible shares, indexed by symbol.
            median_value: Median daily traded value per symbol.

        Returns:
            True for the liquid_count shares with the highest traded value.

        Raises:
            None.
        """
        values = median_value.reindex(betas.index).fillna(0.0)
        top = values.nlargest(self.liquid_count).index
        return pd.Series(betas.index.isin(top), index=betas.index)

    def build(
        self,
        betas: pd.DataFrame,
        median_value: pd.DataFrame,
        formation_dates: list[pd.Timestamp],
    ) -> dict[str, pd.DataFrame]:
        """Builds target weights for every portfolio and holding month.

        The weights formed at a month-end are labelled with the next month,
        the month they are held.

        Args:
            betas: Month-end betas, dates by shares.
            median_value: Median traded values on the same dates.
            formation_dates: The month-ends at which to form portfolios.

        Returns:
            A dictionary from portfolio name to a table of holding months by
            shares. The names are full_D1 to full_D10 (all shares with a beta,
            decile cut points from the liquid shares), liquid_D1 to
            liquid_D10, bab_full, bab_liquid and for the liquid universe
            bab_low_leg and bab_low_leg_levered.

        Raises:
            KeyError: If a formation date is missing from the inputs.
        """
        rows = {}
        for date in formation_dates:
            rows[date] = self.weights_at(
                betas.loc[date].dropna(), median_value.loc[date]
            )
        names = list(next(iter(rows.values())).keys())
        result = {}
        for name in names:
            periods = []
            frames = []
            for date, weights in rows.items():
                periods.append(date.to_period('M') + 1)
                frames.append(weights[name])
            table = pd.DataFrame(frames, index=pd.PeriodIndex(periods))
            result[name] = table.fillna(0.0)
        return result

    def weights_at(
        self, betas: pd.Series, median_value: pd.Series
    ) -> dict[str, pd.Series]:
        """Builds every portfolio's weights at one formation date.

        Args:
            betas: Betas of the shares that have one, indexed by symbol.
            median_value: Median traded value per symbol.

        Returns:
            A dictionary from portfolio name to a weight series.

        Raises:
            ValueError: If no share has a beta.
        """
        liquid = self.liquid_flags(betas, median_value)
        liquid_betas = betas[liquid]
        output = {}
        full_deciles = self.builder.decile_weights(betas, liquid)
        liquid_deciles = self.builder.decile_weights(liquid_betas, liquid)
        for decile in range(1, 11):
            output[f'full_D{decile}'] = full_deciles[decile]
            output[f'liquid_D{decile}'] = liquid_deciles[decile]
        low, high, low_beta, high_beta = self.builder.bab_weights(
            betas, liquid
        )
        output['bab_full'] = self.builder.bab_target(
            low, high, low_beta, high_beta
        )
        low, high, low_beta, high_beta = self.builder.bab_weights(
            liquid_betas, liquid
        )
        output['bab_liquid'] = self.builder.bab_target(
            low, high, low_beta, high_beta
        )
        output['bab_low_leg'] = low
        output['bab_low_leg_levered'] = low / low_beta
        return output
