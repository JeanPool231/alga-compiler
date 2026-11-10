import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from antlr4 import CommonTokenStream, InputStream

from codegen.code_gen_visitor import CodeGenVisitor
from codegen.TACEmitter import BINARY_OPERATORS
from gen.AlgaLexer import AlgaLexer
from gen.AlgaParser import AlgaParser
from main import analyze
from semantic.semantic_visitor import SemanticVisitor

ROOT = Path(__file__).resolve().parents[1]


def generar(source):
    parser = AlgaParser(CommonTokenStream(AlgaLexer(InputStream(source))))
    tree = parser.s()
    semantico = SemanticVisitor()
    semantico.visit(tree)
    assert not semantico.errors, semantico.errors
    generador = CodeGenVisitor(semantico)
    generador.visit(tree)
    return generador.tac


def codigo(source):
    resultado = analyze(source, "tac")
    assert resultado["errors"] == [], resultado["errors"]
    cuerpo = resultado["tac"].split(".code", 1)[1]
    return [linea.strip() for linea in cuerpo.splitlines() if linea.strip()]


def programas_validos():
    manifiesto = json.loads((ROOT / "examples/casos.json").read_text(encoding="utf-8"))
    rutas = [
        ROOT / c["archivo"]
        for c in manifiesto
        if c["error"] is None and c["archivo"].startswith("examples/01_validos/")
    ]
    rutas += sorted((ROOT / "examples/05_metodos_numericos").glob("*.txt"))
    rutas += sorted((ROOT / "examples/06_tac").glob("*.txt"))
    rutas += [ROOT / "test_valid.txt"]
    return rutas


class TACEsperado(unittest.TestCase):
    def test_expresion_con_precedencia(self):
        self.assertEqual(
            codigo("scalar x = 5; scalar y = 3; scalar z = x + y * 2;"),
            ["x = 5", "y = 3", "t1 = y * 2", "t2 = x + t1", "z = t2"],
        )

    def test_asociatividad_izquierda(self):
        self.assertEqual(
            codigo("scalar a = 1; scalar r = a - 2 - 3;"),
            ["a = 1", "t1 = a - 2", "t2 = t1 - 3", "r = t2"],
        )

    def test_unario(self):
        self.assertEqual(
            codigo("scalar x = -3; scalar y = -x; scalar z = +x;"),
            ["x = -3", "t1 = -x", "y = t1", "z = x"],
        )

    def test_declaracion_sin_inicializador_no_genera_codigo(self):
        self.assertEqual(codigo("scalar x; vector v[2]; matrix A[2][2];"), [])

    def test_if_sin_else(self):
        self.assertEqual(
            codigo("scalar a = 1; if (a > 0) { a = 2; }"),
            ["a = 1", "t1 = a > 0", "ifFalse t1 goto L1", "a = 2", "L1:"],
        )

    def test_if_else(self):
        self.assertEqual(
            codigo("scalar a = 1; if (a > 0) { a = 2; } else { a = 3; }"),
            [
                "a = 1",
                "t1 = a > 0",
                "ifFalse t1 goto L1",
                "a = 2",
                "goto L2",
                "L1:",
                "a = 3",
                "L2:",
            ],
        )

    def test_while(self):
        self.assertEqual(
            codigo("scalar i = 0; while (i < 3) { i = i + 1; }"),
            [
                "i = 0",
                "L1:",
                "t1 = i < 3",
                "ifFalse t1 goto L2",
                "t2 = i + 1",
                "i = t2",
                "goto L1",
                "L2:",
            ],
        )

    def test_for(self):
        self.assertEqual(
            codigo(
                "scalar s = 0; scalar i; for (i = 0; i < 3; i = i + 1) { s = s + i; }"
            ),
            [
                "s = 0",
                "i = 0",
                "L1:",
                "t1 = i < 3",
                "ifFalse t1 goto L2",
                "t2 = s + i",
                "s = t2",
                "t3 = i + 1",
                "i = t3",
                "goto L1",
                "L2:",
            ],
        )

    def test_condicion_sin_comparador_usa_el_valor_directo(self):
        self.assertEqual(
            codigo("matrix A[2][2]; if (isSymmetric(A)) { }"),
            ["param A", "t1 = call isSymmetric, 1", "ifFalse t1 goto L1", "L1:"],
        )

    def test_literales_de_vector_y_matriz(self):
        self.assertEqual(
            codigo("vector v[2] = [-1,2]; matrix A[2][2] = [[1,2],[3,4]];"),
            ["v[0] = -1", "v[8] = 2", "A[0] = 1", "A[8] = 2", "A[16] = 3", "A[24] = 4"],
        )

    def test_indice_constante_se_pliega(self):
        # A[1][2] matrix 2x3: (1*3 + 2) * 8 = 40
        self.assertEqual(codigo("matrix A[2][3]; A[1][2] = 7;"), ["A[40] = 7"])

    def test_indice_variable_por_filas(self):
        self.assertEqual(
            codigo("matrix A[2][3]; scalar i = 1; scalar j = 2; scalar x = A[i][j];"),
            [
                "i = 1",
                "j = 2",
                "t1 = i * 3",
                "t2 = t1 + j",
                "t3 = t2 * 8",
                "t4 = A[t3]",
                "x = t4",
            ],
        )

    def test_escritura_en_vector_con_indice_variable(self):
        self.assertEqual(
            codigo("vector v[3]; scalar i = 1; v[i] = 5;"),
            ["i = 1", "t1 = i * 8", "v[t1] = 5"],
        )

    def test_llamada_evalua_argumentos_antes_de_los_param(self):
        self.assertEqual(
            codigo("matrix A[2][2]; vector b[2]; vector x[2] = solve(A, b);"),
            ["param A", "param b", "t1 = call solve, 2", "x = t1"],
        )

    def test_print_no_devuelve_valor(self):
        self.assertEqual(codigo('print("hola");'), ['param "hola"', "call print, 1"])

    def test_operador_de_alto_nivel_sobre_agregados(self):
        self.assertEqual(
            codigo(
                "matrix A[2][2]; vector x[2]; vector b[2]; vector r[2] = b - A * x;"
            ),
            ["t1 = A * x", "t2 = b - t1", "r = t2"],
        )

    def test_literal_dentro_de_una_expresion_usa_un_temporal(self):
        self.assertEqual(
            codigo("matrix A[2][2]; matrix C[2][2] = A * [[1,0],[0,1]];"),
            [
                "t1[0] = 1",
                "t1[8] = 0",
                "t1[16] = 0",
                "t1[24] = 1",
                "t2 = A * t1",
                "C = t2",
            ],
        )


