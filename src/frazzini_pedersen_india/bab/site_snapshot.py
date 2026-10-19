"""Writes the compact data files the companion page reads."""

import datetime
import json
import pathlib

import pandas as pd

from frazzini_pedersen_india.bab.study_inputs import StudyInputs


class SiteSnapshot:
    """Turns the result tables into JSON for the web page.

    Only derived results are written, never raw exchange data.

    Attributes:
        data_folder: The study's data folder.
        results_folder: The results folder.
        site_data_folder: Where the JSON files are written.
    """

    benchmark_files = (
        ('nifty500', 'nifty500_tri.json'),
        ('lowvol30', 'nifty100_lowvol30_tri.json'),
        ('lowvol50', 'nifty_lowvol50_tri.json'),
    )
    wealth_series = (
        ('liquid_D1', 'main'),
        ('liquid_D1_every_12_months', 'tables'),
        ('full_D1', 'main'),
        ('bab_low_leg', 'main'),
    )
    excess_series = (
        ('bab_full', 'main'),
        ('bab_liquid', 'main'),
        ('bab_full_equal', 'tables'),
        ('bab_full_value', 'tables'),
    )

    def __init__(
        self,
        data_folder: pathlib.Path,
        results_folder: pathlib.Path,
        site_data_folder: pathlib.Path,
    ) -> None:
        """Stores the folders.

        Args:
            data_folder: The study's data folder.
            results_folder: The results folder.
            site_data_folder: Where the JSON files are written.

        Returns:
            None.

        Raises:
            None.
        """
        self.data_folder = data_folder
        self.results_folder = results_folder
        self.site_data_folder = site_data_folder

    def rows(self, file_name: str) -> list[dict]:
        """Reads a result table as rounded row dictionaries.

        Args:
            file_name: A CSV file in the results folder.

        Returns:
            One dictionary per row, with floats rounded to six places and
            NaN as None.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        frame = pd.read_csv(self.results_folder / file_name)
        frame = frame.round(6)
        frame = frame.astype(object).where(frame.notna(), None)
        return frame.to_dict(orient='records')

    def write(self) -> None:
        """Writes meta.json, summary.json and monthly.json.

        Args:
            None.

        Returns:
            None.

        Raises:
            FileNotFoundError: If an input file is missing.
        """
        self.site_data_folder.mkdir(parents=True, exist_ok=True)
        summary = {
            'main': self.rows('main_summary.csv'),
            'tables': self.rows('tables_summary.csv'),
            'variants': self.rows('variants_summary.csv'),
            'subperiods': self.rows('subperiods.csv'),
            'benchmarks': self.rows('long_only_vs_benchmarks.csv'),
            'exposure': self.rows('bab_dollar_exposure.csv'),
        }
        self.dump('summary.json', summary)
        monthly, months = self.monthly()
        self.dump('monthly.json', monthly)
        meta = {
            'first_month': months[0],
            'last_month': months[-1],
            'months': len(months),
            'specifications': 17,
            'generated': datetime.date.today().isoformat(),
        }
        self.dump('meta.json', meta)

    def monthly(self) -> tuple[dict, list[str]]:
        """Builds the monthly series the charts need.

        Args:
            None.

        Returns:
            A dictionary of series by name, and the list of months.

        Raises:
            FileNotFoundError: If an input file is missing.
        """
        inputs = StudyInputs(self.data_folder)
        main = pd.read_csv(
            self.results_folder / 'main_monthly_excess_returns.csv',
            index_col=0,
        )
        tables = pd.read_csv(
            self.results_folder / 'tables_monthly_excess_returns.csv',
            index_col=0,
        )
        sources = {'main': main, 'tables': tables}
        months = list(main.index)
        periods = pd.PeriodIndex(months, freq='M')
        free = inputs.risk_free.reindex(periods).to_numpy()
        series = {}
        for name, source in self.excess_series:
            for cost in ('gross', 'net'):
                column = sources[source][f'{name}_{cost}']
                series[f'{name}_{cost}'] = self.clean(column)
        series['market_excess'] = self.clean(main['market_excess'])
        for name, source in self.wealth_series:
            for cost in ('gross', 'net'):
                column = sources[source][f'{name}_{cost}']
                total = column.to_numpy() + free
                series[f'{name}_{cost}_total'] = self.clean(total)
        for label, file_name in self.benchmark_files:
            daily = inputs.market_data.index_returns_on(
                file_name, inputs.panel.sessions
            ).fillna(0.0)
            grouped = (1.0 + daily).groupby(daily.index.to_period('M')).prod()
            monthly = (grouped - 1.0).reindex(periods)
            series[f'{label}_total'] = self.clean(monthly.to_numpy())
        series['risk_free'] = self.clean(free)
        return {'months': months, 'series': series}, months

    def clean(self, values: object) -> list:
        """Rounds a series and turns NaN into None.

        Args:
            values: A pandas Series or a NumPy array of floats.

        Returns:
            A list of rounded floats with None for missing values.

        Raises:
            None.
        """
        array = pd.Series(list(values)).round(6)
        return [None if pd.isna(value) else float(value) for value in array]

    def dump(self, file_name: str, content: object) -> None:
        """Writes one JSON file.

        Args:
            file_name: The file's name.
            content: Anything JSON can hold.

        Returns:
            None.

        Raises:
            OSError: If the file cannot be written.
        """
        path = self.site_data_folder / file_name
        path.write_text(json.dumps(content, separators=(',', ':')))
