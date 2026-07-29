# cedarkit-test-data

![Maturity-Archived](https://img.shields.io/badge/Maturity-Archived-FE7D37)

> [!IMPORTANT]
> This project has been archived and is no longer maintained.
> It is kept available for historical reference.
>
> Its functionality has been merged into [cemc-oper/reki](https://github.com/cemc-oper/reki)
> (the built-in `test` source in `reki/sources/test.py` and the `reki-test-data`
> command). Please use `reki` instead — see "Migrating to reki" below.
>
> If this package remains installed alongside a newer `reki`, its
> `reki.sources` entry point shadows reki's built-in `test` source;
> uninstall it with `pip uninstall cedarkit-test-data`.

## Migrating to reki

The `test` source is built into `reki`; no plugin installation is needed.

Python API — unchanged call, works out of the box:

```python
import reki

# fetch (or reuse) the GFS test file and open it as a GRIB reader
data = reki.from_source("test", "gfs", output_dir="./data")
field = data.to_xarray(parameter="t", level_type="pl", level=850)
```

Command line — `cedarkit-test-data` becomes `reki-test-data`:

```bash
# before
cedarkit-test-data download gfs --source wis --output ./data

# after
reki-test-data download gfs --source wis --output ./data
```

The downloader API moved from `cedarkit_test_data` to `reki.sources.test`:

```python
# before
from cedarkit_test_data import download_gfs_data

# after
from reki.sources.test import download_gfs_data
```

---

*The sections below are kept for historical reference.*

![GitHub Release](https://img.shields.io/github/v/release/cemc-oper/cedarkit-test-data)
![PyPI - Version](https://img.shields.io/pypi/v/cedarkit-test-data)
![GitHub License](https://img.shields.io/github/license/cemc-oper/cedarkit-test-data)
![GitHub Action Workflow Status](https://github.com/cemc-oper/cedarkit-test-data/actions/workflows/ci.yaml/badge.svg)

A test data downloader that prepares test datasets for the cedarkit toolkits.

## Installation

```bash
pip install -e .
```

## Usage

### Command line

Download GFS data from WIS:

```bash
cedarkit-test-data download gfs --source wis --output ./data
```

Copy data from a locally mounted directory:

```bash
cedarkit-test-data download gfs --source music-dir --storage-base M: --output ./data
```

### Python API

```python
from cedarkit_test_data import download_gfs_data
from pathlib import Path

# Download to a target directory
download_gfs_data(
    output_dir=Path("./data"),
    source="wis",
)
```

### reki `test` source

Once cedarkit-test-data is installed, it registers a `test` source in the
`reki.sources` entry point group, so test datasets can be loaded through
reki's unified entry point:

```python
import reki

# fetch (or reuse) the GFS test file and open it as a GRIB reader
data = reki.from_source("test", "gfs", output_dir="./data")
field = data.to_xarray(parameter="t", level_type="pl", level=850)
```

Downloads are idempotent: an existing file in `output_dir` is reused and
no network access happens.

## Supported data sources

- `wis`: download from the CMA WIS data service
- `music-dir`: copy from a locally mounted music-dir directory

## Supported data types

- `gfs`: CMA GRAPES-GFS global model data

## License

Licensed under the [Apache License, Version 2.0](LICENSE).
