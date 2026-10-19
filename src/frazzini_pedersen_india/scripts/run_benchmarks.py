"""Compares the long-only low-beta portfolios with the benchmarks."""

import pathlib
import sys

import pandas as pd
from brahmagupta.performance_report import PerformanceReport

from frazzini_pedersen_india.bab.study_inputs import StudyInputs


class RunBenchmarksApplication:
    """Command-line step scoring long-only portfolios against indices.

    Attributes:
        candidates: The portfolio return series compared, by file and name.
    """

    candidates = (
        ('main', 'liquid_D1'),
        ('tables', 'liquid_D1_every_3_months'),
        ('tables', 'liquid_D1_every_12_months'),
        ('main', 'bab_low_leg'),
        ('tables', 'bab_low_leg_every_3_months'),
        ('main', 'full_D1'),
    )

    def run(
        self, data_folder: pathlib.Path, results_folder: pathlib.Path
    ) -> None:
        """Scores each long-only portfolio, before and after costs.

        Args:
            data_folder: The study's data folder.
            results_folder: Where the results are read and written.

        Returns:
            None.

        Raises:
            FileNotFoundError: If a result file is missing.
        """
        inputs = StudyInputs(data_folder)
        main = pd.read_csv(
            results_folder / 'main_monthly_excess_returns.csv', index_col=0
        )
        tables = pd.read_csv(
            results_folder / 'tables_monthly_excess_returns.csv', index_col=0
        )
        sources = {'main': main, 'tables': tables}
        index = pd.PeriodIndex(main.index, freq='M')
        free = inputs.risk_free.reindex(index)
        free.index = main.index
        benchmarks = self.benchmark_returns(inputs, index)
        benchmarks.index = main.index
        rows = []
        for label, series in benchmarks.items():
            rows.append(
                self.row(
                    label, 'index', series, benchmarks['NIFTY 500 TRI'], free
                )
            )
        for source, name in self.candidates:
            for cost in ('gross', 'net'):
                excess = sources[source][f'{name}_{cost}']
                total = excess + free
                rows.append(
                    self.row(
                        name,
                        cost,
                        total,
                        benchmarks['NIFTY 500 TRI'],
                        free,
                    )
                )
        pd.DataFrame(rows).to_csv(
            results_folder / 'long_only_vs_benchmarks.csv', index=False
        )

    def benchmark_returns(
        self, inputs: StudyInputs, index: pd.PeriodIndex
    ) -> pd.DataFrame:
        """Gives monthly total returns of the three benchmark indices.

        Args:
            inputs: The study inputs.
            index: The holding months.

        Returns:
            A table with one column per index.

        Raises:
            FileNotFoundError: If an index file is missing.
        """
        files = {
            'NIFTY 500 TRI': 'nifty500_tri.json',
            'NIFTY100 Low Volatility 30 TRI': 'nifty100_lowvol30_tri.json',
            'NIFTY Low Volatility 50 TRI': 'nifty_lowvol50_tri.json',
        }
        columns = {}
        for label, file_name in files.items():
            daily = inputs.market_data.index_returns_on(
                file_name, inputs.panel.sessions
            ).fillna(0.0)
            months = daily.index.to_period('M')
            monthly = (1.0 + daily).groupby(months).prod() - 1.0
            columns[label] = monthly.reindex(index)
        return pd.DataFrame(columns)

    def row(
        self,
        label: str,
        kind: str,
        total: pd.Series,
        benchmark: pd.Series,
        risk_free: pd.Series,
    ) -> dict:
        """Scores a total-return series against the NIFTY 500 TRI.

        Args:
            label: The series' name.
            kind: 'gross', 'net' or 'index'.
            total: Monthly total returns.
            benchmark: The NIFTY 500 TRI's monthly returns.
            risk_free: The monthly risk-free rate on the same months.

        Returns:
            A row with annual return, volatility, drawdown and the annual
            excess over the benchmark, from total returns, and the Sharpe
            ratio, alpha and beta, from returns in excess of the risk-free
            rate.

        Raises:
            ValueError: If the series has no return.
        """
        summary = PerformanceReport(total, benchmark).summary()
        excess_summary = PerformanceReport(
            total - risk_free, benchmark - risk_free
        ).summary()
        row = {'portfolio': label, 'costs': kind}
        for key in (
            'periods',
            'compound_annual',
            'volatility_annual',
            'maximum_drawdown',
            'benchmark_compound_annual',
            'excess_annual',
            'excess_t',
        ):
            row[key] = summary.get(key)
        row['sharpe_excess'] = excess_summary['sharpe']
        row['alpha'] = excess_summary.get('alpha')
        row['alpha_t'] = excess_summary.get('alpha_t')
        row['beta'] = excess_summary.get('beta')
        if label == 'NIFTY 500 TRI':
            row['alpha'] = None
            row['alpha_t'] = None
        return row


if __name__ == '__main__':
    RunBenchmarksApplication().run(
        pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    )
