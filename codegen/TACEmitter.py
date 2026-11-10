import re

from semantic.type_rules import SCALAR, STRING

WORD = 8
BINARY_OPERATORS = ("+", "-", "*", "/", "<", ">", "==", "!=")
_NUMBER = re.compile(r"[+-]?[0-9]+(?:\.[0-9]+)?$")


def is_number(texto):
    return _NUMBER.match(texto) is not None


class Quad:
    __slots__ = ("op", "arg1", "arg2", "res")

    def __init__(self, op, arg1=None, arg2=None, res=None):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.res = res

    def tuple_like(self):
        return (self.op, self.arg1, self.arg2, self.res)

    def __eq__(self, other):
        return isinstance(other, Quad) and self.tuple_like() == other.tuple_like()

    def __hash__(self):
        return hash(self.tuple_like())

    def __repr__(self):
        return f"Quad{self.tuple_like()}"

    def __str__(self):
        op = self.op
        if op in BINARY_OPERATORS:
            return f"{self.res} = {self.arg1} {op} {self.arg2}"
        if op == "copy":
            return f"{self.res} = {self.arg1}"
        if op == "neg":
            return f"{self.res} = -{self.arg1}"
        if op == "label":
            return f"{self.res}:"
        if op == "goto":
            return f"goto {self.res}"
        if op == "ifFalse":
            return f"ifFalse {self.arg1} goto {self.res}"
        if op == "aload":
            return f"{self.res} = {self.arg1}[{self.arg2}]"
        if op == "astore":
            return f"{self.arg1}[{self.arg2}] = {self.res}"
        if op == "param":
            return f"param {self.arg1}"
        if op == "call":
            llamada = f"call {self.arg1}, {self.arg2}"
            return llamada if self.res is None else f"{self.res} = {llamada}"
        raise ValueError(f"fatal: unknown TAC operator: {op}")


class TACEmitter:
    def __init__(self):
        self._counter = 0
        self._tags = 0
        self._instructions = []
        self.types = {}
        self._storage = []
        self._temps = []

    def declare(self, name, type):
        self.types[name] = type
        self._storage.append((name, type))

    def new_temp(self, type=SCALAR):
        self._counter += 1
        name = f"t{self._counter}"
        self.types[name] = type
        if type.kind in ("vector", "matrix"):
            self._temps.append((name, type))
        return name

    def new_tag(self):
        self._tags += 1
        return f"L{self._tags}"

    def type_of(self, op):
        if is_number(op):
            return SCALAR
        if op.startswith('"'):
            return STRING
        return self.types[op]

    def _add(self, *args):
        self._instructions.append(Quad(*args))

    def emit(self, target, left, op, right):
        self._add(op, left, right, target)

    def emit_copy(self, target, src):
        self._add("copy", src, None, target)

    def emit_neg(self, target, src):
        self._add("neg", src, None, target)

    def emit_Tag(self, tag):
        self._add("label", None, None, tag)

    def emit_goto(self, tag):
        self._add("goto", None, None, tag)

    def emit_goto_false(self, condicion, etiqueta):
        self._add("ifFalse", condicion, None, etiqueta)

    def emit_load(self, target, base, move):
        self._add("aload", base, move, target)

    def emit_store(self, base, move, value):
        self._add("astore", base, move, value)

    def emit_param(self, op):
        self._add("param", op)

    def emit_call(self, fn, n_args, dest=None):
        self._add("call", fn, n_args, dest)

    def instructions(self):
        return list(self._instructions)

    @staticmethod
    def bytes_of(type):
        size = 1
        for dim in type.shape:
            size *= dim
        return size * WORD

    def code(self, header=True):
        lines = []
        if header:
            lines.append(".data")
            data = self._storage + self._temps
            width = max([len(f"{n} : {t}") for n, t in data] + [0])
            for name, type in data:
                decl = f"{name} : {type}"
                lines.append(f"    {decl.ljust(width)}  ; {self.bytes_of(type)} bytes")
            lines.append(".code")
        for q in self._instructions:
            lines.append(str(q) if q.op == "label" else f"    {q}")
        return "\n".join(lines)
