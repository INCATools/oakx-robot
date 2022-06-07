import os
import pprint
from pathlib import Path

ROOT = os.path.abspath(os.path.dirname(__file__))
INPUT_DIR = Path(ROOT) / 'input'
OUTPUT_DIR = Path(ROOT) / 'output'

CHEBI_NUCLEUS = 'CHEBI:33252'
NUCLEUS = 'GO:0005634'
NUCLEAR_ENVELOPE = 'GO:0005635'
THYLAKOID = 'GO:0009579'


def output_path(fn: str) -> str:
    return str(Path(OUTPUT_DIR) / fn)
