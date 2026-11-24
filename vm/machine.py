import re

from codegen.TACEmitter import BINARY_OPERATORS, WORD, is_number

from .values import (
    AlgaRuntimeError,
    Tensor,
    add,
    decode_string,
    div,
    f_cols,
    f_det,
    f_is_symmetric,
    f_norm,
    f_rows,
    f_solve,
    f_trace,
    f_transpose,
    fmt_value,
    mul,
    sub,
)

_TEMP_OR_LABEL = re.compile(r"[tL][0-9]+$")

_COMPARE = {
    "<": lambda a, b: 1.0 if a < b else 0.0,
    ">": lambda a, b: 1.0 if a > b else 0.0,
    "==": lambda a, b: 1.0 if a == b else 0.0,
    "!=": lambda a, b: 1.0 if a != b else 0.0,
}
_ARITH = {"+": add, "-": sub, "*": mul, "/": div}

_BUILTINS = {
    "transpose": f_transpose,
    "trace": f_trace,
    "norm": f_norm,
    "rows": f_rows,
    "cols": f_cols,
    "isSymmetric": f_is_symmetric,
    "det": f_det,
    "solve": f_solve,
}


class VM:
    def __init__(self, tac, output=None, max_steps=5_000_000, max_cells=1_000_000):
        self.output = output or print
        self.max_steps = max_steps
        self.max_cells = max_cells
        self.steps = 0
        self._types = tac.types
        self._datasets = getattr(tac, "datasets", {})
        self._code = []
        self._labels = {}
        self.mem = {}
        self._load(tac)

    def _load(self, tac):
        mem = self.mem
        cells = 0
        for type_ in self._types.values():
            if type_.kind in ("vector", "matrix"):
                size = 1
                for dim in type_.shape:
                    size *= dim
                cells += size
        if cells > self.max_cells:
            raise AlgaRuntimeError(
                f"Memoria excedida: el programa reserva {cells} celdas (máximo {self.max_cells})"
            )
        for name, type_ in self._types.items():
            if type_.kind in ("vector", "matrix"):
                mem[name] = Tensor(type_.shape)
            else:
                mem[name] = 0.0  # def is 0

        for quad in tac.instructions():
            if quad.op == "label":
                self._labels[quad.res] = len(self._code)
            for operand in (quad.arg1, quad.arg2):
                if isinstance(operand, str):
                    if is_number(operand):
                        mem[operand] = float(operand)
                    elif operand.startswith('"'):
                        mem[operand] = decode_string(operand)
            if quad.op == "call":
                quad.arg2 = int(quad.arg2)
            if quad.op == "astore" and is_number(quad.res):
                mem[quad.res] = float(quad.res)
            self._code.append(quad)

    def run(self):
        code, mem, labels = self._code, self.mem, self._labels
        params = []
        pc, n = 0, len(code)
        steps, limit = 0, self.max_steps
        quad = None
        try:
            while pc < n:
                quad = code[pc]
                pc += 1
                steps += 1
                if steps > limit:
                    raise AlgaRuntimeError(
                        f"Se superó el límite de {limit} instrucciones (¿bucle infinito?)"
                    )
                op = quad.op
                if op in BINARY_OPERATORS:
                    a, b = mem[quad.arg1], mem[quad.arg2]
                    if op in _COMPARE:
                        mem[quad.res] = _COMPARE[op](a, b)
                    else:
                        mem[quad.res] = _ARITH[op](a, b)
                elif op == "aload":
                    base = mem[quad.arg1]
                    mem[quad.res] = base.data[
                        self._index(quad.arg1, base, mem[quad.arg2])
                    ]
                elif op == "astore":
                    base = mem[quad.arg1]
                    base.data[self._index(quad.arg1, base, mem[quad.arg2])] = mem[
                        quad.res
                    ]
                elif op == "copy":
                    value = mem[quad.arg1]
                    mem[quad.res] = value.copy() if isinstance(value, Tensor) else value
                elif op == "ifFalse":
                    if mem[quad.arg1] == 0:
                        pc = labels[quad.res]
                elif op == "goto":
                    pc = labels[quad.res]
                elif op == "neg":
                    value = mem[quad.arg1]
                    mem[quad.res] = (
                        Tensor(value.shape, [-x for x in value.data])
                        if isinstance(value, Tensor)
                        else -value
                    )
                elif op == "param":
                    params.append(mem[quad.arg1])
                elif op == "call":
                    args = params[len(params) - quad.arg2 :]
                    del params[len(params) - quad.arg2 :]
                    result = self._call(quad.arg1, args)
                    if quad.res is not None:
                        mem[quad.res] = result
        except AlgaRuntimeError as error:
            if error.pos is None and quad is not None:
                error.pos = quad.pos
            raise
        finally:
            self.steps = steps

    def _index(self, name, base, offset):
        if offset % WORD != 0:
            raise AlgaRuntimeError(f"El índice de {name} debe ser entero")
        i = int(offset) // WORD
        if i < 0 or i >= len(base.data):
            raise AlgaRuntimeError(
                f"Índice fuera de rango en {name} (posición {i}; tamaño {len(base.data)})"
            )
        return i

    def _call(self, name, args):
        if name == "print":
            for value in args:
                self.output(fmt_value(value))
            return None
        
        if name == "csv":
            path, sep = args[0], args[1]
            dataset = self._datasets[(path, sep)]
            return Tensor(dataset.type_.shape, list(dataset.data))
        
        return _BUILTINS[name](*args)

    def variables(self):
        return {
            name: value
            for name, value in self.mem.items()
            if name in self._types and not _TEMP_OR_LABEL.match(name)
        }
