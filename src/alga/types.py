"""Reglas estáticas; no evalúa valores ni ejecuta operaciones matriciales."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Type:
    kind: str
    shape: tuple[int, ...] = ()

    def __str__(self):
        return self.kind + ''.join(f'[{n}]' for n in self.shape)


SCALAR = Type('scalar')
STRING = Type('string')
BOOL = Type('bool')
VOID = Type('void')
ERROR = Type('error')
NUMERIC = {'scalar', 'vector', 'matrix'}


def binary(op, left, right):
    """Asociatividad izquierda aplicada por el visitor; * es producto algebraico."""
    if ERROR in (left, right):
        return ERROR
    if left.kind not in NUMERIC or right.kind not in NUMERIC:
        raise ValueError(f'Operación {op} no definida para {left} y {right}')
    if op in ('+', '-') and left == right:
        return left
    if op == '/' and right == SCALAR:
        return left
    if op == '*':
        if left == SCALAR:
            return right
        if right == SCALAR:
            return left
        if left.kind == right.kind == 'matrix' and left.shape[1] == right.shape[0]:
            return Type('matrix', (left.shape[0], right.shape[1]))
        if left.kind == 'matrix' and right.kind == 'vector' and left.shape[1] == right.shape[0]:
            return Type('vector', (left.shape[0],))
    raise ValueError(f'Operandos incompatibles para {op}: {left} y {right}')


def builtin(name, args):
    arities = {'transpose': 1, 'det': 1, 'trace': 1, 'norm': 1,
               'rows': 1, 'cols': 1, 'isSymmetric': 1, 'solve': 2, 'print': 1}
    if name not in arities:
        raise ValueError(f'Función {name} no definida')
    if len(args) != arities[name]:
        raise ValueError(f'{name} requiere {arities[name]} argumento(s); recibió {len(args)}')
    if ERROR in args:
        return ERROR
    first = args[0]
    if name == 'print' and first.kind in NUMERIC | {'string', 'bool'}:
        return VOID
    if name == 'norm' and first.kind == 'vector':
        return SCALAR
    if first.kind == 'matrix':
        rows, cols = first.shape
        if name == 'transpose':
            return Type('matrix', (cols, rows))
        if name in ('rows', 'cols'):
            return SCALAR
        if name == 'isSymmetric':
            return BOOL
        if rows == cols:
            if name in ('det', 'trace'):
                return SCALAR
            if name == 'solve' and args[1] == Type('vector', (rows,)):
                return Type('vector', (rows,))
    raise ValueError(f'Argumentos incompatibles para {name}: ' + ', '.join(map(str, args)))



def indexed(base, indices, texts):
    """Referencia completa, base cero. Solo literales firmados se evalúan aquí.

    Para expresiones dinámicas, enteridad y límites deberán verificarse durante
    la ejecución futura. No se promete probarlos mediante análisis de tipos.
    """
    from decimal import Decimal
    import re

    if ERROR in (base, *indices):
        return ERROR
    if base.kind not in {'vector', 'matrix'}:
        raise ValueError(f'No se puede indexar {base}')
    if len(indices) != len(base.shape):
        raise ValueError(f'{base} requiere {len(base.shape)} índice(s)')
    for axis, (typ, text, size) in enumerate(zip(indices, texts, base.shape), 1):
        if typ != SCALAR:
            raise ValueError(f'El índice {axis} requiere scalar; se obtuvo {typ}')
        if re.fullmatch(r'[+-]?[0-9]+(?:\.[0-9]+)?', text):
            value = Decimal(text)
            if value != value.to_integral_value():
                raise ValueError(f'El índice {axis} debe ser entero')
            if not 0 <= value < size:
                raise ValueError(f'Índice {axis} fuera de rango: {text}; rango [0, {size})')
    return SCALAR
