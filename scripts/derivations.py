"""Construye y verifica derivaciones de la GLC; no reemplaza el parser ANTLR.

Cada paso sustituye exactamente el no terminal más a la izquierda. El lector
por memoización solo se usa para documentación y no es el compilador entregado.
"""
import argparse
from functools import lru_cache
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
GRAMMAR = json.loads((ROOT / 'docs/glc.json').read_text(encoding='utf-8'))
KEYWORDS = {'matrix', 'vector', 'scalar', 'if', 'else', 'while', 'for', 'transpose', 'det', 'trace'}
LEXEME = re.compile(r'\s+|"(?:\\["\\nrt]|[^"\\\r\n])*"|[a-zA-Z_][a-zA-Z0-9_]*|[0-9]+(?:\.[0-9]+)?|==|!=|[=+*/<>()[\]{},;\-]')


def tokenize(source):
    tokens = []
    position = 0
    while position < len(source):
        match = LEXEME.match(source, position)
        if match is None:
            raise ValueError(f'Carácter inválido en {position}: {source[position]!r}')
        value = match.group()
        position = match.end()
        if value.isspace():
            continue
        if value[0] == '"':
            symbol = 'string'
        elif value[0].isdigit():
            symbol = 'num'
        elif (value[0].isalpha() or value[0] == '_') and value not in KEYWORDS:
            symbol = 'id'
        else:
            symbol = value
        tokens.append((symbol, value))
    return tokens


def parse(source, start='S'):
    tokens = tokenize(source)

    @lru_cache(None)
    def read(symbol, pos):
        if symbol not in GRAMMAR:
            if pos < len(tokens) and tokens[pos][0] == symbol:
                return ((pos + 1, (symbol, None)),)
            return ()
        results = []
        for production in GRAMMAR[symbol]:
            states = [(pos, ())]
            for child in production:
                states = [(end, children + (tree,))
                          for current, children in states
                          for end, tree in read(child, current)]
            results.extend((end, (symbol, children)) for end, children in states)
        return tuple(results)

    trees = [tree for end, tree in read(start, 0) if end == len(tokens)]
    if len(trees) != 1:
        raise ValueError(f'Se esperó un árbol para {source!r}; se encontraron {len(trees)}')
    return tokens, trees[0]


def derive(tree):
    form = [tree[0]]
    steps = [('Inicio', form.copy())]

    def expand(node):
        name, children = node
        if children is None:
            return
        pos = next(i for i, symbol in enumerate(form) if symbol in GRAMMAR)
        assert form[pos] == name
        rhs = [child[0] for child in children]
        assert rhs in GRAMMAR[name]
        form[pos:pos + 1] = rhs
        steps.append((f'{name} → ' + (' '.join(rhs) or 'ε'), form.copy()))
        for child in children:
            expand(child)

    expand(tree)
    assert not any(symbol in GRAMMAR for symbol in form)
    return steps


def documents():
    examples = json.loads((ROOT / 'docs/ejemplos_informe.json').read_text(encoding='utf-8'))
    # Cuatro por construcción; incluyen inicialización, signos, llamadas y else.
    chosen = {'declaraciones': [0, 1, 3, 4], 'asignaciones': [0, 2, 3, 4],
              'expresiones': [0, 1, 2, 4], 'selectivas': [0, 2, 3, 4], 'iterativas_while': [0, 1, 3, 4], 'iterativas_for': [0, 1, 2, 3]}
    starts = {'declaraciones': 'D', 'asignaciones': 'A', 'expresiones': 'exprstmt', 'selectivas': 'I', 'iterativas_while': 'W', 'iterativas_for': 'W'}
    for index, (name, selection) in enumerate(chosen.items(), 1):
        parts = [f'# {name.capitalize()}: cuatro derivaciones más a la izquierda\n',
                 'GLC ampliada propuesta para el informe (ver `../03_gramatica.md`). '
                 '`id`, `num` y `string` son terminales; sus lexemas se indican debajo. '
                 'Cada fila sustituye un solo no terminal, siempre el situado más a la izquierda. '
                 'La derivación parte del no terminal de la construcción; desde S se alcanza con '
                 '`S ⇒ L ⇒ stmt L ⇒ ' + starts[name] + ' L` y al final `L ⇒ ε`.\n']
        for number, selection_index in enumerate(selection, 1):
            source = examples[name][selection_index]
            tokens, tree = parse(source, starts[name])
            steps = derive(tree)
            assert steps[-1][1] == [t[0] for t in tokens]
            parts.extend([f'## Ejemplo {number}\n', f'```alga\n{source}\n```\n',
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
