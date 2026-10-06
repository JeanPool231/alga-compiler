import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
from scripts import derivations as glc


class GrammarDocumentationTests(unittest.TestCase):
    def test_thirty_proposed_examples(self):
        groups = json.loads((ROOT / 'docs/ejemplos_informe.json').read_text())
        for group, examples in groups.items():
            self.assertEqual(len(examples), 5)
            for source in examples:
                with self.subTest(group=group, source=source):
                    tokens, tree = glc.parse(source)
                    self.assertEqual(glc.derive(tree)[-1][1], [t[0] for t in tokens])

    def test_leftmost_documents_are_current(self):
        for path, text in glc.documents():
            self.assertEqual(path.read_text(), text)

    def test_invalid_syntax(self):
        for source in ['scalar k', 'print();', 'vector v[2] = [];',
                       'while 1 > 0 {}', 'if (1 < 2 < 3) {}', '1; @']:
            with self.subTest(source=source), self.assertRaises(ValueError):
                glc.parse(source)

    def test_nested_conditionals_parse(self):
        glc.parse('if (1 > 0) { if (2 > 1) {} else {} } else {}')


    def test_numerical_methods_parse(self):
        for path in sorted((ROOT / 'examples/05_metodos_numericos').glob('*.txt')):
            with self.subTest(path=path.name):
                glc.parse(path.read_text())

    def test_references_and_nested_loops(self):
        glc.parse('for (i = 0; i < 2; i = i + 1) { while (j < 2) { A[i][j] = v[j]; } }')
        for source in ['A[0][0][0];', 'for (;;) {}', 'while (1 > 0) x = 1;']:
            with self.subTest(source=source), self.assertRaises(ValueError):
                glc.parse(source)
