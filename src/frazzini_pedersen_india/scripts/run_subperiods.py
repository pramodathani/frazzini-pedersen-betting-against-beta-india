"""Scores the main portfolios in consecutive subperiods."""

import pathlib
import sys

import pandas as pd
from brahmagupta.return_statistics import ReturnStatistics


class RunSubperiodsApplication:
    """Command-line step splitting the sample into equal parts.

    Attributes:
        portfolios: The portfolios scored.
        parts: The number of subperiods.
    """

    portfolios = ('bab_full', 'bab_liquid', 'liquid_D1', 'full_D1')
    parts = 3

    def run(self, results_folder: pathlib.Path) -> None:
        """Writes results/subperiods.csv.

        Args:
            results_folder: The results folder holding the monthly series.

        Returns:
            None.

        Raises:
            FileNotFoundError: If the monthly file is missing.
        """
        monthly = pd.read_csv(
            results_folder / 'main_monthly_excess_returns.csv', index_col=0
        )
        statistics = ReturnStatistics()
        size = len(monthly) // self.parts
        rows = []
        for part in range(self.parts):
            start = part * size
            stop = len(monthly) if part == self.parts - 1 else start + size
            block = monthly.iloc[start:stop]
            for name in self.portfolios:
                for cost in ('gross', 'net'):
                    series = block[f'{name}_{cost}']
                    mean, t_statistic = statistics.newey_west_mean_and_t(
                        series
                    )
                    rows.append(
                        {
                            'portfolio': name,
                            'costs': cost,
                            'first_month': block.index[0],
                            'last_month': block.index[-1],
                            'months': len(block),
                            'mean_monthly': mean,
                            'nw_t': t_statistic,
                        }
                    )
        pd.DataFrame(rows).to_csv(
            results_folder / 'subperiods.csv', index=False
        )


if __name__ == '__main__':
    RunSubperiodsApplication().run(pathlib.Path(sys.argv[1]))
