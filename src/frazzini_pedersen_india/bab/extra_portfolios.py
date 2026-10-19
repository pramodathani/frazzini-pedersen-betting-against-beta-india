"""Builds the paper's robustness portfolios beyond the main ones."""

import pandas as pd

from frazzini_pedersen_india.bab.portfolio_builder import PortfolioBuilder
from frazzini_pedersen_india.bab.weight_schedule import WeightSchedule


class ExtraPortfolios:
    """Monthly weights for the robustness portfolios.

    These are the scaled legs, equal and value weighted BAB, and BAB within
    size and idiosyncratic volatility groups.

    Attributes:
        schedule: The main weight schedule, used for the liquid flags.
        builder: The portfolio builder.
        groups: How many size and volatility groups to form.
    """

    def __init__(self, liquid_count: int = 500, groups: int = 5) -> None:
        """Stores the liquid universe size and the number of groups.

        Args:
            liquid_count: Number of most traded shares in the liquid set.
            groups: Number of size and volatility groups.

        Returns:
            None.

        Raises:
            None.
        """
        self.schedule = WeightSchedule(liquid_count)
        self.builder = PortfolioBuilder()
        self.groups = groups

    def build(
        self,
        betas: pd.DataFrame,
        values: pd.DataFrame,
        traded: pd.DataFrame,
        volatility: pd.DataFrame,
        formation_dates: list[pd.Timestamp],
    ) -> dict[str, pd.DataFrame]:
        """Builds every extra portfolio's monthly weights.

        Args:
            betas: Month-end betas.
            values: Median traded values.
            traded: Whether each share traded in each formation month.
            volatility: Idiosyncratic volatility at each month-end.
            formation_dates: Formation month-ends.

        Returns:
            A dictionary from portfolio name to a table of holding months by
            shares.

        Raises:
            KeyError: If a date is missing from an input.
        """
        rows = {}
        for date in formation_dates:
            eligible = betas.loc[date].dropna()
            flags = traded.loc[date].reindex(eligible.index)
            eligible = eligible[flags.fillna(False).astype(bool)]
            rows[date] = self.at_date(
                eligible, values.loc[date], volatility.loc[date]
            )
        names = list(next(iter(rows.values())).keys())
        result = {}
        for name in names:
            periods = []
            frames = []
            for date, weights in rows.items():
                periods.append(date.to_period('M') + 1)
                frames.append(weights.get(name, pd.Series(dtype=float)))
            table = pd.DataFrame(frames, index=pd.PeriodIndex(periods))
            result[name] = table.fillna(0.0)
        return result

    def at_date(
        self,
        betas: pd.Series,
        values: pd.Series,
        volatility: pd.Series,
    ) -> dict[str, pd.Series]:
        """Builds the extra portfolios at one formation date.

        Args:
            betas: Betas of the eligible shares.
            values: Median traded value per symbol.
            volatility: Idiosyncratic volatility per symbol.

        Returns:
            A dictionary from portfolio name to weights.

        Raises:
            ValueError: If no share has a beta.
        """
        liquid = self.schedule.liquid_flags(betas, values)
        everything = pd.Series(True, index=betas.index)
        output = {}
        low, high, low_beta, high_beta = self.builder.bab_weights(
            betas, liquid
        )
        output['full_low_leg_scaled'] = low / low_beta
        output['full_high_leg_scaled'] = high / high_beta
        liquid_betas = betas[liquid]
        low, high, low_beta, high_beta = self.builder.bab_weights(
            liquid_betas, liquid
        )
        output['liquid_low_leg_scaled'] = low / low_beta
        output['liquid_high_leg_scaled'] = high / high_beta
        output['bab_full_equal'] = self.builder.equal_weighted_bab(
            betas, liquid
        )
        output['bab_liquid_equal'] = self.builder.equal_weighted_bab(
            liquid_betas, liquid
        )
        shares_value = values.reindex(betas.index).fillna(0.0)
        output['bab_full_value'] = self.builder.value_weighted_bab(
            betas, shares_value, liquid
        )
        output['bab_liquid_value'] = self.builder.value_weighted_bab(
            liquid_betas, shares_value[liquid], liquid
        )
        self.add_groups('size', shares_value, betas, output, everything)
        shares_volatility = volatility.reindex(betas.index)
        self.add_groups('ivol', shares_volatility, betas, output, everything)
        return output

    def add_groups(
        self,
        label: str,
        characteristic: pd.Series,
        betas: pd.Series,
        output: dict[str, pd.Series],
        everything: pd.Series,
    ) -> None:
        """Adds one BAB per group of a characteristic.

        Args:
            label: Name stem, such as 'size'.
            characteristic: The grouping variable, indexed by symbol; shares
                with NaN are left out.
            betas: Betas of the eligible shares.
            output: The dictionary to add to.
            everything: A flag series with every eligible share True.

        Returns:
            None.

        Raises:
            None.
        """
        known = characteristic.dropna()
        ranks = known.rank(method='first')
        groups = pd.qcut(ranks, self.groups, labels=False)
        for group in range(self.groups):
            members = groups[groups == group].index
            group_betas = betas.reindex(members).dropna()
            if len(group_betas) < 20:
                continue
            flags = everything.reindex(group_betas.index)
            try:
                low, high, low_beta, high_beta = self.builder.bab_weights(
                    group_betas, flags
                )
            except ValueError:
                continue
            output[f'bab_{label}_Q{group + 1}'] = self.builder.bab_target(
                low, high, low_beta, high_beta
            )
