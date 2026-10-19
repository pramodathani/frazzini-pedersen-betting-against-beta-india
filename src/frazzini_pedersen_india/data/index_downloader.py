"""Downloads daily total return index history from niftyindices.com."""

import json
import pathlib
import sys

import requests


class IndexDownloader:
    """Fetches one index's total return history and saves it as JSON.

    Attributes:
        endpoint: The niftyindices.com address that serves the history.
    """

    endpoint = (
        'https://www.niftyindices.com/BackPage/getTotalReturnIndexString'
    )

    def __init__(self, output_folder: pathlib.Path) -> None:
        """Stores where files are saved.

        Args:
            output_folder: Folder that receives one JSON file per index.

        Returns:
            None.

        Raises:
            None.
        """
        self.output_folder = output_folder
        self.index_names = {
            'nifty500_tri': 'Nifty 500',
            'nifty100_lowvol30_tri': 'NIFTY100 LOW VOLATILITY 30',
            'nifty_lowvol50_tri': 'NIFTY LOW VOLATILITY 50',
        }

    def fetch(self, index_name: str, start: str, end: str) -> list[dict]:
        """Asks the site for one index's daily history.

        Args:
            index_name: The index name as the site spells it.
            start: First day, as DD-Mon-YYYY.
            end: Last day, as DD-Mon-YYYY.

        Returns:
            The rows the site returned, newest first.

        Raises:
            requests.HTTPError: If the site answers with an error.
        """
        payload = {
            'cinfo': json.dumps(
                {
                    'name': index_name,
                    'startDate': start,
                    'endDate': end,
                    'indexName': index_name,
                }
            ),
        }
        headers = {
            'Content-Type': 'application/json; charset=UTF-8',
            'Referer': 'https://www.niftyindices.com/reports/historical-data',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) Chrome/126',
        }
        response = requests.post(
            self.endpoint, json=payload, headers=headers, timeout=60
        )
        response.raise_for_status()
        body = response.json()
        if isinstance(body, list):
            return body
        return json.loads(body['d'])

    def run(self, end: str) -> None:
        """Downloads the low volatility indices in yearly slices.

        Args:
            end: Last year to fetch, as YYYY.

        Returns:
            None.

        Raises:
            requests.HTTPError: If the site answers with an error.
        """
        self.output_folder.mkdir(parents=True, exist_ok=True)
        for stem in ('nifty100_lowvol30_tri', 'nifty_lowvol50_tri'):
            rows = []
            for year in range(2000, int(end) + 1):
                rows.extend(
                    self.fetch(
                        self.index_names[stem],
                        f'01-Jan-{year}',
                        f'31-Dec-{year}',
                    )
                )
            path = self.output_folder / f'{stem}.json'
            path.write_text(json.dumps(rows))
            print(stem, len(rows), rows[0]['Date'], rows[-1]['Date'])


if __name__ == '__main__':
    IndexDownloader(pathlib.Path(sys.argv[1])).run(sys.argv[2])
