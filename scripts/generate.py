"""Compatibilidad con el comando anterior; la generación está en el Makefile."""
from pathlib import Path
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(['make', 'generate'], cwd=root)
    return result.returncode


if __name__ == '__main__':
    sys.exit(main())
