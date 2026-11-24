import os
import tempfile
import unittest
import unicodedata
from unittest import mock

from antlr4 import InputStream

from main import compilar
from semantic import csv_data
from vm import VM

def plain(text):
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()


class CsvBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def write(self, name, content):
        path = os.path.join(self.dir, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, "wb") as handle:
            handle.write(content if isinstance(content, bytes) else content.encode("utf-8"))

    def compile(self, source, base_dir="default"):
        base = self.dir if base_dir == "default" else base_dir
        return compilar(InputStream(source), base_dir=base)

    def run_ok(self, source):
        result, tac = self.compile(source)
        self.assertEqual(result["errors"], [], result["errors"])
        out = []
        VM(tac, output=out.append).run()
        return out

    def errors(self, source, **kw):
        return [str(e) for e in self.compile(source, **kw)[0]["errors"]]

    def assert_error(self, source, fragment, **kw):
        errs = self.errors(source, **kw)
        self.assertTrue(any(plain(fragment) in plain(e) for e in errs), errs)
        self.assertRegex(errs[0], r"^semántico:\d+:\d+: csv:" if "csv:" in errs[0] else r":\d+:\d+:")


class CsvShapeTests(CsvBase):
    def test_matrix(self):
        self.write("m.csv", "1,2\n3,4\n5,6\n")
        self.assertEqual(self.run_ok('auto A = csv("m.csv"); print(A); print(rows(A)); print(cols(A));'),
                         ["[[1, 2],\n [3, 4],\n [5, 6]]", "3", "2"])

    def test_single_column_is_vector(self):
        self.write("v.csv", "1\n2\n3\n")
        self.assertEqual(self.run_ok('auto v = csv("v.csv"); print(v);'), ["[1, 2, 3]"])

    def test_single_row_is_vector(self):
        self.write("v.csv", "1,2,3\n")
        self.assertEqual(self.run_ok('auto v = csv("v.csv"); print(v);'), ["[1, 2, 3]"])

    def test_single_value_is_vector_of_one(self):
        self.write("v.csv", "7\n")
        self.assertEqual(self.run_ok('auto v = csv("v.csv"); print(v);'), ["[7]"])

    def test_declared_target_is_checked_against_file(self):
        self.write("m.csv", "1,2\n3,4\n")
        self.assertEqual(self.run_ok('matrix A[2][2] = csv("m.csv"); print(trace(A));'), ["5"])
        self.assert_error('matrix A[3][2] = csv("m.csv");', "Se esperaba matrix[3][2]; se obtuvo matrix[2][2]")
        self.assert_error('vector v[4] = csv("m.csv");', "Se esperaba vector[4]; se obtuvo matrix[2][2]")

    def test_usable_inside_expressions(self):
        self.write("v.csv", "1\n2\n")
        self.write("m.csv", "2,0\n0,2\n")
        self.assertEqual(self.run_ok('print(csv("m.csv") * csv("v.csv"));'), ["[2, 4]"])
        self.assertEqual(self.run_ok('print(csv("v.csv") * 10);'), ["[10, 20]"])

    def test_shape_mismatch_in_operation_is_a_normal_semantic_error(self):
        self.write("v.csv", "1,2,3\n")
        self.write("m.csv", "1,2\n3,4\n")
        self.assertTrue(self.errors('print(csv("m.csv") * csv("v.csv"));'))

    def test_assignment_keeps_value_semantics(self):
        self.write("v.csv", "1,2\n")
        out = self.run_ok('auto a = csv("v.csv"); auto b = csv("v.csv"); a[0] = 9; print(a); print(b);')
        self.assertEqual(out, ["[9, 2]", "[1, 2]"])


class CsvFormatTests(CsvBase):
    def test_default_separator_is_comma_and_custom_separators(self):
        self.write("semi.csv", "1;2\n3;4\n")
        self.write("tab.csv", "1\t2\n3\t4\n")
        self.assertEqual(self.run_ok('print(csv("semi.csv", ";"));'), ["[[1, 2],\n [3, 4]]"])
        self.assertEqual(self.run_ok('print(csv("tab.csv", "\\t"));'), ["[[1, 2],\n [3, 4]]"])
        self.assert_error('print(csv("semi.csv"));', "valor no numérico")

    def test_number_formats(self):
        self.write("n.csv", "1e2, -3.5 ,+4\n.5,7.,0\n")
        self.assertEqual(self.run_ok('print(csv("n.csv"));'), ["[[100, -3.5, 4],\n [0.5, 7, 0]]"])

    def test_quoted_numbers(self):
        self.write("q.csv", '"1.5",2\n')
        self.assertEqual(self.run_ok('print(csv("q.csv"));'), ["[1.5, 2]"])

    def test_crlf_bom_and_blank_lines(self):
        self.write("w.csv", b"\xef\xbb\xbf1,2\r\n\r\n3,4\r\n\r\n")
        self.assertEqual(self.run_ok('print(csv("w.csv"));'), ["[[1, 2],\n [3, 4]]"])

    def test_text_cell_fails_with_position(self):
        self.write("h.csv", "x,y\n1,2\n")
        self.assert_error('auto A = csv("h.csv");', "valor no numérico en la línea 1, columna 1: 'x'")

    def test_bad_numbers_fail(self):
        for index, cell in enumerate(["nan", "inf", "1_0", "0x10", "1e999", "--1", "1,5x"]):
            with self.subTest(cell=cell):
                self.write(f"b{index}.csv", f"1,{cell}\n")
                self.assertTrue(self.errors(f'auto A = csv("b{index}.csv");'))

    def test_empty_cell_and_trailing_separator_fail(self):
        self.write("e.csv", "1,,3\n")
        self.write("t.csv", "1,2,\n")
        self.assert_error('auto A = csv("e.csv");', "una celda vacía")
        self.assert_error('auto A = csv("t.csv");', "una celda vacía")

    def test_ragged_rows_fail(self):
        self.write("r.csv", "1,2,3\n4,5\n")
        self.assert_error('auto A = csv("r.csv");', "la línea 2 tiene 2 valores y la primera fila tiene 3")

    def test_empty_file_fails(self):
        self.write("e.csv", "\n\n")
        self.assert_error('auto A = csv("e.csv");', "está vacío")

    def test_non_utf8_fails(self):
        self.write("b.csv", b"\xff\xfe1,2\n")
        self.assert_error('auto A = csv("b.csv");', "no es texto UTF-8")

    def test_value_limit(self):
        self.write("m.csv", "1,2\n3,4\n")
        with mock.patch.object(csv_data, "MAX_VALUES", 3):
            self.assert_error('auto A = csv("m.csv");', "excede el máximo de 3 valores")


