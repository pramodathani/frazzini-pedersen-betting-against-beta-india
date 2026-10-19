"""Collects RBI 91-day Treasury bill auction yields from press releases."""

import csv
import pathlib
import re
import sys
import time

import requests


class TreasuryBillDownloader:
    """Walks backwards through RBI auction result press releases.

    Attributes:
        address: The RBI press release address, with a place for the number.
        pattern: Matches the 91-day cut-off yield in an auction release.
    """

    address = (
        'https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid={}'
    )
    pattern = re.compile(
        r'Cut-off price \(.\) / Yield\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+'
        r'\(YTM: ([\d.]+)%\)'
    )
    date_pattern = re.compile(r'Date : ([A-Za-z]{3} \d+, \d{4})')

    def __init__(self, output_path: pathlib.Path) -> None:
        """Stores the output file and opens a polite session.

        Args:
            output_path: The CSV file that receives one row per auction.

        Returns:
            None.

        Raises:
            None.
        """
        self.output_path = output_path
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0'

    def read_release(self, release_number: int) -> tuple[str, str, float]:
        """Reads one press release.

        Args:
            release_number: The RBI press release number in the address.

        Returns:
            The date text, a flag 'auction' or 'other', and the yield, which
            is zero when the release is not an auction result.

        Raises:
            requests.HTTPError: If RBI answers with an error.
        """
        response = self.session.get(
            self.address.format(release_number), timeout=30
        )
        response.raise_for_status()
        text = re.sub(r'<[^>]*>', ' ', response.text)
        text = re.sub(r'\s+', ' ', text)
        date_match = self.date_pattern.search(text)
        date_text = date_match.group(1) if date_match else ''
        match = self.pattern.search(text)
        if match and 'Treasury Bills: Full Auction Result' in text:
            return date_text, 'auction', float(match.group(1))
        return date_text, 'other', 0.0

    def run(self, start_number: int, stop_number: int) -> None:
        """Scans release numbers and saves the auctions it finds.

        Args:
            start_number: The highest release number to read.
            stop_number: The lowest release number to read.

        Returns:
            None.

        Raises:
            requests.HTTPError: If RBI answers with an error.
        """
        rows = []
        release_number = start_number
        while release_number >= stop_number:
            date_text, kind, yield_percent = self.read_release(release_number)
            if kind == 'auction':
                rows.append([release_number, date_text, yield_percent])
                print(rows[-1], flush=True)
                release_number -= 30
            else:
                release_number -= 1
            time.sleep(0.2)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with self.output_path.open('w', newline='') as handle:
            writer = csv.writer(handle)
            writer.writerow(['release_number', 'date', 'yield_91_day_ytm'])
            writer.writerows(rows)


if __name__ == '__main__':
    TreasuryBillDownloader(pathlib.Path(sys.argv[1])).run(
        int(sys.argv[2]), int(sys.argv[3])
    )
