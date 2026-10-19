"""Builds the JSON data files for the companion page."""

import pathlib
import sys

from frazzini_pedersen_india.bab.site_snapshot import SiteSnapshot


class BuildSnapshotApplication:
    """Command-line step that writes src/<package>/site/data."""

    def run(
        self,
        data_folder: pathlib.Path,
        results_folder: pathlib.Path,
        site_data_folder: pathlib.Path,
    ) -> None:
        """Writes the snapshot.

        Args:
            data_folder: The study's data folder.
            results_folder: The results folder.
            site_data_folder: The page's data folder.

        Returns:
            None.

        Raises:
            FileNotFoundError: If an input file is missing.
        """
        SiteSnapshot(data_folder, results_folder, site_data_folder).write()


if __name__ == '__main__':
    BuildSnapshotApplication().run(
        pathlib.Path(sys.argv[1]),
        pathlib.Path(sys.argv[2]),
        pathlib.Path(sys.argv[3]),
    )
