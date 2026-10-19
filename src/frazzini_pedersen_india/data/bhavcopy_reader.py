"""Reads NSE daily bhavcopy zip files in both of NSE's formats."""

import pathlib
import sys
import zipfile

import pandas as pd


class BhavcopyReader:
    """Turns bhavcopy zips into one table of daily closes.

    Attributes:
        series_kept: The NSE series that are ordinary tradable shares.
        columns: The columns every table from this reader has.
    """

    series_kept = ('EQ', 'BE', 'BZ')
    columns = ('date', 'symbol', 'series', 'isin', 'close', 'traded_value')

    def read_file(self, path: pathlib.Path) -> pd.DataFrame:
        """Reads one bhavcopy zip.

        Args:
            path: A zip named like 2015-03-02.csv.zip, in the old format or
                in the UDiFF format that NSE uses from 2024-07-08.

        Returns:
            A table with the columns date, symbol, series, isin, close and
            traded_value, holding only ordinary shares. The isin column is
            empty for old files that do not carry it.

        Raises:
            FileNotFoundError: If the path does not exist.
        """
        date = pd.Timestamp(path.name[:10])
        with zipfile.ZipFile(path) as archive:
            name = archive.namelist()[0]
            with archive.open(name) as handle:
                raw = pd.read_csv(handle, low_memory=False)
        if 'TckrSymb' in raw.columns:
            raw = raw[raw['FinInstrmTp'] == 'STK']
            table = pd.DataFrame(
                {
                    'symbol': raw['TckrSymb'].str.strip(),
                    'series': raw['SctySrs'].str.strip(),
                    'isin': raw['ISIN'],
                    'close': raw['ClsPric'],
                    'traded_value': raw['TtlTrfVal'],
                }
            )
        else:
            isin = raw['ISIN'] if 'ISIN' in raw.columns else None
            table = pd.DataFrame(
                {
                    'symbol': raw['SYMBOL'].str.strip(),
                    'series': raw['SERIES'].str.strip(),
                    'isin': isin,
                    'close': raw['CLOSE'],
                    'traded_value': raw['TOTTRDVAL'],
                }
            )
        table = table[table['series'].isin(self.series_kept)]
        table.insert(0, 'date', date)
        return table.reset_index(drop=True)

    def read_folders(
        self, folders: list[pathlib.Path], first_year: int
    ) -> pd.DataFrame:
        """Reads every bhavcopy in several folders.

        Args:
            folders: Folders holding one sub-folder per year.
            first_year: The first year to read.

        Returns:
            One table of every share-day, with a share that appears in
            more than one series on a day kept once, preferring EQ.

        Raises:
            FileNotFoundError: If a folder does not exist.
        """
        paths = {}
        for folder in folders:
            for year_folder in sorted(folder.iterdir()):
                if not year_folder.name.isdigit():
                    continue
                if int(year_folder.name) < first_year:
                    continue
                for path in year_folder.glob('*.csv.zip'):
                    paths[path.name] = path
        tables = []
        for name in sorted(paths):
            tables.append(self.read_file(paths[name]))
        combined = pd.concat(tables, ignore_index=True)
        order = {'EQ': 0, 'BE': 1, 'BZ': 2}
        combined['rank'] = combined['series'].map(order)
        combined = combined.sort_values(['date', 'symbol', 'rank'])
        combined = combined.drop_duplicates(['date', 'symbol'])
        return combined.drop(columns='rank').reset_index(drop=True)


if __name__ == '__main__':
    reader = BhavcopyReader()
    output = reader.read_folders(
        [pathlib.Path(argument) for argument in sys.argv[3:]],
        int(sys.argv[2]),
    )
    output.to_parquet(sys.argv[1])
    print(len(output), output['date'].min(), output['date'].max())
