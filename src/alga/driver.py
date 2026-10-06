"""CLI: detiene el pipeline si la fase previa contiene errores."""
import argparse
import json
import sys
from pathlib import Path
from antlr4 import InputStream, CommonTokenStream, Token
from antlr4.error.ErrorListener import ErrorListener
from .generated.AlgaLexer import AlgaLexer
from .generated.AlgaParser import AlgaParser
from .semantic import SemanticAnalyzer


class Diagnostics(ErrorListener):
    def __init__(self, phase):
        super().__init__()
        self.phase = phase
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append(f'{self.phase}:{line}:{column + 1}: {msg}')


def analyze(source, phase='semantic'):
    lexer = AlgaLexer(InputStream(source))
    lexical = Diagnostics('léxico')
    lexer.removeErrorListeners()
    lexer.addErrorListener(lexical)
    tokens = CommonTokenStream(lexer)
    tokens.fill()
    result = {'tokens': [
        {'token': lexer.symbolicNames[t.type], 'lexema': t.text,
         'linea': t.line, 'columna': t.column + 1}
        for t in tokens.tokens if t.type != Token.EOF
    ], 'errors': lexical.errors, 'tree': None}
    if lexical.errors or phase == 'lex':
        return result
    parser = AlgaParser(tokens)
    syntax = Diagnostics('sintáctico')
    parser.removeErrorListeners()
    parser.addErrorListener(syntax)
    tree = parser.program()
    result['errors'] = syntax.errors
    result['tree'] = tree.toStringTree(recog=parser)
    if not syntax.errors and phase == 'semantic':
        result['errors'] = SemanticAnalyzer().visit(tree)
    return result


def main(argv=None):
    cli = argparse.ArgumentParser(description='Alga: análisis estático del Hito 1')
    cli.add_argument('file', type=Path)
    cli.add_argument('--phase', choices=['lex', 'parse', 'semantic'], default='semantic')
    cli.add_argument('--json', action='store_true')
    args = cli.parse_args(argv)
    try:
        result = analyze(args.file.read_text(encoding='utf-8'), args.phase)
    except (OSError, UnicodeError) as exc:
        print(f'No se pudo leer {args.file}: {exc}', file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if args.phase == 'lex':
            for token in result['tokens']:
                print(f"{token['linea']}:{token['columna']} {token['token']} {token['lexema']!r}")
        if args.phase == 'parse' and not result['errors']:
            print(result['tree'])
        for diagnostic in result['errors']:
            print(diagnostic, file=sys.stderr)
        if not result['errors']:
            print(f'OK: fase {args.phase}; análisis estático completado')
    return 1 if result['errors'] else 0


if __name__ == '__main__':
    sys.exit(main())
