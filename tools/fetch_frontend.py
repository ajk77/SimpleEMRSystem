#!/usr/bin/env python3
"""Download pinned case-viewer JS (jQuery, Highstock, Bootstrap) into static/js.

Run from the repo root (install.sh / install.bat does this). Files are gitignored;
do not commit them. Highcharts 8.2.2 is commercial software; a license is still
required for non-eval use.
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "SEMRinterface" / "static" / "js"

ASSETS = (
    {
        "url": "https://code.jquery.com/jquery-3.6.4.min.js",
        "name": "jquery-3.6.4.min.js",
        "min_bytes": 80000,
    },
    {
        "url": "https://cdnjs.cloudflare.com/ajax/libs/highcharts/8.2.2/highstock.js",
        "name": "highstock-8.2.2.js",
        "min_bytes": 300000,
    },
    {
        "url": (
            "https://cdn.jsdelivr.net/gh/ajk77/SimpleEMRSystem@a2c35bf/"
            "SEMRinterface/static/js/bootstrap.min.js"
        ),
        "name": "bootstrap.min.js",
        "min_bytes": 30000,
    },
)


def fetch(asset: dict) -> None:
    dest = DEST / asset["name"]
    print(f"  {asset['name']} <- {asset['url']}")
    req = urllib.request.Request(
        asset["url"],
        headers={"User-Agent": "SimpleEMRSystem-fetch_frontend"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    if len(data) < asset["min_bytes"]:
        raise SystemExit(
            f"ERROR: {asset['name']} was {len(data)} bytes "
            f"(expected at least {asset['min_bytes']})"
        )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    print(f"    {len(data)} bytes")


def main() -> int:
    print("Downloading pinned frontend scripts...")
    DEST.mkdir(parents=True, exist_ok=True)
    for asset in ASSETS:
        fetch(asset)
    return 0


if __name__ == "__main__":
    sys.exit(main())
