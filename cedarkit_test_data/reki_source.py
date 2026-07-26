"""reki ``test`` source: fetch well-known test datasets through reki.

This module is registered in the ``reki.sources`` entry point group,
so ``reki.from_source("test", "gfs", ...)`` works once cedarkit-test-data
is installed. reki itself does not depend on this package; the source is
discovered at runtime (see ``doc/reki-future-development.md`` §9.1).
"""

import tempfile
from pathlib import Path
from typing import Literal, Optional, Union

import pandas as pd

from reki.core import Source
from reki.sources import get_source

#: default directory for downloaded test data files.
DEFAULT_DATA_DIR = Path(tempfile.gettempdir()) / "cedarkit-test-data"

#: supported dataset names.
DATASETS = ("gfs",)


class TestSource(Source):
    """Fetch a test dataset file, then read it as a local file.

    Parameters
    ----------
    dataset_name
        which dataset to fetch. Currently only ``"gfs"`` (a GRIB2 file
        of CMA-GFS from the WIS website or a mounted music-dir
        directory).
    output_dir
        directory the data file is downloaded to. Defaults to a
        per-user temp directory. Downloads are idempotent: an existing
        file is reused (see ``reki.sources.url.download_file``).
    source
        fetch backend, ``"wis"`` (HTTP download) or ``"music-dir"``
        (copy from a mounted directory, requires ``storage_base``).
    storage_base
        storage base directory for ``source="music-dir"``.
    start_time
        model start time. Defaults to yesterday 00Z.
    forecast_time
        forecast time. Defaults to 24 hours.
    """

    #: not a pytest test class despite the name.
    __test__ = False

    #: fetching the dataset is remote I/O; defer it to first use.
    remote = True

    def __init__(
            self,
            dataset_name: str = "gfs",
            output_dir: Optional[Union[str, Path]] = None,
            source: Literal["wis", "music-dir"] = "wis",
            storage_base: Optional[str] = None,
            start_time: Optional[pd.Timestamp] = None,
            forecast_time: Optional[pd.Timedelta] = None,
            **kwargs,
    ):
        super().__init__(**kwargs)
        if dataset_name not in DATASETS:
            raise ValueError(
                f"unknown test dataset: {dataset_name!r}, "
                f"expected one of {DATASETS}"
            )
        self.dataset_name = dataset_name
        self.output_dir = (
            Path(output_dir) if output_dir is not None else DEFAULT_DATA_DIR
        )
        self.fetch_source = source
        self.storage_base = storage_base
        self.start_time = start_time
        self.forecast_time = forecast_time

    def mutate(self) -> Source:
        from cedarkit_test_data.downloader import download_gfs_data

        path = download_gfs_data(
            output_dir=self.output_dir,
            source=self.fetch_source,
            start_time=self.start_time,
            forecast_time=self.forecast_time,
            storage_base=self.storage_base,
        )
        return get_source("file", path)

    def __repr__(self):
        return f"TestSource({self.dataset_name!r})"


source = TestSource
