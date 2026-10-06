"""Crea el ZIP de fuentes y materiales de entrega sin incluir dependencias."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = [
    'README.md', 'main.py', 'Makefile', 'requirements.txt', '.gitignore',
    'test_valid.txt', 'test_invalid.txt',
    'Teoria_de_Compiladores_Trabajo_Parcial_y_Final-1.pdf',
    'Grupo 2 Trabajo Parcial Compiladores.docx',
]
DIRECTORIES = ['grammar', 'semantic', 'scripts', 'tests', 'examples', 'docs', 'clases', 'entregables']


def main():
    files = []
    for name in ROOT_FILES:
        path = ROOT / name
        if not path.is_file():
            raise FileNotFoundError(f'Falta un archivo de entrega: {name}')
        files.append(path)
    files.append(ROOT / 'gen/__init__.py')
    for folder in DIRECTORIES:
        for path in sorted((ROOT / folder).rglob('*')):
            if not path.is_file() or path.is_symlink():
                continue
            if '__pycache__' in path.parts or path.suffix in ('.pyc', '.pyo'):
                continue
            if path.name == '.Rhistory':
                continue
            files.append(path)

    destination = ROOT / 'dist/alga_hito1.zip'
    destination.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, 'alga_hito1/' + path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('El ZIP no pasó la comprobación de integridad')
    print(f'{destination}: {len(files)} archivos; integridad verificada')


if __name__ == '__main__':
    main()
