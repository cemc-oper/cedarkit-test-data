# cedarkit-test-data

> [!IMPORTANT]
> **This repository has changed purpose.** It is no longer a Python
> package — it is now the **data-generation project and release-asset
> store** for frozen test datasets used by the
> [cedarkit](https://github.com/cemc-oper/cedarkit) /
> [reki](https://github.com/cemc-oper/reki) documentation and tests.
>
> - The old installable package is archived on the
>   [`legacy/test-data-package`](https://github.com/cemc-oper/cedarkit-test-data/tree/legacy/test-data-package)
>   branch. **Do not `pip install` it**: its `reki.sources` entry point
>   shadows reki's built-in `test` source. Its functionality was merged
>   into reki (built-in `test` source + `reki-test-data` CLI).
> - The actual data files are **GitHub release assets**, not files in
>   this repo. See [Releases](https://github.com/cemc-oper/cedarkit-test-data/releases).

## What this repository is

1. **Generation scripts** (`scripts/`) that produce small, frozen test
   datasets from ECMWF IFS open data (CC-BY-4.0).
2. **Release assets**: each data version is published as a GitHub
   release tagged with an independent calver (`v<year>.<month>.<rev>`,
   e.g. `v2026.8.0`), decoupled from reki releases. Data semantics
   (model / domain / run date / forecast step) live in the asset file
   names, not in the version number.

## Data inventory

Asset naming: `ifs_<domain>_<run-date><run-time>_f<step>.grib2`

| Asset | Model | Run | Step | Parameters | Domain | Intended use |
|---|---|---|---|---|---|---|
| `ifs_eastasia_2026081800_f024.grib2` | ECMWF IFS HRES 0.25° | 2026-08-18 00Z | +24h | 2t, 2d, 10u, 10v, msl, tp | 0–60N, 60–150E | read / plot examples |
| `ifs_global_2026081800_f024.grib2` | ECMWF IFS HRES 0.25° | 2026-08-18 00Z | +24h | 2t | global | regrid / area operator examples |

## Using the data

The recommended entry point is reki's built-in `test` source
(`ecmwf_ifs` dataset), which downloads from the release URL and opens
the file in one call:

```python
import reki

ds = reki.from_source("test", "ecmwf_ifs")           # frozen East-Asia subset
field = ds.sel(parameter="2t", level_type="heightAboveGround", level=2).to_xarray()
```

or the CLI:

```bash
reki-test-data download ecmwf_ifs --domain eastasia -o ./data
```

Direct release-URL reference (advanced):

```
https://github.com/cemc-oper/cedarkit-test-data/releases/download/v2026.8.0/ifs_eastasia_2026081800_f024.grib2
```

## Regenerating the data

ECMWF open data only keeps the last few run cycles, so regeneration
means: pick a current run, pin it in the script, generate, tag, release.

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
# also required on PATH: cdo, grib_copy, grib_ls (apt install cdo libeccodes-tools)

# pin DATE/TIME/STEP in scripts/generate_ifs.py first, then:
.venv/bin/python scripts/generate_ifs.py --output-dir build

git commit -am "data: regenerate IFS assets (<run date>)"
git tag v<yyyy>.<m>.<rev>
git push origin main --tags
scripts/upload_release.sh v<yyyy>.<m>.<rev> build/ifs_*.grib2
```

Then bump the URL constant in reki (`reki/sources/test.py`,
`ECMWF_IFS_RELEASE_TAG` / `ECMWF_IFS_ASSETS`) via a reviewable PR.

## License and attribution

- The **scripts** in this repository are under the repository's
  original license (see [LICENSE](LICENSE)).
- The **data assets** contain modified ECMWF IFS open data,
  © ECMWF, licensed under
  [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
  See [NOTICE](NOTICE). When using the data, attribute ECMWF.

## Historical note

Releases up to `v2026.7.0` (and PyPI package `cedarkit-test-data`) were
the old Python test-data package; see the `legacy/test-data-package`
branch. Data releases start at `v2026.8.0`.
