"""
GFS data sources.
"""
import shutil
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pandas as pd
import requests
from tqdm import tqdm

from .base import DataSource


GFS_BASE_URL_TEMPLATE = "http://data.wis.cma.cn/DCPC_WMC_BJ/open/nwp/gmf_gra/t{start_hour_str}00/f0_f240_6h/"
GFS_FILE_NAME_TEMPLATE = "Z_NAFP_C_BABJ_{start_time_str}0000_P_NWPC-GRAPES-GFS-GLB-{forecast_hour_str}00.grib2"
GFS_BASE_PATH_TEMPLATE = "{storage_base}/DATA/NAFP/NMC/GRAPES-GFS-GLB/{start_year_str}/{start_date_str}/"


class GfsWisSource(DataSource):
    """GFS data source from CMA WIS website."""

    def get_file_path_or_url(
        self,
        start_time: pd.Timestamp,
        forecast_time: pd.Timedelta,
        **kwargs,
    ) -> str:
        start_hour_str = start_time.strftime("%H")
        start_time_str = start_time.strftime("%Y%m%d%H")
        forecast_hour_str = f"{int(forecast_time / pd.Timedelta(hours=1)):03}"

        file_url = GFS_BASE_URL_TEMPLATE.format(
            start_hour_str=start_hour_str,
        ) + GFS_FILE_NAME_TEMPLATE.format(
            start_time_str=start_time_str,
            forecast_hour_str=forecast_hour_str
        )
        return file_url

    def fetch(
        self,
        start_time: pd.Timestamp,
        forecast_time: pd.Timedelta,
        output_dir: Path,
        **kwargs,
    ) -> Path:
        file_url = self.get_file_path_or_url(start_time, forecast_time)
        
        parsed_url = urlparse(file_url)
        path = parsed_url.path
        file_name = path.rstrip('/').split('/')[-1]
        file_path = output_dir / file_name

        self._download_file(url=file_url, file_path=file_path)
        return file_path

    def get_metadata(
        self,
        start_time: pd.Timestamp,
        forecast_time: pd.Timedelta,
        file_name: str,
        **kwargs,
    ) -> dict[str, Any]:
        return {
            "file_name": file_name,
            "system": "cma_gfs",
            "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "forecast_time": forecast_time.isoformat(),
            "source": "wis",
        }

    @staticmethod
    def _download_file(url: str, file_path: Path) -> None:
        file_name = file_path.name
        response = requests.head(url)
        total_size = int(response.headers.get('content-length', 0))

        with requests.get(url, stream=True) as r, open(file_path, 'wb') as f, tqdm(
            total=total_size, unit='B', unit_scale=True, desc=file_name
        ) as progress_bar:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    progress_bar.update(len(chunk))


class GfsMusicDirSource(DataSource):
    """GFS data source from local mounted music-dir directory."""

    def __init__(self, storage_base: str):
        self.storage_base = storage_base

    def get_file_path_or_url(
        self,
        start_time: pd.Timestamp,
        forecast_time: pd.Timedelta,
        **kwargs,
    ) -> Path:
        start_year_str = start_time.strftime("%Y")
        start_date_str = start_time.strftime("%Y%m%d")
        start_time_str = start_time.strftime("%Y%m%d%H")
        forecast_hour_str = f"{int(forecast_time / pd.Timedelta(hours=1)):03}"

        file_path = Path(
            GFS_BASE_PATH_TEMPLATE.format(
                start_year_str=start_year_str,
                start_date_str=start_date_str,
                storage_base=self.storage_base,
            ),
            GFS_FILE_NAME_TEMPLATE.format(
                start_time_str=start_time_str,
                forecast_hour_str=forecast_hour_str
            ),
        )
        return file_path

    def fetch(
        self,
        start_time: pd.Timestamp,
        forecast_time: pd.Timedelta,
        output_dir: Path,
        **kwargs,
    ) -> Path:
        source_file_path = self.get_file_path_or_url(start_time, forecast_time)
        file_name = source_file_path.name
        file_path = output_dir / file_name

        shutil.copy(source_file_path, file_path)
        return file_path

    def get_metadata(
        self,
        start_time: pd.Timestamp,
        forecast_time: pd.Timedelta,
        file_name: str,
        **kwargs,
    ) -> dict[str, Any]:
        return {
            "file_name": file_name,
            "system": "cma_gfs",
            "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "forecast_time": forecast_time.isoformat(),
            "source": "music-dir",
        }