class Nombres(unittest.TestCase):
    def test_variable_oculta_recibe_nombre_unico(self):
        self.assertEqual(
            codigo("scalar k; if (1 > 0) { vector k[2]; k[0] = 1; } k = 2;"),
            ["t1 = 1 > 0", "ifFalse t1 goto L1", "k_1[0] = 1", "L1:", "k = 2"],
        )

    def test_ambito_que_se_cierra_no_afecta_al_exterior(self):
        lineas = codigo(
            "scalar k = 1; if (k > 0) { scalar k = 5; k = k + 1; } k = k + 2;"
        )
        self.assertIn("k_1 = 5", lineas)
        self.assertIn("t2 = k_1 + 1", lineas)
        self.assertIn("t3 = k + 2", lineas)

    def test_variable_del_usuario_no_choca_con_temporales_ni_etiquetas(self):
        lineas = codigo("scalar t1 = 1; scalar L1 = 2; scalar y = t1 + L1;")
        self.assertEqual(lineas, ["t1_1 = 1", "L1_1 = 2", "t1 = t1_1 + L1_1", "y = t1"])

    def test_zona_data_con_tamanos(self):
        tac = analyze("scalar s; vector v[3]; matrix A[2][3];", "tac")["tac"]
        data = tac.split(".code")[0]
        self.assertIn("s : scalar", data)
        self.assertIn("8 bytes", data)
        self.assertIn("v : vector[3]", data)
        self.assertIn("24 bytes", data)
        self.assertIn("A : matrix[2][3]", data)
        self.assertIn("48 bytes", data)


OPERANDO = re.compile(r'-?[0-9]+(?:\.[0-9]+)?$|[A-Za-z_][A-Za-z0-9_]*$|".*"$')
TEMPORAL = re.compile(r"t[0-9]+$")


