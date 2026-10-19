"""Runs the main specification and writes its summary tables."""

import pathlib
import sys

import pandas as pd
from brahmagupta.backtest import Backtest
from brahmagupta.costs.delivery_costs import DeliveryCosts
from brahmagupta.performance_report import PerformanceReport

from frazzini_pedersen_india.bab.factor_regression import FactorRegression
from frazzini_pedersen_india.bab.weight_schedule import WeightSchedule
from frazzini_pedersen_india.data.market_data import MarketData


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
        monthly = pd.read_parquet(derived / 'monthly_returns.parquet')
        traded = pd.read_parquet(derived / 'traded_in_month.parquet')
        market_data = MarketData(data_folder)
        risk_free = market_data.monthly_risk_free()
        factors = market_data.factors()
        formation_dates = []
        for date in betas.index:
            if date >= pd.Timestamp('2008-01-01') and date < pd.Timestamp(
                '2026-09-01'
            ):
                formation_dates.append(date)
        schedule = WeightSchedule().build(
            betas, values, formation_dates, traded
        )
        excess = monthly.sub(risk_free.reindex(monthly.index), axis=0)
        first = pd.Period(formation_dates[0], 'M') + 1
        last = pd.Period(formation_dates[-1], 'M') + 1
        excess = excess.loc[first:last]
        market = self.market_monthly(derived, monthly.index)
        market_excess = market - risk_free.reindex(market.index)
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
                    self.summarise(
                        name, label, frame, column, factors, market_excess
                    )
                )
        series['market_excess'] = market_excess.loc[first:last]
        pd.DataFrame(series).to_csv(
            results_folder / 'main_monthly_excess_returns.csv'
        )
        pd.DataFrame(summaries).to_csv(
            results_folder / 'main_summary.csv', index=False
        )

    def market_monthly(
        self, derived: pathlib.Path, index: pd.PeriodIndex
    ) -> pd.Series:
        """Compounds the daily NIFTY 500 returns into months.

        Args:
            derived: The derived data folder.
            index: The months wanted.

        Returns:
            Monthly NIFTY 500 total returns.

        Raises:
            FileNotFoundError: If the daily file is missing.
        """
        daily = pd.read_parquet(derived / 'market_daily.parquet')['market']
        compounded = (1.0 + daily).groupby(
            daily.index.to_period('M')
        ).prod() - 1.0
        return compounded.reindex(index)

    def summarise(
        self,
        name: str,
        label: str,
        frame: pd.DataFrame,
        column: str,
        factors: pd.DataFrame,
        market_excess: pd.Series,
    ) -> dict:
        """Scores one return series.

        Args:
            name: The portfolio's name.
            label: 'gross' or 'net'.
            frame: The backtest's table.
            column: The column holding the returns to score.
            factors: IIMA factors.
            market_excess: The NIFTY 500 excess return by month.

        Returns:
            A row of statistics.

        Raises:
            ValueError: If the series has no return.
        """
        returns = frame[column].dropna()
        report = PerformanceReport(returns).summary()
        regression = FactorRegression()
        capm = regression.alpha(returns, market_excess.to_frame('MKT'))
        three = regression.alpha(returns, factors[['MF', 'SMB', 'HML']])
        four = regression.alpha(returns, factors[['MF', 'SMB', 'HML', 'WML']])
        return {
            'portfolio': name,
            'costs': label,
            'months': report['periods'],
            'mean_monthly': report['mean'],
            'nw_t': report['newey_west_t'],
            'sharpe': report['sharpe'],
            'volatility_annual': report['volatility_annual'],
            'max_drawdown': report['maximum_drawdown'],
            'capm_alpha': capm['alpha'],
            'capm_alpha_t': capm['alpha_t'],
            'capm_beta': capm['loading_MKT'],
            'ff3_alpha': three['alpha'],
            'ff3_alpha_t': three['alpha_t'],
            'ff4_alpha': four['alpha'],
            'ff4_alpha_t': four['alpha_t'],
            'turnover_mean': frame['turnover'].mean(),
            'holdings_mean': frame['holding_count'].mean(),
            'unpriced_weight_mean': frame['unpriced_weight'].mean(),
        }


if __name__ == '__main__':
    RunMainApplication().run(
        pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    )
