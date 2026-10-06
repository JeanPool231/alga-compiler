"""Regresiones de la migración y correspondencia con el informe entregado."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

from gen.AlgaLexer import AlgaLexer
from main import analyze
from scripts import derivations

ROOT = Path(__file__).resolve().parents[1]


def report_paragraphs():
    with zipfile.ZipFile(ROOT / 'Grupo 2 Trabajo Parcial Compiladores.docx') as document:
        root = ET.fromstring(document.read('word/document.xml'))
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    paragraphs = []
    for paragraph in root.findall('.//w:p', ns):
        text = ''
        for part in paragraph.findall('.//w:t', ns):
            text += part.text or ''
        paragraphs.append(text.strip())
    return paragraphs


class ReportConsistencyTests(unittest.TestCase):
    def test_docx_productions_match_documented_grammar(self):
        productions = {}
        for line in report_paragraphs():
            match = re.fullmatch(r'([A-Za-z][A-Za-z0-9′]*)\s*→\s*(.+)', line)
            if match:
                name, body = match.groups()
                productions[name] = []
                for alternative in body.split('|'):
                    if alternative.strip() == 'ε':
                        productions[name].append([])
                    else:
                        productions[name].append(alternative.split())
        self.assertEqual(productions, derivations.GRAMMAR)

    def test_antlr_productions_match_documented_grammar(self):
        source = (ROOT / 'grammar/AlgaParser.g4').read_text()
        source = re.sub(r'//[^\n]*', '', source)
        names = dict(derivations.NAMES)
        names.update({'ID': 'id', 'NUM': 'num', 'STRING': 'string'})
        for index, literal in enumerate(AlgaLexer.literalNames):
            if literal.startswith("'"):
                names[AlgaLexer.symbolicNames[index]] = literal[1:-1]
        productions = {}
        for rule, body in re.findall(r'\b([a-z][a-z0-9]*)\s*:\s*([^;]*);', source):
            alternatives = []
            for alternative in body.split('|'):
                symbols = []
                for token in alternative.split():
                    if token != 'EOF':
                        symbols.append(names[token])
                alternatives.append(symbols)
            productions[names[rule]] = alternatives
        self.assertEqual(productions, derivations.GRAMMAR)

    def test_docx_has_five_examples_per_construction_and_they_parse(self):
        groups = {}
        current = None
        source = None
        for line in report_paragraphs():
            if re.match(r'4\.\s*Analizador', line):
                if source is not None:
                    groups[current].append(source)
                break
            if re.fullmatch(r'[A-E]\.\s+.+', line):
                if source is not None:
                    groups[current].append(source)
                current = line
                groups[current] = []
                source = None
            elif current is not None:
                example = re.match(r'[1-5]\.\s*(.*)', line)
                if example:
                    if source is not None:
                        groups[current].append(source)
                    source = example.group(1)
                elif source is not None and line:
                    source += ' ' + line
        self.assertEqual(len(groups), 5)
        for group, examples in groups.items():
            self.assertEqual(len(examples), 5, group)
            for source in examples:
                with self.subTest(group=group, source=source):
                    self.assertEqual(analyze(source, 'parse')['errors'], [])
                    tokens, tree = derivations.parse(source)
                    self.assertEqual(derivations.derive(tree)[-1][1], [t[0] for t in tokens])


class MigrationTests(unittest.TestCase):
    def test_all_input_files_are_covered(self):
        cases = json.loads((ROOT / 'examples/casos.json').read_text())
        manifest = set()
        for case in cases:
            path = ROOT / case['archivo']
            self.assertEqual(path.suffix, '.txt')
            self.assertTrue(path.is_file(), case['archivo'])
            manifest.add(path)
        manifest.add(ROOT / 'examples/01_validos/05_demo.txt')
        self.assertEqual(manifest, set((ROOT / 'examples').rglob('*.txt')))
        self.assertEqual(list((ROOT / 'examples').rglob('*.alga')), [])
        self.assertEqual(list(ROOT.glob('*.alga')), [])

    def test_long_valid_and_invalid_inputs(self):
        valid = (ROOT / 'test_valid.txt').read_text()
        invalid = (ROOT / 'test_invalid.txt').read_text()
        self.assertEqual(analyze(valid)['errors'], [])
        self.assertEqual(analyze(invalid, 'parse')['errors'], [])
        errors = analyze(invalid)['errors']
        self.assertEqual(len(errors), 57)
        self.assertIn('destinoNoDeclarado', errors[0])
        self.assertIn('errorAlFinal', errors[-1])

    def test_sibling_scopes_on_same_line_are_independent(self):
        source = 'if (1 < 2) { scalar x; } else { scalar x; }'
        self.assertEqual(analyze(source)['errors'], [])
        source = 'if (1 < 2) { scalar x; } else { print(x); }'
        self.assertIn('Variable x no declarada', analyze(source)['errors'][0])

    def test_while_body_is_checked_with_valid_condition(self):
        errors = analyze('while (1 < 2) { x = 1; }')['errors']
        self.assertEqual(len(errors), 1)
        self.assertIn('Variable x no declarada', errors[0])

    def test_cli_from_other_directory_without_pythonpath(self):
        environment = dict(os.environ)
        environment.pop('PYTHONPATH', None)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'entrada.txt'
            path.write_text('scalar k = 1; print(k);', encoding='utf-8')
            result = subprocess.run(
                [sys.executable, str(ROOT / 'main.py'), 'entrada.txt', '--json'],
                cwd=directory, env=environment, capture_output=True, text=True,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['errors'], [])
