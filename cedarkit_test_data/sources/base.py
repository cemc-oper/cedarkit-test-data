"""
Base class for data sources.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import pandas as pd


class DataSource(ABC):
    """Abstract base class for data sources."""

    @abstractmethod
    def get_file_path_or_url(
        self,
        start_time: pd.Timestamp,
        forecast_time: pd.Timedelta,
        **kwargs,
    ) -> str | Path:
        """Get the file path or URL for the data file."""
        pass

    @abstractmethod
    def fetch(
        self,
        start_time: pd.Timestamp,
        forecast_time: pd.Timedelta,
        output_dir: Path,
        **kwargs,
    ) -> Path:
        """Fetch the data file to the output directory."""
        pass

    @abstractmethod
    def get_metadata(
        self,
        start_time: pd.Timestamp,
        forecast_time: pd.Timedelta,
        file_name: str,
        **kwargs,
    ) -> dict[str, Any]:
        """Get metadata for the downloaded file."""
        pass
