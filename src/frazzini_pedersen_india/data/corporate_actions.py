"""Turns NSE corporate action records into price factors and dividends."""

import json
import pathlib
import re

import pandas as pd


class CorporateActionParser:
    """Reads the text of one corporate action subject.

    Attributes:
        bonus_pattern: Matches a bonus ratio such as 1:2.
        amount_pattern: Matches a rupee amount such as Rs 2.50.
        percent_pattern: Matches a dividend given as a percent of face value.
    """

    bonus_pattern = re.compile(
        r'bonus\s*-?\s*(\d+)\s*:\s*(\d+)', re.IGNORECASE
    )
    amount_pattern = re.compile(
        r'(?:rs|re)\.?\s*([\d]+(?:\.\d+)?)', re.IGNORECASE
    )
    percent_pattern = re.compile(r'([\d]+(?:\.\d+)?)\s*%')

    def parse(self, subject: str, face_value: str) -> tuple[float, float]:
        """Finds the price factor and the cash dividend in one subject.

        Args:
            subject: The action's text, such as 'Bonus 1:1'.
            face_value: The share's face value as text, or '-'.

        Returns:
            The price factor and the dividend per share. The factor is 1.0
            when the action does not change the share count, and the dividend
            is 0.0 when there is no cash payment.

        Raises:
            None.
        """
        text = subject.strip()
        lowered = text.lower()
        if 'capital reduction' in lowered:
            return 1.0, 0.0
        factor = 1.0
        bonus = self.bonus_pattern.search(text)
        if bonus:
            new_shares = float(bonus.group(1))
            old_shares = float(bonus.group(2))
            if old_shares > 0:
                factor = factor * old_shares / (old_shares + new_shares)
        is_split = 'split' in lowered or 'sub-division' in lowered
        is_consolidation = 'consolidat' in lowered
        if is_split or is_consolidation:
            amounts = self.amount_pattern.findall(text)
            if len(amounts) >= 2:
                old_value = float(amounts[0])
                new_value = float(amounts[1])
                if old_value > 0 and new_value > 0:
                    factor = factor * new_value / old_value
        dividend = 0.0
        if 'dividend' in lowered and not (bonus or is_split):
            dividend = self.parse_dividend(text, face_value)
        return factor, dividend

    def parse_dividend(self, text: str, face_value: str) -> float:
        """Finds the cash dividend in a dividend subject.

        Args:
            text: The action's text.
            face_value: The share's face value as text, or '-'.

        Returns:
            The dividend per share in rupees, or 0.0 when none is found.

        Raises:
            None.
        """
        amounts = self.amount_pattern.findall(text)
        if amounts:
            total = 0.0
            for amount in amounts:
                total = total + float(amount)
            return total
        percent = self.percent_pattern.search(text)
        if percent:
            try:
                face = float(face_value)
            except ValueError:
                return 0.0
            return float(percent.group(1)) / 100.0 * face
        return 0.0


class CorporateActionTable:
    """Loads NSE corporate action files into one table of price effects."""

    def __init__(self) -> None:
        """Creates the table builder with its parser.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        self.parser = CorporateActionParser()

    def load(self, paths: list[pathlib.Path]) -> pd.DataFrame:
        """Reads action files and keeps those that change prices.

        Args:
            paths: The yearly JSON files. A later file replaces earlier
                records of the same symbol, ex-date and subject.

        Returns:
            A table with columns symbol, ex_date, price_factor and dividend,
            one row per symbol and ex-date, with factors multiplied and
            dividends added when several actions share a date.

        Raises:
            FileNotFoundError: If a path does not exist.
        """
        rows = []
        for path in paths:
            records = json.loads(path.read_text())
            for record in records:
                if record.get('series') not in ('EQ', 'BE', 'BZ', 'SM', 'ST'):
                    continue
                ex_text = record.get('exDate')
                if not ex_text or ex_text == '-':
                    continue
                factor, dividend = self.parser.parse(
                    record.get('subject', ''),
                    record.get('faceVal', '-'),
                )
                if factor == 1.0 and dividend == 0.0:
                    continue
                rows.append(
                    {
                        'symbol': record['symbol'],
                        'ex_date': pd.to_datetime(ex_text, format='%d-%b-%Y'),
                        'subject': record.get('subject', '').strip(),
                        'price_factor': factor,
                        'dividend': dividend,
                    }
                )
        table = pd.DataFrame(rows)
        table = table.drop_duplicates(['symbol', 'ex_date', 'subject'])
        grouped = table.groupby(['symbol', 'ex_date'], as_index=False).agg(
            price_factor=('price_factor', 'prod'),
            dividend=('dividend', 'sum'),
        )
        return grouped
