"""
Main downloader module.
"""
import shutil
from pathlib import Path
from typing import Literal, Optional

import pandas as pd
import yaml

from .sources import GfsWisSource, GfsMusicDirSource, DataSource


def download_gfs_data(
    output_dir: Path,
    source: Literal["wis", "music-dir"] = "wis",
    start_time: Optional[pd.Timestamp] = None,
    forecast_time: Optional[pd.Timedelta] = None,
    storage_base: Optional[str] = None,
) -> Path:
    """
    Download GFS test data.

    Parameters
    ----------
    output_dir : Path
        Output directory for downloaded data.
    source : str
        Data source, either "wis" or "music-dir".
    start_time : pd.Timestamp, optional
        Start time. Defaults to yesterday 00Z.
    forecast_time : pd.Timedelta, optional
        Forecast time. Defaults to 24 hours.
    storage_base : str, optional
        Storage base directory for music-dir source.

    Returns
    -------
    Path
        Path to the downloaded file.
    """
    if start_time is None:
        start_time = pd.Timestamp.utcnow().floor(freq="D") - pd.Timedelta(days=1)
    if forecast_time is None:
        forecast_time = pd.Timedelta(hours=24)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Create data source
    data_source: DataSource
    if source == "wis":
        data_source = GfsWisSource()
    elif source == "music-dir":
        if storage_base is None:
            raise ValueError("storage_base is required for music-dir source")
        data_source = GfsMusicDirSource(storage_base=storage_base)
    else:
        raise ValueError(f"Unknown source: {source}")

    # Fetch data
    file_path = data_source.fetch(
        start_time=start_time,
        forecast_time=forecast_time,
        output_dir=output_dir,
    )

    # Write metadata
    metadata = data_source.get_metadata(
        start_time=start_time,
        forecast_time=forecast_time,
        file_name=file_path.name,
    )
    metadata_file_path = output_dir / "metadata.yaml"
    with open(metadata_file_path, "w") as f:
        yaml.safe_dump([metadata], f, default_flow_style=False)

    return file_path
