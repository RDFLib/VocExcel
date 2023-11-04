#!/bin/bash
P="$(cd ../; pwd)"
GP="$(cd ../../; pwd)"
PYTHON=$GP/.venv/bin/python  # point this variable to your Python installation
$PYTHON $P/"convert.py" "$@"
