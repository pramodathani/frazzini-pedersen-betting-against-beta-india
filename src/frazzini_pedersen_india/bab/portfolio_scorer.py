"""Scores a portfolio's monthly excess returns with the study's statistics."""

import pandas as pd
from brahmagupta.performance_report import PerformanceReport

from frazzini_pedersen_india.bab.factor_regression import FactorRegression


class PortfolioScorer:
    """Turns one return series into one row of statistics.

    Attributes:
        factors: IIMA's monthly factors, with MF the market excess return.
        market_excess: NIFTY 500 total return minus the risk-free rate.
    """

    def __init__(
        self, factors: pd.DataFrame, market_excess: pd.Series
    ) -> None:
        """Stores the factors the alphas are measured against.

        Args:
            factors: IIMA's monthly factors, with columns MF, SMB, HML, WML.
            market_excess: NIFTY 500 monthly excess return by month.

        Returns:
            None.

        Raises:
            None.
        """
        self.factors = factors
        self.market_excess = market_excess

    def score(
        self,
        name: str,
        label: str,
        returns: pd.Series,
        turnover: pd.Series | None = None,
        holdings: pd.Series | None = None,
        unpriced: pd.Series | None = None,
    ) -> dict:
        """Scores one series of monthly excess returns.

        Args:
            name: The portfolio's name.
            label: 'gross' or 'net'.
            returns: Monthly excess returns by month.
            turnover: Bought plus sold as a share of value, by month.
            holdings: Number of holdings by month.
            unpriced: Absolute weight on shares without a return, by month.

        Returns:
            A row with months, mean, Newey-West t, Sharpe ratio, volatility,
            worst drawdown, CAPM, three-factor and four-factor alphas with
            Newey-West t-statistics, and the trading statistics given.

        Raises:
            ValueError: If the series has no return.
        """
        clean = returns.dropna()
        report = PerformanceReport(clean).summary()
        regression = FactorRegression()
        capm = regression.alpha(clean, self.market_excess.to_frame('MKT'))
        three = regression.alpha(clean, self.factors[['MF', 'SMB', 'HML']])
        four = regression.alpha(
            clean, self.factors[['MF', 'SMB', 'HML', 'WML']]
        )
        row = {
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
            'ff4_months': four['periods'],
        }
        if turnover is not None:
            row['turnover_mean'] = turnover.mean()
        if holdings is not None:
            row['holdings_mean'] = holdings.mean()
        if unpriced is not None:
            row['unpriced_weight_mean'] = unpriced.mean()
        return row
