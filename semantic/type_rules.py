"""Reglas propias de Alga: comprueban tipos y dimensiones, no calculan valores."""
from decimal import Decimal
import re


class Type:
    def __init__(self, kind, shape=()):
        self.kind = kind
        self.shape = shape

    def __eq__(self, other):
        if not isinstance(other, Type):
            return False
        return self.kind == other.kind and self.shape == other.shape

    def __str__(self):
        text = self.kind
        for size in self.shape:
            text += f'[{size}]'
        return text

    def __repr__(self):
        return str(self)


SCALAR = Type('scalar')
STRING = Type('string')
BOOL = Type('bool')
VOID = Type('void')
ERROR = Type('error')
NUMERIC = ('scalar', 'vector', 'matrix')


def binary(op, left, right):
    if left == ERROR or right == ERROR:
        return ERROR
    if left.kind not in NUMERIC or right.kind not in NUMERIC:
        raise ValueError(f'Operación {op} no definida para {left} y {right}')

    if op == '+' or op == '-':
        if left == right:
            return left
    elif op == '/':
        if right == SCALAR:
            return left
    elif op == '*':
        if left == SCALAR:
            return right
        if right == SCALAR:
            return left
        if left.kind == 'matrix' and right.kind == 'matrix':
            if left.shape[1] == right.shape[0]:
                return Type('matrix', (left.shape[0], right.shape[1]))
        if left.kind == 'matrix' and right.kind == 'vector':
            if left.shape[1] == right.shape[0]:
                return Type('vector', (left.shape[0],))
    raise ValueError(f'Operandos incompatibles para {op}: {left} y {right}')


ARITIES = {
    'transpose': 1, 'det': 1, 'trace': 1, 'norm': 1,
    'rows': 1, 'cols': 1, 'isSymmetric': 1, 'solve': 2, 'print': 1,
}


def builtin(name, args):
    if name not in ARITIES:
        raise ValueError(f'Función {name} no definida')
    if len(args) != ARITIES[name]:
        raise ValueError(f'{name} requiere {ARITIES[name]} argumento(s); recibió {len(args)}')
    if ERROR in args:
        return ERROR

    first = args[0]
    if name == 'print':
        if first.kind in ('scalar', 'vector', 'matrix', 'string', 'bool'):
            return VOID
    elif name == 'norm':
        if first.kind == 'vector':
            return SCALAR
    elif first.kind == 'matrix':
        rows, cols = first.shape
        if name == 'transpose':
            return Type('matrix', (cols, rows))
        if name == 'rows' or name == 'cols':
            return SCALAR
        if name == 'isSymmetric':
            return BOOL
        if rows == cols:
            if name == 'det' or name == 'trace':
                return SCALAR
            if name == 'solve' and args[1] == Type('vector', (rows,)):
                return Type('vector', (rows,))

    descriptions = []
    for type_ in args:
        descriptions.append(str(type_))
    raise ValueError(f'Argumentos incompatibles para {name}: ' + ', '.join(descriptions))


def indexed(base, indices, texts):
    if base == ERROR or ERROR in indices:
        return ERROR
    if base.kind not in ('vector', 'matrix'):
        raise ValueError(f'No se puede indexar {base}')
    if len(indices) != len(base.shape):
        raise ValueError(f'{base} requiere {len(base.shape)} índice(s)')

    for position in range(len(indices)):
        axis = position + 1
        if indices[position] != SCALAR:
            raise ValueError(f'El índice {axis} requiere scalar; se obtuvo {indices[position]}')
        text = texts[position]
        size = base.shape[position]
        # Solo se conocen los valores de los índices literales con signo.
        # Decimal evita redondear un índice fraccionario hasta volverlo entero.
        if re.fullmatch(r'[+-]?[0-9]+(?:\.[0-9]+)?', text):
            value = Decimal(text)
            if value != value.to_integral_value():
                raise ValueError(f'El índice {axis} debe ser entero')
            if value < 0 or value >= size:
                raise ValueError(f'Índice {axis} fuera de rango: {text}; rango [0, {size})')
    return SCALAR
