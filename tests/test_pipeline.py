"""Pruebas de integración reales: requieren runtime y generación de ANTLR."""
import json
from pathlib import Path
import subprocess
import sys
import unittest
from alga.driver import analyze

ROOT = Path(__file__).resolve().parents[1]


class PipelineTests(unittest.TestCase):
    def test_manifest(self):
        cases = json.loads((ROOT / 'examples/casos.json').read_text(encoding='utf-8'))
        for case in cases:
            with self.subTest(file=case['archivo']):
                source = (ROOT / case['archivo']).read_text(encoding='utf-8')
                result = analyze(source, case['fase'])
                if case['error'] is None:
                    self.assertEqual(result['errors'], [])
                else:
                    self.assertTrue(any(case['error'] in e for e in result['errors']), result)
                    self.assertRegex(result['errors'][0], r':\d+:\d+:')
                    if case['fase'] != 'lex':
                        previous = 'lex' if case['fase'] == 'parse' else 'parse'
                        self.assertEqual(analyze(source, previous)['errors'], [])

    def test_keyword_longest_match_and_sign(self):
        result = analyze('scalar scalar1 = -3.5; if (scalar1 != 0) {}', 'lex')
        self.assertEqual(result['errors'], [])
        self.assertEqual([t['token'] for t in result['tokens'][:6]],
                         ['TK_SCALAR', 'ID', 'TK_ASSIGN', 'TK_MINUS', 'NUM', 'TK_SEMICOLON'])
        self.assertIn('TK_NEQ', [t['token'] for t in result['tokens']])

    def test_source_locations(self):
        tokens = analyze('scalar k;\n  k = 2;', 'lex')['tokens']
        self.assertEqual((tokens[3]['linea'], tokens[3]['columna']), (2, 3))

    def test_lex_error_stops_parser(self):
        result = analyze('scalar k = @;')
        self.assertIsNone(result['tree'])
        self.assertTrue(all(e.startswith('léxico:') for e in result['errors']))

    def test_parse_error_stops_semantics(self):
        result = analyze('k = ;')
        self.assertTrue(result['errors'])
        self.assertTrue(all(e.startswith('sintáctico:') for e in result['errors']))

    def test_precedence(self):
        source = 'matrix A[2][3]; matrix B[3][4]; matrix C[3][4]; A * B + C;'
        self.assertTrue(analyze(source)['errors'])  # (A * B) + C: 2x4 + 3x4
        self.assertEqual(analyze(source.replace('A * B + C', 'A * (B + C)'))['errors'], [])

    def test_left_associative_product(self):
        # Izquierda: (A / k) * B es válido. Derecha: A / (k * B) no lo sería.
        self.assertEqual(analyze('matrix A[2][3]; scalar k; matrix B[3][4]; A / k * B;')['errors'], [])
        self.assertEqual(analyze('vector v[2]; v * 2 / 3;')['errors'], [])
        self.assertTrue(analyze('vector v[2]; 2 / v * 3;')['errors'])

    def test_scope_and_shadowing(self):
        self.assertEqual(analyze('scalar k; if (1 > 0) { vector k[2]; k = [1,2]; } k = 2;')['errors'], [])
        self.assertTrue(analyze('if (1 > 0) { scalar k; } else { k = 1; }')['errors'])

    def test_self_initializer_is_undeclared(self):
        self.assertTrue(analyze('scalar k = k;')['errors'])

    def test_demo(self):
        source = (ROOT / 'examples/01_validos/05_demo.alga').read_text()
        self.assertEqual(analyze(source)['errors'], [])

    def test_cli_exit_codes(self):
        for filename, expected in [('examples/01_validos/05_demo.alga', 0),
                                   ('examples/04_errores_semanticos/dimension_vector.alga', 1),
                                   ('examples/no_existe.alga', 2)]:
            result = subprocess.run([sys.executable, '-m', 'alga.driver', filename],
                                    cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, expected, result.stderr)


    def test_loops_and_indexed_references(self):
        source = 'scalar i; vector v[3] = [0,0,0]; for (i = 0; i < 3; i = i + 1) { v[i] = i; }'
        self.assertEqual(analyze(source)['errors'], [])
        self.assertEqual(analyze('while (1 < 2) {}')['errors'], [])  # No ejecuta el bucle.

    def test_loop_scope_and_header(self):
        self.assertTrue(analyze('while (1 < 2) { scalar t; } t = 0;')['errors'])
        self.assertTrue(analyze('scalar i; for (i = 0; i < 2; i = t) { scalar t = 1; }')['errors'])
        self.assertTrue(analyze('scalar i; for (i = 0; i < 2; i = i + 1) { vector i[2]; i = 3; }')['errors'])

    def test_indexed_reads_writes_and_dynamic_limit(self):
        self.assertEqual(analyze('matrix A[2][2]; scalar x = A[0][1]; A[1][0] = x;')['errors'], [])
        self.assertTrue(analyze('vector v[2]; scalar x = v[2];')['errors'])
        self.assertTrue(analyze('matrix A[2][2]; scalar x = A[0];')['errors'])
        # Se documenta que el Hito 1 no prueba valores de índices dinámicos.
        self.assertEqual(analyze('vector v[2]; scalar i = 0.5; v[i];')['errors'], [])
