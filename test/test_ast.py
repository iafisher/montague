import unittest

from montague.ast import *


class FormulaToStrTest(unittest.TestCase):
    def test_variable_to_str(self):
        self.assertEqual(str(Var('a')), 'a')

    def test_and_to_str(self):
        self.assertEqual(str(And(Var('a'), Var('b'))), 'a & b')

    def test_or_to_str(self):
        self.assertEqual(str(Or(Var('a'), Var('b'))), 'a | b')

    def test_if_then_to_str(self):
        self.assertEqual(str(IfThen(Var('a'), Var('b'))), 'a -> b')

    def test_if_and_only_if_to_str(self):
        self.assertEqual(
            str(IfAndOnlyIf(Var('a'), Var('b'))),
            'a <-> b'
        )

    def test_lambda_to_str(self):
        tree = Lambda('x', And(Var('a'), Var('x')))
        self.assertEqual(str(tree), 'λx.a & x')
        self.assertEqual(tree.ascii_str(), 'Lx.a & x')
        # This formula is semantically invalid but that doesn't matter.
        self.assertEqual(
            str(
                And(
                    Lambda('x', Var('x')),
                    Lambda('y', Var('y'))
                )
            ),
            '[λx.x] & [λy.y]'
        )

    def test_call_to_str(self):
        self.assertEqual(
            str(
                Call(
                    Call(Var('P'), And(Var('a'), Var('b'))),
                    Lambda('x', Var('x'))
                )
            ),
            'P(a & b, λx.x)'
        )
        self.assertEqual(str(Call(Var('P'), Var('x'))), 'P(x)')

    def test_for_all_to_str(self):
        tree = ForAll('x', Call(Var('P'), Var('x')))
        self.assertEqual(str(tree), '∀ x.P(x)')
        self.assertEqual(tree.ascii_str(), 'Ax.P(x)')

    def test_exists_to_str(self):
        tree = Exists('x', Call(Var('P'), Var('x')))
        self.assertEqual(str(tree), '∃ x.P(x)')
        self.assertEqual(tree.ascii_str(), 'Ex.P(x)')

    def test_not_to_str(self):
        self.assertEqual(str(Not(Var('x'))), '~x')
        self.assertEqual(
            str(Not(Or(Var('x'), Var('y')))),
            '~[x | y]'
        )

    def test_binary_operators_to_str(self):
        self.assertEqual(
            str(And(Or(Var('a'), Var('b')), Var('c'))),
            '[a | b] & c'
        )
        self.assertEqual(
            str(Or(And(Var('a'), Var('b')), Var('c'))),
            'a & b | c'
        )
        self.assertEqual(
            str(Or(Var('a'), Or(Var('b'), Var('c')))),
            'a | b | c'
        )
        self.assertEqual(
            str(And(Var('a'), And(Var('b'), Var('c')))),
            'a & b & c'
        )

    def test_nested_exists_and_for_all_to_str(self):
        self.assertEqual(
            str(
                And(
                    ForAll('x', Var('x')),
                    Exists('x', Var('x'))
                )
            ),
            '[∀ x.x] & [∃ x.x]'
        )

    def test_iota_to_str(self):
        tree = Iota('x', Var('x'))
        self.assertEqual(str(tree), 'ιx.x')
        self.assertEqual(tree.ascii_str(), 'ix.x')


class TypeToStrTest(unittest.TestCase):
    def test_entity_to_str(self):
        self.assertEqual(str(TYPE_ENTITY), 'e')

    def test_event_to_str(self):
        self.assertEqual(str(TYPE_EVENT), 'v')

    def test_truth_value_to_str(self):
        self.assertEqual(str(TYPE_TRUTH_VALUE), 't')

    def test_world_to_str(self):
        self.assertEqual(str(TYPE_WORLD), 's')

    def test_recursive_type_to_str(self):
        self.assertEqual(
            str(ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE)),
            '<e, t>'
        )

    def test_deeply_recursive_type_to_str(self):
        self.assertEqual(
            str(
                ComplexType(
                    TYPE_EVENT,
                    ComplexType(
                        ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE),
                        ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE)
                    )
                )
            ),
            '<v, <<e, t>, <e, t>>>'
        )

    def test_recursive_type_to_concise_str(self):
        typ = ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE)
        self.assertEqual(typ.concise_str(), 'et')

    def test_deeply_recursive_type_to_concise_str(self):
        typ = ComplexType(
            TYPE_EVENT,
            ComplexType(
                ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE),
                ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE)
            )
        )
        self.assertEqual(typ.concise_str(), '<v, <et, et>>')


class ReplacerTest(unittest.TestCase):
    def test_simple_replace_variable(self):
        self.assertTupleEqual(
            Var('x').replace_variable('x', Var('y')),
            Var('y')
        )

    def test_replace_variable_in_and_or(self):
        tree = And(Or(Var('x'), Var('y')), Var('z'))
        self.assertTupleEqual(
            tree.replace_variable('x', Var("x'")),
            And(Or(Var("x'"), Var('y')), Var('z'))
        )

    def test_replace_predicate(self):
        tree = Call(Var('P'), Var('x'))
        self.assertTupleEqual(
            tree.replace_variable('P', Var('Good')),
            Call(Var('Good'), Var('x'))
        )

    def test_replace_variable_in_quantifiers(self):
        tree = ForAll('x',
            Or(
                And(
                    ForAll('b', Var('b')),
                    Exists('b', Var('b')),
                ),
                Exists('y', Var('b'))
            )
        )
        self.assertTupleEqual(
            tree.replace_variable('b', Var('bbb')),
            ForAll(
                'x',
                Or(
                    And(
                        ForAll('b', Var('b')),
                        Exists('b', Var('b')),
                    ),
                    Exists('y', Var('bbb'))
                )
            )
        )


    def test_recursive_replace_variable(self):
        # BFP(x, Lx.x, x & y)
        tree = Call(
            Call(
                Call(Var('BFP'), Var('x')),
                Lambda('x', Var('x'))  # This should not be replaced.
            ),
            And(Var('x'), Var('y'))
        )
        self.assertTupleEqual(
            tree.replace_variable('x', Var('j')),
            Call(
                Call(
                    Call(
                        Var('BFP'),
                        Var('j')
                    ),
                    Lambda('x', Var('x'))
                ),
                And(Var('j'), Var('y'))
            )
        )

    def test_replace_variable_in_iota(self):
        tree = Iota('x', And(Var('x'), Var('y')))
        self.assertTupleEqual(tree.replace_variable('x', Var('a')), tree)
        self.assertTupleEqual(
            tree.replace_variable('y', Var('b')),
            Iota('x', And(Var('x'), Var('b')))
        )
