"""Tests for reading corporate action subjects."""

import json
import pathlib

import pytest

from frazzini_pedersen_india.data.corporate_actions import (
    CorporateActionParser,
    CorporateActionTable,
)


class TestCorporateActionParser:
    """Checks on the subject parser."""

    def test_bonus_ratio(self) -> None:
        """A 1:2 bonus gives one new share for two held.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If the factor is not two thirds.
        """
        factor, dividend = CorporateActionParser().parse('Bonus 1:2', '10')
        assert factor == pytest.approx(2.0 / 3.0)
        assert dividend == 0.0

    def test_split(self) -> None:
        """A split from Rs 10 to Rs 2 divides the price by five.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If the factor is not 0.2.
        """
        subject = (
            'Face Value Split (Sub-Division) - From Rs 10/- Per Share '
            'To Rs 2/- Per Share'
        )
        factor, dividend = CorporateActionParser().parse(subject, '10')
        assert factor == pytest.approx(0.2)
        assert dividend == 0.0

    def test_bonus_and_split_multiply(self) -> None:
        """A bonus and a split in one record combine.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If the factor is not 0.1.
        """
        subject = (
            'Bonus 1:1 / Face Value Split From Rs 10/- Per Share '
            'To Rs 2/- Per Share'
        )
        factor, _ = CorporateActionParser().parse(subject, '10')
        assert factor == pytest.approx(0.5 * 0.2)

    def test_consolidation_raises_price(self) -> None:
        """A consolidation from Re 1 to Rs 10 multiplies the price by ten.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If the factor is not 10.
        """
        subject = (
            'Consolidation Of Equity Shares From Re 1 Per Share '
            'To Rs 10 Per Share'
        )
        factor, _ = CorporateActionParser().parse(subject, '1')
        assert factor == pytest.approx(10.0)

    def test_dividend_in_rupees(self) -> None:
        """A rupee dividend is read as an amount.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If the amount is wrong.
        """
        factor, dividend = CorporateActionParser().parse(
            'Interim Dividend - Rs 2.50 Per Share', '10'
        )
        assert factor == 1.0
        assert dividend == pytest.approx(2.5)

    def test_dividend_in_percent_uses_face_value(self) -> None:
        """A percent dividend is a share of the face value.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If the amount is wrong.
        """
        _, dividend = CorporateActionParser().parse('Agm/Dividend - 40%', '10')
        assert dividend == pytest.approx(4.0)

    def test_rights_are_ignored(self) -> None:
        """Rights issues leave price and dividend unchanged.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: If anything is changed.
        """
        parsed = CorporateActionParser().parse(
            'Rights 1:2 @ Premium Re 1.50/-', '10'
        )
        assert parsed == (1.0, 0.0)


class TestCorporateActionTable:
    """Checks on loading action files."""

    def test_same_day_actions_combine(self, tmp_path: pathlib.Path) -> None:
        """A bonus and a dividend on one date become one row.

        Args:
            tmp_path: A temporary folder from pytest.

        Returns:
            None.

        Raises:
            AssertionError: If the row is wrong.
        """
        records = [
            {
                'symbol': 'ABC',
                'series': 'EQ',
                'exDate': '05-Jan-2015',
                'subject': 'Bonus 1:1',
                'faceVal': '10',
            },
            {
                'symbol': 'ABC',
                'series': 'EQ',
                'exDate': '05-Jan-2015',
                'subject': 'Dividend - Rs 2 Per Share',
                'faceVal': '10',
            },
            {
                'symbol': 'GOVT',
                'series': 'GS',
                'exDate': '05-Jan-2015',
                'subject': 'Interest Payment',
                'faceVal': '100',
            },
        ]
        path = tmp_path / '2015.json'
        path.write_text(json.dumps(records))
        table = CorporateActionTable().load([path])
        assert len(table) == 1
        assert table.iloc[0]['price_factor'] == pytest.approx(0.5)
        assert table.iloc[0]['dividend'] == pytest.approx(2.0)
