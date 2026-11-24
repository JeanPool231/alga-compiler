import argparse
import json
import os
import sys

from antlr4 import CommonTokenStream, FileStream, InputStream, Token

from codegen.code_gen_visitor import CodeGenVisitor
from gen.AlgaLexer import AlgaLexer
from gen.AlgaParser import AlgaParser
from semantic.errors import DiagnosticListener
from semantic.semantic_visitor import SemanticVisitor


def analizar(input_stream, phase="semantic", base_dir=None):
    return _pipeline(input_stream, phase, base_dir)[0]


def compilar(input_stream, base_dir=None):
    return _pipeline(input_stream, "tac", base_dir)


def _pipeline(input_stream, phase, base_dir=None):
    lexer = AlgaLexer(input_stream)
    lexical = DiagnosticListener("léxico")
    lexer.removeErrorListeners()
    lexer.addErrorListener(lexical)
    stream = CommonTokenStream(lexer)
    stream.fill()

    tokens = []
    for token in stream.tokens:
        if token.type != Token.EOF:
            tokens.append(
                {
                    "token": lexer.symbolicNames[token.type],
                    "lexema": token.text,
                    "linea": token.line,
                    "columna": token.column + 1,
                }
            )
    result = {"tokens": tokens, "errors": lexical.errors, "tree": None}
    if lexical.errors or phase == "lex":
        return result, None

    parser = AlgaParser(stream)
    syntax = DiagnosticListener("sintáctico")
    parser.removeErrorListeners()
    parser.addErrorListener(syntax)
    tree = parser.s()  # S es la regla inicial del informe.
    result["tree"] = tree.toStringTree(recog=parser)
    result["errors"] = syntax.errors
    if parser.getNumberOfSyntaxErrors() > 0 or phase == "parse":
        return result, None

    visitor = SemanticVisitor(base_dir=base_dir)
    visitor.visit(tree)
    for error in visitor.errors:
        result["errors"].append(str(error))
    if result["errors"] or phase != "tac":
        return result, None

    generador = CodeGenVisitor(visitor)
    generador.visit(tree)
    result["tac"] = generador.tac.code()
    return result, generador.tac


def analyze(source, phase="semantic"):
    return analizar(InputStream(source), phase)


def mostrar_tokens(tokens):
    for token in tokens:
        print(
            f"{token['linea']}:{token['columna']} {token['token']} {token['lexema']!r}"
        )


def main(argv=None):
    cli = argparse.ArgumentParser(
        description="Alga"
    )
    cli.add_argument("file")
    cli.add_argument(
        "--phase", choices=["lex", "parse", "semantic", "tac"], default="semantic"
    )
    cli.add_argument("--json", action="store_true")
    cli.add_argument(
        "--out",
        metavar="ARCHIVO",
        help="con --phase tac: guarda también el TAC en ARCHIVO",
    )
    args = cli.parse_args(argv)

    try:
        input_stream = FileStream(args.file, encoding="utf-8")
    except (OSError, UnicodeError) as error:
        print(f"No se pudo leer {args.file}: {error}", file=sys.stderr)
        return 2
    base_dir = os.path.dirname(os.path.abspath(args.file)) 
    result = analizar(input_stream, args.phase, base_dir=base_dir)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if args.phase == "lex":
            mostrar_tokens(result["tokens"])
        if args.phase == "parse" and not result["errors"]:
            print(result["tree"])
        for error in result["errors"]:
            print(error, file=sys.stderr)
        if not result["errors"]:
            if args.phase == "tac":
                print(result["tac"])
                if args.out:
                    try:
                        with open(args.out, "w", encoding="utf-8") as salida:
                            salida.write(result["tac"] + "\n")
                    except OSError as error:
                        print(
                            f"No se pudo escribir {args.out}: {error}", file=sys.stderr
                        )
                        return 2
            else:
                print(f"OK: fase {args.phase}; análisis estático completado")
    if result["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
