import re

from .errors import SemanticError

_RESERVADOS = re.compile(r"[tL][0-9]+$")


class Symbol:
    def __init__(self, name, type_, scope, line, unique=None):
        self.name = name
        self.type_ = type_
        self.scope = scope
        self.line = line
        self.unique = unique or name


class SymbolTable:
    def __init__(self):
        self._table = {"global": {}}
        self._scope_stack = ["global"]
        self._next_scope = 0
        self._uses = {}
        self._used_unique = set()

    @property
    def current_scope(self):
        return self._scope_stack[-1]

    def enter_scope(self):
        # Dos bloques en la misma línea siguen siendo ámbitos diferentes.
        self._next_scope += 1
        name = f"bloque_{self._next_scope}"
        self._scope_stack.append(name)
        self._table[name] = {}

    def exit_scope(self):
        self._scope_stack.pop()

    def declare(self, name, type_, line, column):
        scope = self.current_scope
        if name in self._table[scope]:
            raise SemanticError(
                f"Variable {name} ya declarada en este ámbito", line, column
            )
        symbol = Symbol(name, type_, scope, line, self._unique_name(name))
        self._table[scope][name] = symbol
        return symbol

    def lookup(self, name):
        for scope in reversed(self._scope_stack):
            if name in self._table[scope]:
                return self._table[scope][name]
        return None

    def _unique_name(self, name):
        count = self._uses.get(name, 0)
        self._uses[name] = count + 1
        candidate = name if count == 0 else f"{name}_{count}"
        while candidate in self._used_unique or _RESERVADOS.match(candidate):
            count += 1
            candidate = f"{name}_{count}"
        self._used_unique.add(candidate)
        return candidate
