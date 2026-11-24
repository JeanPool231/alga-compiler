import math
from semantic.literals import decode_string

class AlgaRuntimeError(Exception):
    def __init__(self, message, pos=None):
        super().__init__(message)
        self.message = message
        self.pos = pos  # (línea, columna) o None

    def __str__(self):
        if self.pos:
            return f"ejecución:{self.pos[0]}:{self.pos[1]}: {self.message}"
        return f"ejecución: {self.message}"


EPS = 1e-12


class Tensor:
    __slots__ = ("shape", "data")

    def __init__(self, shape, data=None):
        self.shape = tuple(shape)
        if data is None:
            size = 1
            for dim in self.shape:
                size *= dim
            data = [0.0] * size
        self.data = data

    def copy(self):
        return Tensor(self.shape, list(self.data))

    def rows_list(self):
        rows, cols = self.shape
        return [self.data[r * cols : (r + 1) * cols] for r in range(rows)]


def _same_shape(a, b, op):
    if a.shape != b.shape:
        raise AlgaRuntimeError(f"Formas incompatibles en '{op}': {a.shape} y {b.shape}")


def add(a, b):
    if isinstance(a, Tensor):
        _same_shape(a, b, "+")
        return Tensor(a.shape, [x + y for x, y in zip(a.data, b.data)])
    return a + b


def sub(a, b):
    if isinstance(a, Tensor):
        _same_shape(a, b, "-")
        return Tensor(a.shape, [x - y for x, y in zip(a.data, b.data)])
    return a - b


def mul(a, b):
    a_t, b_t = isinstance(a, Tensor), isinstance(b, Tensor)
    if not a_t and not b_t:
        return a * b
    if not a_t:
        return Tensor(b.shape, [a * y for y in b.data])
    if not b_t:
        return Tensor(a.shape, [x * b for x in a.data])
    return matmul(a, b)


def matmul(a, b):
    if len(a.shape) != 2 or a.shape[1] != b.shape[0]:
        raise AlgaRuntimeError(
            f"Dimensiones incompatibles en '*': {a.shape} y {b.shape}"
        )
    n, m = a.shape
    p = b.shape[1] if len(b.shape) == 2 else 1
    out = [0.0] * (n * p)
    for i in range(n):
        for j in range(p):
            total = 0.0
            for k in range(m):
                total += a.data[i * m + k] * b.data[k * p + j]
            out[i * p + j] = total
    return Tensor((n, p) if len(b.shape) == 2 else (n,), out)


def div(a, b):
    if isinstance(b, Tensor):
        raise AlgaRuntimeError("No se puede dividir entre un vector o matriz")
    if b == 0:
        raise AlgaRuntimeError("División entre cero")
    if isinstance(a, Tensor):
        return Tensor(a.shape, [x / b for x in a.data])
    return a / b


# ---------- funciones integradas ----------


def f_transpose(m):
    rows, cols = m.shape
    return Tensor(
        (cols, rows), [m.data[r * cols + c] for c in range(cols) for r in range(rows)]
    )


def f_trace(m):
    n = m.shape[0]
    return sum(m.data[i * n + i] for i in range(n))


def f_norm(v):
    return math.sqrt(sum(x * x for x in v.data))


def f_rows(m):
    return float(m.shape[0])


def f_cols(m):
    return float(m.shape[1])


def f_is_symmetric(m):
    n, cols = m.shape
    if n != cols:
        return 0.0
    for i in range(n):
        for j in range(i + 1, n):
            if abs(m.data[i * n + j] - m.data[j * n + i]) > EPS:
                return 0.0
    return 1.0


def _eliminate(matrix, rhs=None):
    n = len(matrix)
    det = 1.0
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(matrix[r][col]))
        if abs(matrix[pivot][col]) < EPS:
            return 0.0, matrix, rhs
        if pivot != col:
            matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
            if rhs is not None:
                rhs[col], rhs[pivot] = rhs[pivot], rhs[col]
            det = -det
        det *= matrix[col][col]
        for r in range(col + 1, n):
            factor = matrix[r][col] / matrix[col][col]
            if factor:
                for c in range(col, n):
                    matrix[r][c] -= factor * matrix[col][c]
                if rhs is not None:
                    rhs[r] -= factor * rhs[col]
    return det, matrix, rhs


def f_det(m):
    return _eliminate(m.rows_list())[0]


def f_solve(a, b):
    n = a.shape[0]
    det, u, rhs = _eliminate(a.rows_list(), list(b.data))
    if det == 0.0:
        raise AlgaRuntimeError("solve: la matriz es singular")
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        total = rhs[i] - sum(u[i][j] * x[j] for j in range(i + 1, n))
        x[i] = total / u[i][i]
    return Tensor((n,), x)


def fmt_num(x):
    if math.isfinite(x) and x == int(x) and abs(x) < 1e15:
        return str(int(x))
    return f"{x:.10g}"


def fmt_value(value, multiline=True):
    if isinstance(value, str):
        return value
    if not isinstance(value, Tensor):
        return fmt_num(value)
    if len(value.shape) == 1:
        return "[" + ", ".join(fmt_num(x) for x in value.data) + "]"
    rows = ["[" + ", ".join(fmt_num(x) for x in row) + "]" for row in value.rows_list()]
    if multiline:
        return "[" + ",\n ".join(rows) + "]"
    return "[" + ", ".join(rows) + "]"
