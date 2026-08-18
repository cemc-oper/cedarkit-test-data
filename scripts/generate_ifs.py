#!/usr/bin/env python3
"""Generate the frozen ECMWF IFS open-data test assets for cedarkit-test-data.

What it does
------------
1. Downloads one IFS HRES 0.25° forecast step (surface parameters) from
   ECMWF open data (CC-BY-4.0) via the ``ecmwf-opendata`` client.
2. Produces two release assets:

   - ``ifs_eastasia_<date><time>_f<step>.grib2``
     East-Asia subset: parameters 2t/2d/10u/10v/msl/tp, domain
     0–60N, 60–150E (``cdo sellonlatbox``). For read/plot examples.
   - ``ifs_global_<date><time>_f<step>.grib2``
     Global field, parameter 2t only (``grib_copy`` key filter). For
     regrid/area operator examples.

3. Prints the sha256 of each asset.

The run date/time/step are **pinned below**: ECMWF open data only keeps
the last few run cycles, so an asset must be generated once and frozen
into a GitHub release. To regenerate, update the pinned constants, run
this script, tag the commit and create the release (see README).

Requirements: ``ecmwf-opendata`` (pip), ``cdo`` and ecCodes ``grib_copy``
(system packages or conda). No dependency on reki.
"""

import argparse
import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Pinned data semantics — edit these when regenerating a dataset, then tag.
# ---------------------------------------------------------------------------
DATE = 20260818        # run date, YYYYMMDD
TIME = 0               # run time, UTC hour (0 or 12)
STEP = 24              # forecast step in hours
PARAMS = ["2t", "2d", "10u", "10v", "msl", "tp"]  # east-asia subset params
GLOBAL_PARAMS = ["2t"]                            # global-asset params
EASTASIA_BBOX = (60.0, 150.0, 0.0, 60.0)          # lonmin, lonmax, latmin, latmax

TYPE = "fc"
STREAM = "oper"
LEVTYPE = "sfc"


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run(cmd, check=True)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def asset_name(domain: str, date: int, time: int, step: int) -> str:
    return f"ifs_{domain}_{date}{time:02d}_f{step:03d}.grib2"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--date", type=int, default=DATE,
        help="run date YYYYMMDD (negative N = N days ago, for probing only; "
             "pin the resolved date in this file afterwards)",
    )
    parser.add_argument("--time", type=int, default=TIME, choices=(0, 6, 12, 18))
    parser.add_argument("--step", type=int, default=STEP)
    parser.add_argument("--output-dir", type=Path, default=Path("build"))
    parser.add_argument(
        "--full-file", type=Path, default=None,
        help="reuse an already-downloaded full-field GRIB2 file instead of "
             "downloading (useful on flaky networks; must match the pinned "
             "run date/step)",
    )
    args = parser.parse_args()

    for tool in ("cdo", "grib_copy"):
        if shutil.which(tool) is None:
            sys.exit(f"error: {tool!r} not found on PATH (install cdo / ecCodes)")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    from ecmwf.opendata import Client

    with tempfile.TemporaryDirectory() as tmp:
        full = Path(tmp) / "ifs_full.grib2"
        if args.full_file is not None:
            print(f"reusing pre-downloaded file: {args.full_file}")
            shutil.copy(args.full_file, full)
        else:
            from ecmwf.opendata import Client

            Client().retrieve(
                date=args.date,
                time=args.time,
                step=args.step,
                stream=STREAM,
                type=TYPE,
                levtype=LEVTYPE,
                param=PARAMS,
                target=str(full),
            )

        # Resolve the actual run date for naming when probing with --date=-N.
        out = subprocess.run(
            ["grib_ls", "-p", "dataDate,dataTime", str(full)],
            check=True, capture_output=True, text=True,
        ).stdout
        for line in out.splitlines():
            tokens = line.split()
            if len(tokens) >= 2 and all(t.isdigit() for t in tokens[:2]):
                run_date, run_time = int(tokens[0]), int(tokens[1]) // 100
                break
        else:
            sys.exit(f"error: could not parse grib_ls output:\n{out}")

        eastasia = args.output_dir / asset_name("eastasia", run_date, run_time, args.step)
        global_ = args.output_dir / asset_name("global", run_date, run_time, args.step)

        # East-Asia subset: clip domain (download already limited the params).
        lonmin, lonmax, latmin, latmax = EASTASIA_BBOX
        run([
            "cdo", "-s", "-f", "grb2",
            f"sellonlatbox,{lonmin},{lonmax},{latmin},{latmax}",
            str(full), str(eastasia),
        ])

        # Global asset: keep only the wanted parameters.
        run([
            "grib_copy", "-w",
            "/".join(f"shortName={p}" for p in GLOBAL_PARAMS),
            str(full), str(global_),
        ])

    for asset in (eastasia, global_):
        print(f"{sha256(asset)}  {asset.name}  ({asset.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
