#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv --system-site-packages .venv
.venv/bin/python -m pip install --no-cache-dir --disable-pip-version-check -r requirements.txt
.venv/bin/python -m tools.prepare_font --check
.venv/bin/python -m tools.content --check
.venv/bin/python -m tools.generate
.venv/bin/python -m unittest discover -s tests -v
