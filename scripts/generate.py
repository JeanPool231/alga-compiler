"""Genera Python desde ambos G4 con ANTLR 4.13.2. Requiere Java y el JAR."""
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
JAR = Path(os.environ.get('ANTLR_JAR', ROOT / 'tools/antlr-4.13.2-complete.jar')).resolve()
OUTPUT = ROOT / 'src/alga/generated'


def main():
    if not shutil.which('java') or not JAR.is_file():
        print('Se requiere Java y ANTLR 4.13.2. Consulte README.md; '
              'ANTLR_JAR permite indicar el JAR local.', file=sys.stderr)
        return 2
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for grammar in ('AlgaLexer.g4', 'AlgaParser.g4'):
        subprocess.run(['java', '-jar', str(JAR), '-Dlanguage=Python3', '-visitor',
                        '-no-listener', '-Werror', '-o', str(OUTPUT), '-lib', str(OUTPUT),
                        grammar], cwd=ROOT / 'grammar', check=True)
    (OUTPUT / '__init__.py').write_text('', encoding='utf-8')
    print('Analizadores generados en src/alga/generated')
    return 0


if __name__ == '__main__':
    sys.exit(main())
