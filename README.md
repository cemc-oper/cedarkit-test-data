# cedarkit-test-data

![Maturity-Sandbox](https://img.shields.io/badge/Maturity-Sandbox-F9D71C)
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
