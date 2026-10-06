"""Derivaciones de la GLC a partir del árbol de ANTLR, sin un segundo parser."""
import argparse
import json
from pathlib import Path
import sys

# Permite ejecutar python3 scripts/derivations.py desde la raíz o por ruta absoluta.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from antlr4 import CommonTokenStream, InputStream, Token, ParserRuleContext
from gen.AlgaLexer import AlgaLexer
from gen.AlgaParser import AlgaParser
from semantic.errors import DiagnosticListener

GRAMMAR = json.loads((ROOT / 'docs/glc.json').read_text(encoding='utf-8'))
RULES = {
    'S': 's', 'L': 'l', 'stmt': 'stmt', 'D': 'd', 'J': 'j',
    'A': 'a', 'As': 'asig', 'Ref': 'ref', 'U': 'u', 'U1': 'u1',
    'exprstmt': 'exprstmt', 'E': 'e', 'E′': 'eprima', 'T': 't',
    'T′': 'tprima', 'F': 'f', 'H': 'h', 'K': 'k', 'V': 'v',
    'N′': 'nprima', 'N': 'n', 'Z': 'z', 'M': 'm', 'M′': 'mprima',
    'I': 'i', 'O': 'o', 'B': 'b', 'C': 'c', 'Q': 'q', 'R': 'r', 'W': 'w',
}
NAMES = {}
for symbol, rule in RULES.items():
    NAMES[rule] = symbol


def terminal(token):
    if token.type == AlgaLexer.ID:
        return 'id'
    if token.type == AlgaLexer.NUM:
        return 'num'
    if token.type == AlgaLexer.STRING:
        return 'string'
    return token.text


def parse(source, start='S'):
    lexer = AlgaLexer(InputStream(source))
    lexical = DiagnosticListener('léxico')
    lexer.removeErrorListeners()
    lexer.addErrorListener(lexical)
    stream = CommonTokenStream(lexer)
    stream.fill()
    if lexical.errors:
        raise ValueError('\n'.join(lexical.errors))

    parser = AlgaParser(stream)
    syntax = DiagnosticListener('sintáctico')
    parser.removeErrorListeners()
    parser.addErrorListener(syntax)
    # Las derivaciones pueden empezar en S o en la regla de una construcción.
    tree = getattr(parser, RULES[start])()
    if syntax.errors:
        raise ValueError('\n'.join(syntax.errors))
    if stream.LA(1) != Token.EOF:
        raise ValueError('Quedan tokens sin reconocer')

    tokens = []
    for token in stream.tokens:
        if token.type != Token.EOF:
            tokens.append((terminal(token), token.text))
    return tokens, grammar_tree(tree, parser)


def grammar_tree(node, parser):
    if not isinstance(node, ParserRuleContext):
        return (terminal(node.getSymbol()), None)
    name = NAMES[parser.ruleNames[node.getRuleIndex()]]
    children = []
    for child in node.getChildren():
        if not isinstance(child, ParserRuleContext) and child.getSymbol().type == Token.EOF:
            continue
        children.append(grammar_tree(child, parser))
    return (name, children)


def derive(tree):
    form = [tree[0]]
    steps = [('Inicio', form.copy())]

    def expand(node):
        name, children = node
        if children is None:
            return
        position = 0
        while position < len(form) and form[position] not in GRAMMAR:
            position += 1
        if position == len(form) or form[position] != name:
            raise ValueError('Debe sustituirse el no terminal más a la izquierda')
        production = []
        for child in children:
            production.append(child[0])
        if production not in GRAMMAR[name]:
            raise ValueError(f'Producción fuera de la GLC: {name} → {production}')
        form[position:position + 1] = production
        rule = name + ' → ' + (' '.join(production) or 'ε')
        steps.append((rule, form.copy()))
        for child in children:
            expand(child)

    expand(tree)
    for symbol in form:
        if symbol in GRAMMAR:
            raise ValueError('La derivación debe terminar en una cadena de terminales')
    return steps


def documents():
    examples = json.loads((ROOT / 'docs/ejemplos_informe.json').read_text(encoding='utf-8'))
    # Cuatro por construcción; incluyen inicialización, signos, llamadas y else.
    chosen = {'declaraciones': [0, 1, 3, 4], 'asignaciones': [0, 2, 3, 4],
              'expresiones': [0, 1, 2, 4], 'selectivas': [0, 2, 3, 4], 'iterativas_while': [0, 1, 3, 4], 'iterativas_for': [0, 1, 2, 3]}
    starts = {'declaraciones': 'D', 'asignaciones': 'A', 'expresiones': 'exprstmt', 'selectivas': 'I', 'iterativas_while': 'W', 'iterativas_for': 'W'}
    for index, (name, selection) in enumerate(chosen.items(), 1):
        parts = [f'# {name.capitalize()}: cuatro derivaciones más a la izquierda\n',
                 'GLC del informe (ver [correspondencia con ANTLR](../03_gramatica.md)). '
                 '`id`, `num` y `string` son terminales; sus lexemas se indican debajo. '
                 'Cada fila sustituye un solo no terminal, siempre el situado más a la izquierda. '
                 'La derivación parte del no terminal de la construcción; desde S se alcanza con '
                 '`S ⇒ L ⇒ stmt L ⇒ ' + starts[name] + ' L` y al final `L ⇒ ε`.\n']
        for number, selection_index in enumerate(selection, 1):
            source = examples[name][selection_index]
            tokens, tree = parse(source, starts[name])
            steps = derive(tree)
            if steps[-1][1] != [t[0] for t in tokens]:
                raise ValueError('La derivación no coincide con los tokens de entrada')
            parts.extend([f'## Ejemplo {number}\n', f'```text\n{source}\n```\n',
                          'Lexemas en orden: `' + ' '.join(f'{s}={v}' for s, v in tokens if s in {'id','num','string'}) + '`\n',
                          '```text\n' + '\n'.join(f'{i:02}. {" ".join(form) or "ε"}    [{rule}]' for i,(rule,form) in enumerate(steps)) + '\n```\n'])
        yield ROOT / f'docs/04_derivaciones/{index:02}_{name}.md', '\n'.join(parts)


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument('--check', action='store_true')
    args = cli.parse_args()
    for path, contents in documents():
        if args.check:
            if not path.exists() or path.read_text(encoding='utf-8') != contents:
                raise SystemExit(f'Derivaciones desactualizadas: {path}')
        else:
            path.write_text(contents, encoding='utf-8')
    print('24 derivaciones verificadas: producciones, sustitución izquierda y cadena final.')


if __name__ == '__main__':
    main()
