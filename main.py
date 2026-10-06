"""Entrada directa: python3 main.py archivo.alga [--phase ...] [--json]."""
from pathlib import Path
import sys


if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
    from alga.driver import main

    sys.exit(main())
