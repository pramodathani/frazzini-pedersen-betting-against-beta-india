"""Runs the robustness variants of the main specification."""

import pathlib
import sys

import pandas as pd
from brahmagupta.backtest import Backtest
from brahmagupta.costs.delivery_costs import DeliveryCosts

from frazzini_pedersen_india.bab.beta_estimator import BetaEstimator
from frazzini_pedersen_india.bab.delisting_stress import DelistingStress
from frazzini_pedersen_india.bab.portfolio_scorer import PortfolioScorer
from frazzini_pedersen_india.bab.study_inputs import StudyInputs
from frazzini_pedersen_india.bab.weight_schedule import WeightSchedule


class RunVariantsApplication:
    """Command-line step that scores each robustness variant.

    Attributes:
        reported: The portfolios scored in every variant.
    """

    reported = ('bab_full', 'bab_liquid', 'full_D1', 'liquid_D1')

    def run(
        self, data_folder: pathlib.Path, results_folder: pathlib.Path
    ) -> None:
        """Scores every variant and writes results/variants_summary.csv.

        Args:
            data_folder: The study's data folder.
            results_folder: Where the table is written.

        Returns:
            None.

        Raises:
            FileNotFoundError: If an input file is missing.
        """
        derived = data_folder / 'derived'
        inputs = StudyInputs(data_folder)
        values = pd.read_parquet(derived / 'median_traded_value.parquet')
        traded = pd.read_parquet(derived / 'traded_in_month.parquet')
        main_betas = pd.read_parquet(derived / 'betas_month_end.parquet')
        scorer = PortfolioScorer(inputs.factors, inputs.market_excess())
        dates = inputs.formation_dates()
        excess = inputs.monthly_excess()
        rows = []
        specs = [
            ('main', main_betas, WeightSchedule(), excess),
            (
                'liquid_300',
                main_betas,
                WeightSchedule(liquid_count=300),
                excess,
            ),
            (
                'liquid_1000',
                main_betas,
                WeightSchedule(liquid_count=1000),
                excess,
            ),
            (
                'drop_least_traded_half',
                main_betas,
                WeightSchedule(minimum_value_quantile=0.5),
                excess,
            ),
            (
                'delay_one_session',
                main_betas,
                WeightSchedule(),
                inputs.monthly_excess(skip_first_session=True),
            ),
        ]
        for loss in (-1.0, -0.3):
            stressed = DelistingStress().apply(excess, loss, inputs.risk_free)
            specs.append(
                (f'delisting_{loss}', main_betas, WeightSchedule(), stressed)
            )
        estimators = [
            (
                'correlation_3_year',
                BetaEstimator(
                    correlation_days=756, minimum_correlation_days=450
                ),
            ),
            (
                'correlation_1_year',
                BetaEstimator(
                    correlation_days=252, minimum_correlation_days=120
                ),
            ),
            ('no_shrinkage', BetaEstimator(shrinkage_weight=1.0)),
            ('five_day_overlap', BetaEstimator(overlap_days=5)),
        ]
        for name, estimator in estimators:
            specs.append(
                (name, inputs.betas(estimator), WeightSchedule(), excess)
            )
        for name, betas, schedule, returns in specs:
            print(name, flush=True)
            rows.extend(
                self.score_variant(
                    name,
                    betas,
                    schedule,
                    returns,
                    values,
                    traded,
                    dates,
                    scorer,
                )
            )
            pd.DataFrame(rows).to_csv(
                results_folder / 'variants_summary.csv', index=False
            )

    def score_variant(
        self,
        name: str,
        betas: pd.DataFrame,
        schedule: WeightSchedule,
        returns: pd.DataFrame,
        values: pd.DataFrame,
        traded: pd.DataFrame,
        dates: list[pd.Timestamp],
        scorer: PortfolioScorer,
    ) -> list[dict]:
        """Backtests one variant and scores its reported portfolios.

        Args:
            name: The variant's name.
            betas: Month-end betas to use.
            schedule: The weight schedule to use.
            returns: Monthly excess returns to earn.
            values: Median traded values.
            traded: Whether each share traded in each formation month.
            dates: Formation dates.
            scorer: The scorer.

        Returns:
            Rows of statistics, gross and net for each reported portfolio.

        Raises:
            ValueError: If a portfolio cannot be formed.
        """
        weights = schedule.build(betas, values, dates, traded)
        rows = []
        for portfolio in self.reported:
            impact = 0.003 if 'full' in portfolio else 0.001
            result = Backtest(
                returns, weights[portfolio], DeliveryCosts(impact)
            ).run()
            frame = result.to_frame()
            for label, column in (
                ('gross', 'gross_return'),
                ('net', 'net_return'),
            ):
                row = scorer.score(
                    portfolio,
                    label,
                    frame[column],
                    frame['turnover'],
                    frame['holding_count'],
                    frame['unpriced_weight'],
                )
                row['variant'] = name
                rows.append(row)
        return rows


if __name__ == '__main__':
    RunVariantsApplication().run(
        pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    )
