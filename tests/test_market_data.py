"""Tests for the market data loader."""

import json
import pathlib

import pandas as pd
import pytest

from frazzini_pedersen_india.data.market_data import MarketData


class TestMarketData:
    """Checks on index returns, factors and the risk-free rate."""

    def make_folder(self, root: pathlib.Path) -> pathlib.Path:
        """Writes small index, factor and T-bill files.

        Args:
            root: A temporary folder.

        Returns:
            The data folder.

        Raises:
            None.
        """
        (root / 'nse/indices').mkdir(parents=True)
        (root / 'nse/iima').mkdir(parents=True)
        rows = []
        for date, level in (
            ('01 Jan 2020', '100.0'),
            ('02 Jan 2020', '101.0'),
            ('04 Jan 2020', '103.02'),
            ('06 Jan 2020', '103.02'),
        ):
            rows.append({'Date': date, 'TotalReturnsIndex': level})
        (root / 'nse/indices/test.json').write_text(json.dumps(rows))
        (root / 'nse/iima/2025-12_f.csv').write_text(
            'Date,SMB,HML,WML,MF,RF\n'
            '2025-11,1,2,3,4,0.4\n'
            '2025-12,1,2,3,4,0.5\n'
        )
        (root / 'nse/tbill_auctions.csv').write_text(
            'release_number,date,yield_91_day_ytm\n'
            '1,"Dec 10, 2025",5.0\n'
            '2,"Jan 07, 2026",6.0\n'
            '3,"Jan 21, 2026",6.0\n'
        )
        return root

    def test_special_day_is_bridged(self, tmp_path: pathlib.Path) -> None:
        """An index day that is not a session is compounded into the next.

        Args:
            tmp_path: A temporary folder from pytest.

        Returns:
            None.

        Raises:
            AssertionError: If a return is wrong.
        """
        data = MarketData(self.make_folder(tmp_path))
        sessions = pd.DatetimeIndex(['2020-01-01', '2020-01-02', '2020-01-06'])
        returns = data.index_returns_on('test.json', sessions)
        assert returns.iloc[1] == pytest.approx(0.01)
        assert returns.iloc[2] == pytest.approx(103.02 / 101.0 - 1.0)

    def test_risk_free_joins_iima_and_auctions(
        self, tmp_path: pathlib.Path
    ) -> None:
        """IIMA's rate holds to 2025-12 and auctions supply 2026.

        Args:
            tmp_path: A temporary folder from pytest.

        Returns:
            None.

        Raises:
            AssertionError: If the series is wrong.
        """
        data = MarketData(self.make_folder(tmp_path))
        rate = data.monthly_risk_free()
        assert rate[pd.Period('2025-12')] == pytest.approx(0.005)
        assert rate[pd.Period('2026-01')] == pytest.approx(
            1.06 ** (1.0 / 12.0) - 1.0
        )
        assert len(rate) == 3
