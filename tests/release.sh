#!/bin/sh
# Release gate: the checks on the committed pages, then a planted fault that the checks must catch.
set -e
cd "$(dirname "$0")/.."
python3 -I -B tests/check_site.py .
# Planted fault: a tool whose line is empty must fail the check even after a rebuild.
rm -rf tests/.work; mkdir -p tests/.work/mut/site tests/.work/mut/scripts tests/.work/mut/tests
python3 -I -B -c '
import json,sys
d=json.load(open("site/tools.json")); d["tools"][0]["line"]=""
json.dump(d,open("tests/.work/mut/site/tools.json","w"),indent=2)'
cp scripts/build_site.py tests/.work/mut/scripts/; cp tests/check_site.py tests/.work/mut/tests/; cp .nojekyll tests/.work/mut/
python3 -I -B scripts/build_site.py tests/.work/mut >/dev/null
if python3 -I -B tests/check_site.py tests/.work/mut >/dev/null 2>&1; then echo "FAIL an empty tool line passed the checks"; exit 1; fi
rm -rf tests/.work
echo "gate PASS"