class Invariantes(unittest.TestCase):
    def test_invariantes_de_todos_los_programas(self):
        programas = programas_validos()
        self.assertGreater(len(programas), 40)
        for ruta in programas:
            with self.subTest(archivo=ruta.name):
                self._comprobar(generar(ruta.read_text(encoding="utf-8")))

    def _comprobar(self, tac):
        quads = tac.instructions()
        etiquetas = [q.res for q in quads if q.op == "label"]
        self.assertEqual(
            len(etiquetas), len(set(etiquetas)), "etiqueta definida dos veces"
        )

        definidos = set()
        for q in quads:
            if q.op in BINARY_OPERATORS:
                self.assertIsNotNone(q.arg1)
                self.assertIsNotNone(q.arg2)
            for operando in self._lecturas(q):
                self.assertRegex(operando, OPERANDO)
                if TEMPORAL.match(operando):
                    self.assertIn(
                        operando, definidos, f"{q}: temporal usado sin definir"
                    )
                elif not operando[0] in '-0123456789"':
                    self.assertIn(operando, tac.types, f"{q}: variable sin declarar")

            if q.op in ("aload", "astore"):
                self.assertIn(q.arg1, tac.types, f"{q}: base sin declarar")
            if q.op in ("goto", "ifFalse"):
                self.assertIn(q.res, etiquetas, f"{q}: salto sin destino")
            if q.op == "astore" and TEMPORAL.match(q.arg1):
                definidos.add(q.arg1)
            elif q.op not in ("label", "goto", "ifFalse", "astore", "param") and q.res:
                if TEMPORAL.match(q.res):
                    self.assertNotIn(
                        q.res, definidos, f"{q}: temporal asignado dos veces"
                    )
                    definidos.add(q.res)

    @staticmethod
    def _lecturas(q):
        if q.op in BINARY_OPERATORS:
            return [q.arg1, q.arg2]
        if q.op in ("copy", "neg", "param"):
            return [q.arg1]
        if q.op == "ifFalse":
            return [q.arg1]
        if q.op == "aload":
            return [q.arg1, q.arg2]
        if q.op == "astore":
            return [q.arg2, q.res]
        return []

    def test_todo_programa_valido_genera_tac_sin_errores(self):
        for ruta in programas_validos():
            with self.subTest(archivo=ruta.name):
                resultado = analyze(ruta.read_text(encoding="utf-8"), "tac")
                self.assertEqual(resultado["errors"], [])
                self.assertIn(".code", resultado["tac"])


class ArchivosDeReferencia(unittest.TestCase):
    def casos(self):
        carpeta = ROOT / "examples/06_tac"
        pares = [(f, f.with_suffix(".tac")) for f in sorted(carpeta.glob("*.txt"))]
        for numerico in sorted((ROOT / "examples/05_metodos_numericos").glob("*.txt")):
            pares.append((numerico, carpeta / (numerico.stem + ".tac")))
        return pares

    def test_tac_coincide_con_el_de_referencia(self):
        pares = self.casos()
        self.assertGreaterEqual(len(pares), 10)
        for fuente, esperado in pares:
            with self.subTest(archivo=fuente.name):
                resultado = analyze(fuente.read_text(encoding="utf-8"), "tac")
                self.assertEqual(resultado["errors"], [])
                self.assertEqual(
                    resultado["tac"] + "\n", esperado.read_text(encoding="utf-8")
                )


class LineaDeComandos(unittest.TestCase):
    def ejecutar(self, *args):
        return subprocess.run(
            [sys.executable, str(ROOT / "main.py"), *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

    def test_fase_tac(self):
        r = self.ejecutar("examples/06_tac/01_escalares.txt", "--phase", "tac")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("t1 = y * 2", r.stdout)
        self.assertNotIn("OK:", r.stdout)

    def test_programa_con_errores_no_genera_tac(self):
        r = self.ejecutar(
            "examples/04_errores_semanticos/dimension_vector.txt", "--phase", "tac"
        )
        self.assertEqual(r.returncode, 1)
        self.assertIn("semántico:", r.stderr)
        self.assertNotIn(".code", r.stdout)

    def test_out_guarda_el_resultado(self):
        with tempfile.TemporaryDirectory() as carpeta:
            destino = Path(carpeta) / "salida.tac"
            r = self.ejecutar(
                "examples/06_tac/01_escalares.txt",
                "--phase",
                "tac",
                "--out",
                str(destino),
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(destino.read_text(encoding="utf-8"), r.stdout)

    def test_json_incluye_tac(self):
        r = self.ejecutar(
            "examples/06_tac/01_escalares.txt", "--phase", "tac", "--json"
        )
        datos = json.loads(r.stdout)
        self.assertEqual(datos["errors"], [])
        self.assertIn("t1 = y * 2", datos["tac"])

    def test_fases_anteriores_siguen_igual(self):
        r = self.ejecutar("examples/01_validos/05_demo.txt")
        self.assertEqual(r.returncode, 0)
        self.assertIn("OK: fase semantic", r.stdout)


if __name__ == "__main__":
    unittest.main()
