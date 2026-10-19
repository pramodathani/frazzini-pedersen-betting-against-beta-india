"""Alphas of a return series against factors, with Newey-West errors."""

import math

import pandas as pd
import statsmodels.api as statsmodels_api


class FactorRegression:
    """Regresses a monthly excess return series on factor returns."""

    def alpha(
        self, returns: pd.Series, factors: pd.DataFrame
    ) -> dict[str, float]:
        """Fits returns = alpha + loadings x factors.

        Args:
            returns: Monthly excess returns of the portfolio.
            factors: Monthly factor returns, one column per factor.

        Returns:
            The monthly alpha, its Newey-West t-statistic, the number of
            months, and one loading per factor named loading_<factor>.
            Everything is NaN when fewer than ten months overlap.

        Raises:
            None.
        """
        joined = pd.concat([returns.rename('y'), factors], axis=1).dropna()
        output = {'periods': float(len(joined))}
        if len(joined) < 10:
            output['alpha'] = math.nan
            output['alpha_t'] = math.nan
            for name in factors.columns:
                output[f'loading_{name}'] = math.nan
            return output
        explanatory = statsmodels_api.add_constant(
            joined[list(factors.columns)]
        )
        lags = max(1, math.floor(4.0 * (len(joined) / 100.0) ** (2.0 / 9.0)))
        fitted = statsmodels_api.OLS(joined['y'], explanatory).fit(
            cov_type='HAC', cov_kwds={'maxlags': lags}
        )
        output['alpha'] = float(fitted.params['const'])
        output['alpha_t'] = float(fitted.tvalues['const'])
        for name in factors.columns:
            output[f'loading_{name}'] = float(fitted.params[name])
        return output
