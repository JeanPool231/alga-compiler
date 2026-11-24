import csv
import io
import math
import os
import re

from .type_rules import Type

MAX_BYTES = 5_000_000
MAX_VALUES = 1_000_000

_NUMBER = re.compile(r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$")


class CsvError(Exception):
    pass


class Dataset:
    __slots__ = ("rows", "cols", "data", "type_")

    def __init__(self, rows, cols, data):
        self.rows, self.cols, self.data = rows, cols, data

        if rows == 1 or cols == 1:
            self.type_ = Type("vector", (rows * cols,))
        else:
            self.type_ = Type("matrix", (rows, cols))


def _resolve(base_dir, path):
    if base_dir is None:
        raise CsvError("no esta disponible aqui")
    
    if not path:
        raise CsvError("la ruta esta vacía")
    
    if os.path.isabs(path) or re.match(r"^[A-Za-z]:", path):
        raise CsvError(f"la ruta '{path}' debe ser relativa a la ubicacion del programa")
    
    base = os.path.realpath(base_dir)
    full = os.path.realpath(os.path.join(base, path))
    
    try:
        inside = os.path.commonpath([base, full]) == base
    except ValueError:
        inside = False
    if not inside:
        raise CsvError(f"la ruta '{path}' sale del directorio del programa")
    return full


def load_csv(base_dir, path, sep=","):
    if len(sep) != 1 or sep in '"\r\n':
        raise CsvError("el separador debe ser un solo caracter")
    
    full = _resolve(base_dir, path)
    
    try:
        if not os.path.exists(full):
            raise CsvError(f"no se encontro el archivo '{path}'")
        if not os.path.isfile(full):
            raise CsvError(f"'{path}' no es un archivo")
        if os.path.getsize(full) > MAX_BYTES:
            raise CsvError(f"'{path}' excede el maximo de {MAX_BYTES} bytes")
        with open(full, "rb") as handle:
            text = handle.read().decode("utf-8-sig")
            
    except UnicodeDecodeError:
        raise CsvError(f"'{path}' no es texto UTF-8")
    except OSError as error:
        raise CsvError(f"no se pudo leer '{path}': {error.strerror or error}")

    reader = csv.reader(io.StringIO(text, newline=""), delimiter=sep, strict=True)
    data, rows, cols = [], 0, None
    
    try:
        for row in reader:
            if not row:
                continue
            
            line = reader.line_num
            
            if cols is None:
                cols = len(row)
            elif len(row) != cols:
                raise CsvError(
                    f"la linea {line} tiene {len(row)} valores y la primera fila tiene {cols}; "
                    "no se puede deducir la forma"
                )
                
            for column, cell in enumerate(row, 1):
                cell = cell.strip()
                if not _NUMBER.match(cell):
                    shown = repr(cell[:20]) if cell else "una celda vacía"
                    raise CsvError(f"valor no numérico en la línea {line}, columna {column}: {shown}")
                
                value = float(cell)
                if not math.isfinite(value):
                    raise CsvError(f"numero fuera de rango en la línea {line}, columna {column}")
                
                data.append(value)
            rows += 1
            
            if len(data) > MAX_VALUES:
                raise CsvError(f"el archivo excede el máximo de {MAX_VALUES} valores")
            
    except csv.Error as error:
        raise CsvError(f"formato CSV invalido: {error}")
    
    if rows == 0:
        raise CsvError(f"'{path}' esta vacío")
    
    return Dataset(rows, cols, data)
