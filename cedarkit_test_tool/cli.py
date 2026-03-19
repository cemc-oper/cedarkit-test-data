"""
Command line interface for cedarkit-test-tool.
"""
from pathlib import Path

import click
import pandas as pd

from .downloader import download_gfs_data


@click.group()
@click.version_option()
def main():
    """cedarkit-test-tool: Test data downloader for cedarkit toolkits."""
    pass


@main.group()
def download():
    """Download test data."""
    pass


@download.command("gfs")
@click.option(
    "--source",
    type=click.Choice(["wis", "music-dir"]),
    default="wis",
    help="Data source (wis or music-dir)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=Path("."),
    help="Output directory",
)
@click.option(
    "--storage-base",
    type=str,
    default=None,
    help="Storage base directory for music-dir source",
)
@click.option(
    "--start-time",
    type=str,
    default=None,
    help="Start time in ISO format (e.g., 2024-01-01T00:00:00Z) or YYYYMMDDHH",
)
@click.option(
    "--forecast-time",
    type=str,
    default="24h",
    help="Forecast time in pd.Timedelta format (e.g., 24h, 1d, 48h)",
)
def download_gfs(
    source: str,
    output: Path,
    storage_base: str | None,
    start_time: str | None,
    forecast_time: str,
):
    """Download GFS test data."""
    if start_time:
        if len(start_time) == 10 and start_time.isdigit():
            start_ts = pd.Timestamp(start_time, tz="UTC")
        else:
            start_ts = pd.Timestamp(start_time)
    else:
        start_ts = pd.Timestamp.utcnow().floor(freq="D") - pd.Timedelta(days=1)
    forecast_td = pd.Timedelta(forecast_time)

    click.echo(f"Source: {source}")
    click.echo(f"Start time: {start_ts.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    click.echo(f"Forecast time: {forecast_time}")
    click.echo(f"Output directory: {output.absolute()}")
    click.echo("Downloading...")

    try:
        file_path = download_gfs_data(
            output_dir=output,
            source=source,
            start_time=start_ts,
            forecast_time=forecast_td,
            storage_base=storage_base,
        )
        click.echo(f"Downloaded to: {file_path}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
