from antlr4.error.ErrorListener import ErrorListener


class SemanticError(Exception):
    def __init__(self, message, line, column):
        super().__init__(f'semántico:{line}:{column}: {message}')
        self.line = line
        self.column = column


# Extensión para conservar los diagnósticos de ANTLR y la salida JSON.
class DiagnosticListener(ErrorListener):
    def __init__(self, phase):
        super().__init__()
        self.phase = phase
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append(f'{self.phase}:{line}:{column + 1}: {msg}')
