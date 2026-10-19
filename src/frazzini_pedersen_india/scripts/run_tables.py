"""Runs the robustness portfolios and the long-only variants."""

import pathlib
import sys

import pandas as pd
from brahmagupta.backtest import Backtest
from brahmagupta.costs.delivery_costs import DeliveryCosts

from frazzini_pedersen_india.bab.extra_portfolios import ExtraPortfolios
from frazzini_pedersen_india.bab.idiosyncratic_volatility import (
    IdiosyncraticVolatility,
)
from frazzini_pedersen_india.bab.portfolio_scorer import PortfolioScorer
from frazzini_pedersen_india.bab.rebalance_schedule import RebalanceSchedule
from frazzini_pedersen_india.bab.study_inputs import StudyInputs
from frazzini_pedersen_india.bab.weight_schedule import WeightSchedule


class RunTablesApplication:
    """Command-line step for the robustness tables."""

    def run(
        self, data_folder: pathlib.Path, results_folder: pathlib.Path
    ) -> None:
        """Backtests the extra portfolios and writes their tables.

        Args:
            data_folder: The study's data folder.
            results_folder: Where the tables are written.

        Returns:
            None.

        Raises:
            FileNotFoundError: If an input file is missing.
        """
        derived = data_folder / 'derived'
        inputs = StudyInputs(data_folder)
        betas = pd.read_parquet(derived / 'betas_month_end.parquet')
        values = pd.read_parquet(derived / 'median_traded_value.parquet')
        traded = pd.read_parquet(derived / 'traded_in_month.parquet')
        dates = inputs.formation_dates()
        volatility = IdiosyncraticVolatility().estimate(
            inputs.panel.daily_clean, inputs.market, inputs.month_ends
        )
        portfolios = ExtraPortfolios().build(
            betas, values, traded, volatility, dates
        )
        excess = inputs.monthly_excess()
        main = WeightSchedule().build(betas, values, dates, traded)
        for name in ('liquid_D1', 'bab_low_leg', 'full_D1'):
            for every in (3, 12):
                held = RebalanceSchedule().hold_between(
                    main[name], excess, every
                )
                portfolios[f'{name}_every_{every}_months'] = held
        scorer = PortfolioScorer(inputs.factors, inputs.market_excess())
        rows = []
        series = {}
        for name, weights in portfolios.items():
            impact = 0.003 if 'full' in name or 'size' in name else 0.001
            if 'ivol' in name:
                impact = 0.003
            result = Backtest(excess, weights, DeliveryCosts(impact)).run()
            frame = result.to_frame()
            series[f'{name}_gross'] = frame['gross_return']
            series[f'{name}_net'] = frame['net_return']
            for label, column in (
                ('gross', 'gross_return'),
                ('net', 'net_return'),
            ):
                rows.append(
                    scorer.score(
                        name,
                        label,
                        frame[column],
                        frame['turnover'],
                        frame['holding_count'],
                        frame['unpriced_weight'],
                    )
                )
            print(name, flush=True)
        pd.DataFrame(rows).to_csv(
            results_folder / 'tables_summary.csv', index=False
        )
        pd.DataFrame(series).to_csv(
            results_folder / 'tables_monthly_excess_returns.csv'
        )
        self.dollar_exposure(main, results_folder)

    def dollar_exposure(
        self, main: dict[str, pd.DataFrame], results_folder: pathlib.Path
    ) -> None:
        """Writes the average dollars long and short of the BAB portfolios.

        Args:
            main: The main weight tables.
            results_folder: Where to write.

        Returns:
            None.

        Raises:
            None.
        """
        rows = []
        for name in ('bab_full', 'bab_liquid'):
            weights = main[name]
            rows.append(
                {
                    'portfolio': name,
                    'dollar_long': weights.clip(lower=0).sum(axis=1).mean(),
                    'dollar_short': (-weights)
                    .clip(lower=0)
                    .sum(axis=1)
                    .mean(),
                }
            )
        pd.DataFrame(rows).to_csv(
            results_folder / 'bab_dollar_exposure.csv', index=False
        )


if __name__ == '__main__':
    RunTablesApplication().run(
        pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    )
