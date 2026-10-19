"""Forms beta-sorted portfolios and BAB weights at one formation date."""

import numpy as np
import pandas as pd


class PortfolioBuilder:
    """Turns one date's betas into portfolio weights.

    The decile cut points and the BAB split come from a breakpoint set of
    shares, which plays the role the NYSE plays in the paper (p.41). The
    portfolios themselves are formed from every eligible share.
    """

    def decile_weights(
        self,
        betas: pd.Series,
        breakpoint_shares: pd.Series,
    ) -> pd.DataFrame:
        """Sorts shares into beta deciles with equal weights.

        Args:
            betas: Ex-ante betas of the eligible shares, indexed by symbol,
                with no NaN.
            breakpoint_shares: A True or False flag per symbol saying whether
                the share sets the decile cut points.

        Returns:
            A table with one column per decile, 1 for the lowest beta to 10,
            and one row per share. Each column's weights add to one.

        Raises:
            ValueError: If no breakpoint share is eligible.
        """
        flags = breakpoint_shares.reindex(betas.index).fillna(False)
        reference = betas[flags.astype(bool)]
        if len(reference) == 0:
            raise ValueError('no breakpoint shares among eligible shares')
        cuts = reference.quantile([i / 10.0 for i in range(1, 10)]).to_numpy()
        deciles = np.searchsorted(cuts, betas.to_numpy(), side='right') + 1
        weights = pd.DataFrame(0.0, index=betas.index, columns=range(1, 11))
        for decile in range(1, 11):
            members = deciles == decile
            count = members.sum()
            if count > 0:
                weights.loc[members, decile] = 1.0 / count
        return weights

    def bab_weights(
        self,
        betas: pd.Series,
        breakpoint_shares: pd.Series,
    ) -> tuple[pd.Series, pd.Series, float, float]:
        """Builds the rank-weighted low and high beta portfolios.

        Shares are ranked by beta. The split is at the rank of the breakpoint
        shares' median beta, and weights grow with the distance in rank from
        the split, each leg then scaled to add to one (paper eq. 16, p.19).
        With every share a breakpoint share and no tied betas this is the
        paper's formula.

        Args:
            betas: Ex-ante betas of the eligible shares, indexed by symbol,
                with no NaN.
            breakpoint_shares: A True or False flag per symbol saying whether
                the share sets the median.

        Returns:
            The low-beta weights, the high-beta weights, the low portfolio's
            beta and the high portfolio's beta. Each weight series adds to
            one.

        Raises:
            ValueError: If no breakpoint share is eligible or a leg is empty.
        """
        flags = breakpoint_shares.reindex(betas.index).fillna(False)
        reference = betas[flags.astype(bool)]
        if len(reference) == 0:
            raise ValueError('no breakpoint shares among eligible shares')
        cutoff = reference.median()
        ranks = betas.rank(method='average')
        split = float((betas <= cutoff).sum()) + 0.5
        distance = ranks - split
        high = distance.clip(lower=0.0)
        low = (-distance).clip(lower=0.0)
        if high.sum() == 0.0 or low.sum() == 0.0:
            raise ValueError('a BAB leg has no shares')
        high = high / high.sum()
        low = low / low.sum()
        low_beta = float((betas * low).sum())
        high_beta = float((betas * high).sum())
        return low, high, low_beta, high_beta

    def bab_target(
        self,
        low: pd.Series,
        high: pd.Series,
        low_beta: float,
        high_beta: float,
    ) -> pd.Series:
        """Combines the legs into self-financing BAB weights on excess returns.

        Args:
            low: Low-beta leg weights adding to one.
            high: High-beta leg weights adding to one.
            low_beta: The low leg's beta.
            high_beta: The high leg's beta.

        Returns:
            Weights of low / low beta minus high / high beta. Applied to
            returns in excess of the risk-free rate they give the BAB return
            of paper eq. 17 (p.19).

        Raises:
            ZeroDivisionError: If a leg's beta is zero.
        """
        return low / low_beta - high / high_beta
