"""The loop's modules are plain scripts in .flow/loop/; the tests import them from there."""

import sys
from pathlib import Path

LOOP_DIR = Path(__file__).resolve().parents[1]
if str(LOOP_DIR) not in sys.path:
    sys.path.insert(0, str(LOOP_DIR))
