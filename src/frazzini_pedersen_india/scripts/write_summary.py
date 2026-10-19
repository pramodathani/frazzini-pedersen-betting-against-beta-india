"""Writes results/summary.md from the result tables."""

import pathlib
import sys

import pandas as pd


class WriteSummaryApplication:
    """Command-line step that turns the result CSVs into the summary."""

    def run(self, results_folder: pathlib.Path) -> None:
        """Writes results/summary.md.

        Args:
            results_folder: The results folder.

        Returns:
            None.

        Raises:
            FileNotFoundError: If a result file is missing.
        """
        self.folder = results_folder
        self.main = pd.read_csv(results_folder / 'main_summary.csv')
        self.tables = pd.read_csv(results_folder / 'tables_summary.csv')
        self.variants = pd.read_csv(results_folder / 'variants_summary.csv')
        self.sub = pd.read_csv(results_folder / 'subperiods.csv')
        self.bench = pd.read_csv(
            results_folder / 'long_only_vs_benchmarks.csv'
        )
        self.exposure = pd.read_csv(results_folder / 'bab_dollar_exposure.csv')
        parts = [
            self.header(),
            self.decile_table('liquid'),
            self.decile_table('full'),
            self.bab_table(),
            self.legs_table(),
            self.groups_table('size'),
            self.groups_table('ivol'),
            self.subperiod_table(),
            self.variants_table(),
            self.long_only_table(),
        ]
        text = '\n\n'.join(parts) + '\n'
        (results_folder / 'summary.md').write_text(text)

    def pct(self, value: float) -> str:
        """Formats a monthly return as a percent.

        Args:
            value: A decimal return.

        Returns:
            Text such as '0.79'.

        Raises:
            None.
        """
        return f'{value * 100:.2f}'

    def pick(
        self, frame: pd.DataFrame, name: str, cost: str, column: str
    ) -> float:
        """Reads one number from a summary table.

        Args:
            frame: A summary table.
            name: The portfolio's name.
            cost: 'gross' or 'net'.
            column: The column to read.

        Returns:
            The value.

        Raises:
            IndexError: If the row is missing.
        """
        rows = frame[(frame['portfolio'] == name) & (frame['costs'] == cost)]
        return float(rows.iloc[0][column])

    def header(self) -> str:
        """Writes the opening of the summary.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        months = int(self.pick(self.main, 'bab_full', 'gross', 'months'))
        return (
            '# Results: Betting Against Beta on NSE shares\n\n'
            f'Holding months 2008-02 to 2026-09 ({months} months). Returns '
            'are monthly percent in excess of the risk-free rate. t is the '
            'Newey-West t-statistic. Gross is before trading costs and net '
            'is after brahmagupta delivery costs (STT, stamp duty, '
            'exchange and SEBI charges, GST) plus market impact of 0.10% a '
            'side for the liquid universe and 0.30% for the full universe. '
            'The paper figures are its Table III, US stocks 1926-2012 '
            '(manuscript p.41). Alphas against IIMA factors use the 215 '
            'months to December 2025.'
        )

    def decile_table(self, universe: str) -> str:
        """Writes the Table III analogue for one universe.

        Args:
            universe: 'liquid' or 'full'.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        title = (
            'the 500 most traded shares'
            if universe == 'liquid'
            else 'every share with a beta, cut points from the 500 most traded'
        )
        lines = [
            f'## Beta deciles ({title}), gross of costs',
            '',
            (
                '| Decile | Excess return | t | CAPM alpha | t | 4-factor alpha | t'
                ' | Realised beta | Volatility % | Sharpe |'
            ),
            '|---|---|---|---|---|---|---|---|---|---|',
        ]
        for decile in range(1, 11):
            name = f'{universe}_D{decile}'
            row = self.main[
                (self.main['portfolio'] == name)
                & (self.main['costs'] == 'gross')
            ].iloc[0]
            lines.append(
                f'| P{decile} | {self.pct(row["mean_monthly"])} | '
                f'{row["nw_t"]:.2f} | {self.pct(row["capm_alpha"])} | '
                f'{row["capm_alpha_t"]:.2f} | {self.pct(row["ff4_alpha"])} | '
                f'{row["ff4_alpha_t"]:.2f} | {row["capm_beta"]:.2f} | '
                f'{row["volatility_annual"] * 100:.1f} | {row["sharpe"]:.2f} |'
            )
        if universe == 'liquid':
            lines.append('')
            lines.append(
                'Paper, Table III (US): P1 excess 0.91 (t 6.37), CAPM alpha '
                '0.52, realised beta 0.67, Sharpe 0.70; P10 excess 0.97 '
                '(t 2.55), CAPM alpha -0.10, realised beta 1.85, Sharpe 0.28.'
            )
        return '\n'.join(lines)

    def bab_table(self) -> str:
        """Writes the BAB factor table.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        lines = [
            '## BAB factor',
            '',
            (
                '| Portfolio | Costs | Excess return | t | CAPM alpha | 4-factor '
                'alpha | t | Realised beta | Volatility % | Sharpe | Worst '
                'drawdown % | Turnover per month |'
            ),
            '|---|---|---|---|---|---|---|---|---|---|---|---|',
        ]
        names = (
            ('bab_full', self.main),
            ('bab_liquid', self.main),
            ('bab_full_equal', self.tables),
            ('bab_liquid_equal', self.tables),
            ('bab_full_value', self.tables),
            ('bab_liquid_value', self.tables),
        )
        for name, frame in names:
            for cost in ('gross', 'net'):
                row = frame[
                    (frame['portfolio'] == name) & (frame['costs'] == cost)
                ].iloc[0]
                lines.append(
                    f'| {name} | {cost} | {self.pct(row["mean_monthly"])} | '
                    f'{row["nw_t"]:.2f} | {self.pct(row["capm_alpha"])} | '
                    f'{self.pct(row["ff4_alpha"])} | '
                    f'{row["ff4_alpha_t"]:.2f} | {row["capm_beta"]:.2f} | '
                    f'{row["volatility_annual"] * 100:.1f} | '
                    f'{row["sharpe"]:.2f} | '
                    f'{row["max_drawdown"] * 100:.1f} | '
                    f'{row["turnover_mean"]:.2f} |'
                )
        long_value = self.exposure.iloc[0]
        lines.append('')
        lines.append(
            'Paper, Table III (US, rank weighted): excess 0.70 (t 7.12), '
            '4-factor alpha 0.55 (t 5.59), realised beta -0.06, volatility '
            '10.7, Sharpe 0.78, $1.40 long and $0.70 short (p.19). Indian '
            f'bab_full holds on average ${long_value["dollar_long"]:.2f} long '
            f'and ${long_value["dollar_short"]:.2f} short. Agarwalla et al. '
            '(2014, BSE, 1998-2013, equal-weighted deciles, rank-weighted '
            'BAB): excess 1.70, 4-factor alpha 1.08, Sharpe 0.86.'
        )
        lines.append('')
        lines.append(
            'Value-weighted rows weight by median traded value, not market '
            'capitalisation, which is unavailable before 2024. They follow '
            "the paper's Table B9 construction (2 size x 3 beta groups)."
        )
        return '\n'.join(lines)

    def legs_table(self) -> str:
        """Writes the table of the two BAB legs.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        lines = [
            '## Legs of the BAB factor, each scaled to beta 1 (paper Table B1)',
            '',
            '| Leg | Costs | Excess return | t | 4-factor alpha | t |',
            '|---|---|---|---|---|---|',
        ]
        for name in (
            'full_low_leg_scaled',
            'full_high_leg_scaled',
            'liquid_low_leg_scaled',
            'liquid_high_leg_scaled',
        ):
            for cost in ('gross', 'net'):
                row = self.tables[
                    (self.tables['portfolio'] == name)
                    & (self.tables['costs'] == cost)
                ].iloc[0]
                lines.append(
                    f'| {name} | {cost} | {self.pct(row["mean_monthly"])} | '
                    f'{row["nw_t"]:.2f} | {self.pct(row["ff4_alpha"])} | '
                    f'{row["ff4_alpha_t"]:.2f} |'
                )
        lines.append('')
        lines.append(
            'Paper Table B1 (US): low-beta leg alpha 0.36, high-beta leg '
            'alpha -0.01.'
        )
        return '\n'.join(lines)

    def groups_table(self, kind: str) -> str:
        """Writes BAB within size or volatility groups.

        Args:
            kind: 'size' or 'ivol'.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        if kind == 'size':
            title = (
                'BAB within size groups, by median traded value, full '
                'universe (paper Table B3)'
            )
        else:
            title = (
                'BAB within idiosyncratic volatility groups, full universe '
                '(paper Table B5)'
            )
        lines = [
            f'## {title}',
            '',
            (
                '| Group (1 low to 5 high) | Gross excess | t | 4-factor alpha | '
                't | Net excess | Net t |'
            ),
            '|---|---|---|---|---|---|---|',
        ]
        for group in range(1, 6):
            name = f'bab_{kind}_Q{group}'
            gross = self.tables[
                (self.tables['portfolio'] == name)
                & (self.tables['costs'] == 'gross')
            ].iloc[0]
            net = self.tables[
                (self.tables['portfolio'] == name)
                & (self.tables['costs'] == 'net')
            ].iloc[0]
            lines.append(
                f'| Q{group} | {self.pct(gross["mean_monthly"])} | '
                f'{gross["nw_t"]:.2f} | {self.pct(gross["ff4_alpha"])} | '
                f'{gross["ff4_alpha_t"]:.2f} | '
                f'{self.pct(net["mean_monthly"])} | {net["nw_t"]:.2f} |'
            )
        if kind == 'ivol':
            lines.append('')
            lines.append(
                'Residual volatility here is the one-year market-model '
                'residual of daily returns, an approximation of the paper '
                '(p.61).'
            )
        return '\n'.join(lines)

    def subperiod_table(self) -> str:
        """Writes the subperiod table.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        lines = [
            '## Three subperiods, gross (paper Table B4)',
            '',
            '| Portfolio | Months | Excess return | t |',
            '|---|---|---|---|',
        ]
        rows = self.sub[self.sub['costs'] == 'gross']
        for row in rows.itertuples(index=False):
            lines.append(
                f'| {row.portfolio} | {row.first_month} to {row.last_month}'
                f' | {self.pct(row.mean_monthly)} | {row.nw_t:.2f} |'
            )
        return '\n'.join(lines)

    def variants_table(self) -> str:
        """Writes the robustness variants.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        lines = [
            '## Robustness variants, monthly excess return % (Newey-West t)',
            '',
            (
                '| Variant | bab_full gross | bab_full net | bab_liquid gross | '
                'bab_liquid net | liquid_D1 net |'
            ),
            '|---|---|---|---|---|---|',
        ]
        for name in self.variants['variant'].unique():
            cells = []
            for portfolio, cost in (
                ('bab_full', 'gross'),
                ('bab_full', 'net'),
                ('bab_liquid', 'gross'),
                ('bab_liquid', 'net'),
                ('liquid_D1', 'net'),
            ):
                row = self.variants[
                    (self.variants['variant'] == name)
                    & (self.variants['portfolio'] == portfolio)
                    & (self.variants['costs'] == cost)
                ].iloc[0]
                cells.append(
                    f'{self.pct(row["mean_monthly"])} ({row["nw_t"]:.2f})'
                )
            lines.append(f'| {name} | {" | ".join(cells)} |')
        lines.append('')
        lines.append(
            'Specifications tried: 17, namely the main one and ten variants '
            'above, and the equal-weighted BAB, the value-weighted BAB, '
            'BAB within size groups, BAB within volatility groups, and '
            'holding the long-only portfolios for 3 and for 12 months. With '
            'Bonferroni correction for 17 tests the two-sided 5% threshold is '
            '|t| of about 2.98, and only the gross full-universe BAB passes. '
            'The main specification was fixed in plan/india_plan.md before '
            'any result was seen.'
        )
        return '\n'.join(lines)

    def long_only_table(self) -> str:
        """Writes the long-only comparison with the benchmarks.

        Args:
            None.

        Returns:
            Markdown text.

        Raises:
            None.
        """
        lines = [
            '## Long-only low-beta portfolios against the NIFTY 500 TRI',
            '',
            (
                '| Portfolio | Costs | Annual return % | Volatility % | Worst '
                'drawdown % | Excess over NIFTY 500 % a year | t | CAPM alpha % a'
                ' month | t | Beta |'
            ),
            '|---|---|---|---|---|---|---|---|---|---|',
        ]
        for row in self.bench.itertuples(index=False):
            alpha = '' if pd.isna(row.alpha) else self.pct(row.alpha)
            alpha_t = '' if pd.isna(row.alpha_t) else f'{row.alpha_t:.2f}'
            excess_t = '' if pd.isna(row.excess_t) else f'{row.excess_t:.2f}'
            lines.append(
                f'| {row.portfolio} | {row.costs} | '
                f'{row.compound_annual * 100:.1f} | '
                f'{row.volatility_annual * 100:.1f} | '
                f'{row.maximum_drawdown * 100:.1f} | '
                f'{row.excess_annual * 100:.1f} | {excess_t} | {alpha} | '
                f'{alpha_t} | {row.beta:.2f} |'
            )
        return '\n'.join(lines)


if __name__ == '__main__':
    WriteSummaryApplication().run(pathlib.Path(sys.argv[1]))
