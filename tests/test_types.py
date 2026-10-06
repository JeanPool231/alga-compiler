import unittest
from semantic.type_rules import Type, SCALAR, STRING, BOOL, VOID, ERROR, binary, builtin


class TypeTests(unittest.TestCase):
    def test_matrix_product_rectangular(self):
        self.assertEqual(binary('*', Type('matrix', (2, 3)), Type('matrix', (3, 4))), Type('matrix', (2, 4)))
        with self.assertRaises(ValueError):
            binary('*', Type('matrix', (2, 3)), Type('matrix', (2, 2)))

    def test_matrix_vector(self):
        self.assertEqual(binary('*', Type('matrix', (2, 3)), Type('vector', (3,))), Type('vector', (2,)))
        with self.assertRaises(ValueError):
            binary('*', Type('matrix', (2, 3)), Type('vector', (2,)))

    def test_addition_requires_exact_shape(self):
        self.assertEqual(binary('+', Type('vector', (3,)), Type('vector', (3,))), Type('vector', (3,)))
        with self.assertRaises(ValueError):
            binary('+', Type('vector', (3,)), Type('vector', (2,)))

    def test_scaling_and_division(self):
        vector = Type('vector', (3,))
        self.assertEqual(binary('*', SCALAR, vector), vector)
        self.assertEqual(binary('*', vector, SCALAR), vector)
        self.assertEqual(binary('/', vector, SCALAR), vector)
        with self.assertRaises(ValueError):
            binary('/', SCALAR, vector)

    def test_strings_and_void_cannot_participate_in_arithmetic(self):
        for value in (STRING, BOOL, VOID):
            with self.subTest(value=value), self.assertRaises(ValueError):
                binary('+', value, SCALAR)

    def test_error_propagation(self):
        self.assertEqual(binary('*', ERROR, SCALAR), ERROR)
        self.assertEqual(builtin('det', [ERROR]), ERROR)

    def test_all_builtins(self):
        square = Type('matrix', (2, 2))
        vector = Type('vector', (2,))
        for name in ('det', 'trace', 'rows', 'cols'):
            self.assertEqual(builtin(name, [square]), SCALAR)
        self.assertEqual(builtin('transpose', [Type('matrix', (2, 3))]), Type('matrix', (3, 2)))
        self.assertEqual(builtin('solve', [square, vector]), vector)
        self.assertEqual(builtin('norm', [vector]), SCALAR)
        self.assertEqual(builtin('isSymmetric', [square]), BOOL)
        self.assertEqual(builtin('print', [STRING]), VOID)

    def test_builtin_bad_types_arity_and_names(self):
        for name, args in [('det', [SCALAR]), ('det', [Type('matrix', (2, 3))]),
                           ('solve', [Type('matrix', (2, 2)), Type('vector', (3,))]),
                           ('norm', []), ('trace', [SCALAR, SCALAR]),
                           ('print', [VOID]), ('inventada', [SCALAR])]:
            with self.subTest(name=name, args=args), self.assertRaises(ValueError):
                builtin(name, args)


class IndexTests(unittest.TestCase):
    def check_index(self, base, types, texts):
        from semantic.type_rules import indexed
        return indexed(base, types, texts)

    def test_valid_literal_and_dynamic_indices(self):
        self.assertEqual(self.check_index(Type('vector', (3,)), [SCALAR], ['2']), SCALAR)
        self.assertEqual(self.check_index(Type('matrix', (2, 3)), [SCALAR, SCALAR], ['i', 'j+1']), SCALAR)
        self.assertEqual(self.check_index(Type('vector', (3,)), [SCALAR], ['1.0']), SCALAR)

    def test_bad_count_and_scalar_base(self):
        for base, types, texts in [(SCALAR, [SCALAR], ['0']),
                                   (Type('matrix', (2, 2)), [SCALAR], ['0']),
                                   (Type('vector', (3,)), [SCALAR, SCALAR], ['0','0'])]:
            with self.subTest(base=base), self.assertRaises(ValueError):
                self.check_index(base, types, texts)

    def test_fractional_and_out_of_bounds_literals(self):
        for text in ['-1', '3', '1.5', '+9']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.check_index(Type('vector', (3,)), [SCALAR], [text])

    def test_type_and_error_propagation(self):
        with self.assertRaises(ValueError):
            self.check_index(Type('vector', (3,)), [STRING], ['"i"'])
        self.assertEqual(self.check_index(ERROR, [SCALAR], ['0']), ERROR)
        self.assertEqual(self.check_index(Type('vector', (3,)), [ERROR], ['i']), ERROR)
