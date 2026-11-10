import argparse
import json
import sys

from antlr4 import CommonTokenStream, FileStream, InputStream, Token

from codegen.code_gen_visitor import CodeGenVisitor
from gen.AlgaLexer import AlgaLexer
from gen.AlgaParser import AlgaParser
from semantic.errors import DiagnosticListener
from semantic.semantic_visitor import SemanticVisitor


def analizar(input_stream, phase="semantic"):
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
        return result

    parser = AlgaParser(stream)
    syntax = DiagnosticListener("sintáctico")
    parser.removeErrorListeners()
    parser.addErrorListener(syntax)
    tree = parser.s()  # S es la regla inicial del informe.
    result["tree"] = tree.toStringTree(recog=parser)
    result["errors"] = syntax.errors
    if parser.getNumberOfSyntaxErrors() > 0 or phase == "parse":
        return result

    visitor = SemanticVisitor()
    visitor.visit(tree)
    for error in visitor.errors:
        result["errors"].append(str(error))
    if result["errors"] or phase != "tac":
        return result

    generador = CodeGenVisitor(visitor)
    generador.visit(tree)
    result["tac"] = generador.tac.code()
    return result


def analyze(source, phase="semantic"):
    # InputStream permite probar cadenas
    return analizar(InputStream(source), phase)


def mostrar_tokens(tokens):
    for token in tokens:
        print(
            f"{token['linea']}:{token['columna']} {token['token']} {token['lexema']!r}"
        )


def main(argv=None):
    # Opciones adicionales para conservar las fases, JSON y códigos de salida.
    cli = argparse.ArgumentParser(
        description="Alga: análisis estático y código intermedio"
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
    result = analizar(input_stream, args.phase)

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
