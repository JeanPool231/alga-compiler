from .errors import SemanticError


class Symbol:
    def __init__(self, name, type_, scope, line):
        self.name = name
        self.type_ = type_
        self.scope = scope
        self.line = line


class SymbolTable:
    def __init__(self):
        self._table = {'global': {}}
        self._scope_stack = ['global']
        self._next_scope = 0

    @property
    def current_scope(self):
        return self._scope_stack[-1]

    def enter_scope(self):
        # Dos bloques en la misma línea siguen siendo ámbitos diferentes.
        self._next_scope += 1
        name = f'bloque_{self._next_scope}'
        self._scope_stack.append(name)
        self._table[name] = {}

    def exit_scope(self):
        self._scope_stack.pop()

    def declare(self, name, type_, line, column):
        scope = self.current_scope
        if name in self._table[scope]:
            raise SemanticError(f'Variable {name} ya declarada en este ámbito', line, column)
        symbol = Symbol(name, type_, scope, line)
        self._table[scope][name] = symbol
        return symbol

    def lookup(self, name):
        for scope in reversed(self._scope_stack):
            if name in self._table[scope]:
                return self._table[scope][name]
        return None
