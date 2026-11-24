import unittest

from antlr4 import InputStream  # pyright: ignore[reportMissingModuleSource]

from main import compilar
from vm import VM, AlgaRuntimeError


def run(source, max_steps=1_000_000):
    result, tac = compilar(InputStream(source))
    assert not result["errors"], result["errors"]
    lines = []
    machine = VM(tac, output=lines.append, max_steps=max_steps)
    machine.run()

    return lines, machine


class VMTest(unittest.TestCase):
    def test_scalar_arithmetic_and_precedence(self):
        out, _ = run("scalar a = 2 + 3 * 4; print(a); print(-a / 4);")
        self.assertEqual(out, ["14", "-3.5"])

    def test_control_flow(self):
        out, _ = run(
            "scalar s = 0; scalar i;"
            "for (i = 1; i < 5; i = i + 1) { s = s + i; }"
            'if (s == 10) { print("ok"); } else { print("mal"); }'
        )

        self.assertEqual(out, ["ok"])

    def test_vectors_and_matrices(self):
        out, _ = run(
            "matrix A[2][2] = [[2,1],[1,3]]; vector b[2] = [3,5];"
            "print(A * b); print(transpose(A)); print(b - b * 2);"
        )

        self.assertEqual(out, ["[11, 18]", "[[2, 1],\n [1, 3]]", "[-3, -5]"])

    def test_builtins(self):
        out, _ = run(
            "matrix A[2][2] = [[2,1],[1,3]]; vector b[2] = [3,5];"
            "print(solve(A, b)); print(det(A)); print(trace(A));"
            "print(rows(A)); print(isSymmetric(A)); print(norm(b));"
        )

        self.assertEqual(out[0], "[0.8, 1.4]")
        self.assertEqual(out[1:5], ["5", "5", "2", "1"])
        self.assertEqual(out[5], "5.830951895")

    def test_assignment_copies_value(self):
        out, _ = run(
            "vector a[2] = [1,2]; vector b[2] = a; b[0] = 9; print(a); print(b);"
        )

        self.assertEqual(out, ["[1, 2]", "[9, 2]"])

    def test_shadowed_scopes(self):
        out, _ = run("scalar x = 1; if (x == 1) { scalar x = 2; print(x); } print(x);")
        self.assertEqual(out, ["2", "1"])

    def test_string_escapes(self):
        out, _ = run('print("a\\tb");')
        self.assertEqual(out, ["a\tb"])

    def test_variables_excludes_temps(self):
        _, machine = run("scalar a = 1 + 2;")
        self.assertEqual(machine.variables(), {"a": 3.0})

    def test_division_by_zero(self):
        with self.assertRaises(AlgaRuntimeError) as ctx:
            run("scalar z = 0;\nscalar a = 1 / z;")

        self.assertEqual(ctx.exception.pos, (2, 1))

    def test_index_out_of_range(self):
        with self.assertRaises(AlgaRuntimeError):
            run("vector v[2] = [1,2]; scalar i = 2; print(v[i]);")

    def test_fractional_index(self):
        with self.assertRaises(AlgaRuntimeError):
            run("vector v[2] = [1,2]; scalar i = 0.5; print(v[i]);")

    def test_singular_solve(self):
        with self.assertRaises(AlgaRuntimeError):
            run(
                "matrix A[2][2] = [[1,2],[2,4]]; vector b[2] = [1,1]; print(solve(A, b));"
            )

    def test_memory_limit(self):
        _, tac = compilar(InputStream("vector v[2000000];"))

        with self.assertRaises(AlgaRuntimeError):
            VM(tac)

    def test_step_limit(self):
        with self.assertRaises(AlgaRuntimeError):
            run("scalar x = 1; while (x > 0) { x = x + 1; }", max_steps=1000)

    def test_numerical_examples(self):
        import glob

        for path in sorted(glob.glob("examples/05_metodos_numericos/*.txt")):
            with open(path, encoding="utf-8") as handle:
                out, _ = run(handle.read())

            self.assertTrue(out, path)


if __name__ == "__main__":
    unittest.main()
