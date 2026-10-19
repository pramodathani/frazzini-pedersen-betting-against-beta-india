"""Runs the main specification and writes its summary tables."""

import pathlib
import sys

import pandas as pd
from brahmagupta.backtest import Backtest
from brahmagupta.costs.delivery_costs import DeliveryCosts

from frazzini_pedersen_india.bab.portfolio_scorer import PortfolioScorer
from frazzini_pedersen_india.bab.study_inputs import StudyInputs
from frazzini_pedersen_india.bab.weight_schedule import WeightSchedule


class RunMainApplication:
    """Command-line step for the main specification."""

    def run(
        self, data_folder: pathlib.Path, results_folder: pathlib.Path
    ) -> None:
        """Backtests every portfolio of the main specification.

        Args:
            data_folder: The study's data folder.
            results_folder: Where the tables are written.

        Returns:
            None.

        Raises:
            FileNotFoundError: If an input file is missing.
        """
        derived = data_folder / 'derived'
        betas = pd.read_parquet(derived / 'betas_month_end.parquet')
        values = pd.read_parquet(derived / 'median_traded_value.parquet')
        traded = pd.read_parquet(derived / 'traded_in_month.parquet')
        inputs = StudyInputs(data_folder)
        dates = inputs.formation_dates()
        schedule = WeightSchedule().build(betas, values, dates, traded)
        excess = inputs.monthly_excess()
        market_excess = inputs.market_excess()
        scorer = PortfolioScorer(inputs.factors, market_excess)
        summaries = []
        series = {}
        for name, weights in schedule.items():
            impact = 0.003 if 'full' in name else 0.001
            result = Backtest(excess, weights, DeliveryCosts(impact)).run()
            frame = result.to_frame()
            series[f'{name}_gross'] = frame['gross_return']
            series[f'{name}_net'] = frame['net_return']
            for label, column in (
                ('gross', 'gross_return'),
                ('net', 'net_return'),
            ):
                summaries.append(
                    scorer.score(
                        name,
                        label,
                        frame[column],
                        frame['turnover'],
                        frame['holding_count'],
                        frame['unpriced_weight'],
                    )
                )
        series['market_excess'] = market_excess.reindex(excess.index)
        monthly_path = results_folder / 'main_monthly_excess_returns.csv'
        pd.DataFrame(series).to_csv(monthly_path)
        summary_path = results_folder / 'main_summary.csv'
        pd.DataFrame(summaries).to_csv(summary_path, index=False)


if __name__ == '__main__':
    RunMainApplication().run(
        pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    )
