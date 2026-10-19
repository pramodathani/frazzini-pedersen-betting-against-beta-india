"""Tests for the companion page's data snapshot."""

import json
import pathlib

import numpy as np
import pytest

from frazzini_pedersen_india.bab.site_snapshot import SiteSnapshot


class TestSiteSnapshot:
    """Checks on the JSON helpers."""

    def test_rows_round_and_turn_nan_into_none(
        self, tmp_path: pathlib.Path
    ) -> None:
        """A results table becomes rounded dictionaries with None for NaN.

        Args:
            tmp_path: A temporary folder from pytest.

        Returns:
            None.

        Raises:
            AssertionError: If a row is wrong.
        """
        (tmp_path / 'table.csv').write_text(
            'portfolio,mean,t\nA,0.123456789,\nB,0.5,2.0\n'
        )
        snapshot = SiteSnapshot(tmp_path, tmp_path, tmp_path / 'out')
        rows = snapshot.rows('table.csv')
        assert rows[0]['mean'] == pytest.approx(0.123457)
        assert rows[0]['t'] is None
        assert rows[1]['t'] == 2.0

    def test_clean_and_dump(self, tmp_path: pathlib.Path) -> None:
        """Series are rounded and NaN becomes null in the file.

        Args:
            tmp_path: A temporary folder from pytest.

        Returns:
            None.

        Raises:
            AssertionError: If the file is wrong.
        """
        snapshot = SiteSnapshot(tmp_path, tmp_path, tmp_path)
        cleaned = snapshot.clean(np.array([0.1234567, np.nan]))
        assert cleaned == [0.123457, None]
        snapshot.dump('x.json', {'series': cleaned})
        loaded = json.loads((tmp_path / 'x.json').read_text())
        assert loaded == {'series': [0.123457, None]}
