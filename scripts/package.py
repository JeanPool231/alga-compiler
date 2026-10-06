"""Copia entregables y fuentes; nunca recorre directorios privados del entorno."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIRECTORIES = ['docs', 'grammar', 'src', 'scripts', 'tests', 'examples',
               'entregables', 'clases', '.github']
ROOT_FILES = ['README.md', 'main.py', 'requirements.txt', '.gitignore',
              'Teoria_de_Compiladores_Trabajo_Parcial_y_Final.pdf',
              'Grupo 2 Trabajo Parcial Compiladores(1).docx']
EXCLUDED = {'__pycache__', 'generated', '.venv'}


def main():
    destination = ROOT / 'dist/alga_hito1.zip'
    destination.parent.mkdir(exist_ok=True)
    files = [ROOT / name for name in ROOT_FILES]
    for folder in DIRECTORIES:
        files.extend(p for p in (ROOT / folder).rglob('*')
                     if p.is_file() and not p.is_symlink()
                     and not EXCLUDED.intersection(p.relative_to(ROOT).parts)
                     and p.suffix not in ('.pyc', '.pyo'))
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):
            archive.write(path, 'alga_hito1/' + path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('El ZIP no pasó la comprobación de integridad')
    print(f'{destination}: {len(files)} archivos; integridad verificada')


if __name__ == '__main__':
    main()
