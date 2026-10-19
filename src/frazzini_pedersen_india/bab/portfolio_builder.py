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

    def value_weighted_bab(
        self,
        betas: pd.Series,
        values: pd.Series,
        breakpoint_shares: pd.Series,
    ) -> pd.Series:
        """Builds the two-by-three value-weighted BAB of paper Table B9.

        Shares are split at the median traded value of the breakpoint shares
        into small and large, and within each size group into low beta (below
        the 30th percentile of the breakpoint shares' betas), middle and high
        beta (above the 70th percentile). Legs are weighted by traded value,
        averaged over the two size groups, and divided by their betas.

        Args:
            betas: Ex-ante betas of the eligible shares.
            values: Median traded value of the same shares.
            breakpoint_shares: Flags for the shares that set the cut points.

        Returns:
            Weights of low / low beta minus high / high beta on excess
            returns.

        Raises:
            ValueError: If no breakpoint share is eligible or a group is
                empty.
        """
        flags = breakpoint_shares.reindex(betas.index).fillna(False)
        flags = flags.astype(bool)
        if not flags.any():
            raise ValueError('no breakpoint shares among eligible shares')
        size_cut = values[flags].median()
        low_cut = betas[flags].quantile(0.3)
        high_cut = betas[flags].quantile(0.7)
        low_total = pd.Series(0.0, index=betas.index)
        high_total = pd.Series(0.0, index=betas.index)
        low_beta = 0.0
        high_beta = 0.0
        for large in (False, True):
            if large:
                in_size = values > size_cut
            else:
                in_size = values <= size_cut
            low_members = in_size & (betas <= low_cut)
            high_members = in_size & (betas >= high_cut)
            if not low_members.any() or not high_members.any():
                raise ValueError('a size group has an empty leg')
            low_weights = values.where(low_members, 0.0)
            high_weights = values.where(high_members, 0.0)
            low_weights = low_weights / low_weights.sum()
            high_weights = high_weights / high_weights.sum()
            low_total = low_total + 0.5 * low_weights
            high_total = high_total + 0.5 * high_weights
            low_beta = low_beta + 0.5 * float((betas * low_weights).sum())
            high_beta = high_beta + 0.5 * float((betas * high_weights).sum())
        return low_total / low_beta - high_total / high_beta

    def equal_weighted_bab(
        self,
        betas: pd.Series,
        breakpoint_shares: pd.Series,
    ) -> pd.Series:
        """Builds a BAB with equal weights in each half instead of ranks.

        Args:
            betas: Ex-ante betas of the eligible shares.
            breakpoint_shares: Flags for the shares that set the median.

        Returns:
            Weights of low / low beta minus high / high beta on excess
            returns, each half equally weighted.

        Raises:
            ValueError: If no breakpoint share is eligible or a half is
                empty.
        """
        flags = breakpoint_shares.reindex(betas.index).fillna(False)
        flags = flags.astype(bool)
        if not flags.any():
            raise ValueError('no breakpoint shares among eligible shares')
        cutoff = betas[flags].median()
        low_members = betas <= cutoff
        high_members = betas > cutoff
        if not low_members.any() or not high_members.any():
            raise ValueError('a half has no shares')
        low = low_members.astype(float) / low_members.sum()
        high = high_members.astype(float) / high_members.sum()
        low_beta = float((betas * low).sum())
        high_beta = float((betas * high).sum())
        return self.bab_target(low, high, low_beta, high_beta)