class CsvPathAndArgumentTests(CsvBase):
    def test_path_is_relative_to_base_dir_including_subfolders(self):
        self.write("data/m.csv", "1,2\n")
        self.assertEqual(self.run_ok('print(csv("data/m.csv"));'), ["[1, 2]"])

    def test_missing_file(self):
        self.assert_error('auto A = csv("nada.csv");', "no se encontró el archivo 'nada.csv'")

    def test_directory_is_not_a_file(self):
        os.makedirs(os.path.join(self.dir, "carpeta"))
        self.assert_error('auto A = csv("carpeta");', "no es un archivo")

    def test_absolute_and_escaping_paths_are_rejected(self):
        self.write("m.csv", "1,2\n")
        self.assert_error(f'auto A = csv("{os.path.join(self.dir, "m.csv")}");', "debe ser relativa")
        sub = os.path.join(self.dir, "sub")
        os.makedirs(sub)
        self.assert_error('auto A = csv("../m.csv");', "sale del directorio del programa", base_dir=sub)

    def test_no_base_dir_means_no_csv(self):
        self.assert_error('auto A = csv("m.csv");', "no está disponible aquí", base_dir=None)
        
    def test_arguments_must_be_string_literals(self):
        self.write("m.csv", "1,2\n")
        self.assert_error('auto A = csv(5);', "textos literales")
        self.assert_error('auto A = csv("m.csv", 5);', "textos literales")
        self.assert_error('scalar s = 1; auto A = csv(s);', "textos literales")
        self.assert_error('auto A = csv("m" + "x");', "textos literales")

    def test_argument_count_and_separator_validation(self):
        self.write("m.csv", "1,2\n")
        self.assert_error('auto A = csv("m.csv", ",", ",");', "una ruta y, opcionalmente, un separador")
        self.assert_error('auto A = csv("m.csv", ",,");', "un solo carácter")
        self.assert_error('auto A = csv("m.csv", "");', "un solo carácter")

    def test_error_is_reported_at_the_call_line(self):
        errs = self.errors('scalar a = 1;\nauto A = csv("nada.csv");')
        self.assertTrue(errs[0].startswith("semántico:2:10: csv:"), errs)


class AutoTests(CsvBase):
    def test_infers_every_kind(self):
        out = self.run_ok(
            "auto s = 2 + 3; auto v = [1, 2, 3]; auto m = [[1, 2], [3, 4]];"
            "auto w = m * [1, 1]; auto t = transpose(m); auto n = det(m);"
            "print(s); print(v); print(w); print(t); print(n);"
        )
        
        self.assertEqual(out, ["5", "[1, 2, 3]", "[3, 7]", "[[1, 3],\n [2, 4]]", "-2"])

    def test_inferred_type_is_enforced_later(self):
        self.assertTrue(self.errors("auto v = [1, 2, 3]; v = [1, 2];"))
        self.assertTrue(self.errors("auto s = 1; s = [1, 2];"))

    def test_requires_initializer(self):
        self.assertTrue(any("sintáctico" in e for e in self.errors("auto x;")))

    def test_cannot_infer_from_string(self):
        self.assertTrue(any("auto no puede deducir" in e for e in self.errors('auto x = "hola";')))

    def test_not_visible_in_its_own_initializer(self):
        self.assertTrue(any("no declarada" in e for e in self.errors("auto x = x + 1;")))

    def test_redeclaration_is_an_error(self):
        self.assertTrue(self.errors("auto x = 1; scalar x;"))

    def test_scoping(self):
        out = self.run_ok("auto x = 1; if (x == 1) { auto x = 2; print(x); } print(x);")
        self.assertEqual(out, ["2", "1"])


if __name__ == "__main__":
    unittest.main()
