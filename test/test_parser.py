import unittest

from montague.ast import *
from montague.parser import parse_formula, parse_type

from lark.exceptions import LarkError


class FormulaParseTest(unittest.TestCase):
    def test_parsing_variable(self):
        self.assertTupleEqual(parse_formula('a'), Var('a'))
        self.assertTupleEqual(
            parse_formula("s8DVY_BUvybJH-VDNS'JhjS"),
            Var('s8DVY_BUvybJH-VDNS\'JhjS')
        )

    def test_parsing_conjunction(self):
        self.assertTupleEqual(
            parse_formula("a & a'"),
            And(Var('a'), Var('a\''))
        )
        self.assertTupleEqual(
            parse_formula('a & b & c'),
            And(
                Var('a'),
                And(
                    Var('b'),
                    Var('c')
                )
            )
        )

    def test_parsing_disjunction(self):
        self.assertTupleEqual(
            parse_formula('b | b0'),
            Or(Var('b'), Var('b0'))
        )
        self.assertTupleEqual(
            parse_formula('a | b | c'),
            Or(
                Var('a'),
                Or(
                    Var('b'),
                    Var('c')
                )
            )
        )

    def test_parsing_if_then(self):
        self.assertTupleEqual(
            parse_formula('a -> b'),
            IfThen(Var('a'), Var('b'))
        )
        self.assertTupleEqual(
            parse_formula('a -> b -> c'),
            IfThen(
                Var('a'),
                IfThen(
                    Var('b'),
                    Var('c')
                )
            )
        )

    def test_parsing_if_and_only_if(self):
        self.assertTupleEqual(
            parse_formula('a <-> b'),
            IfAndOnlyIf(
                Var('a'),
                Var('b')
            )
        )
        self.assertTupleEqual(
            parse_formula('a <-> b <-> c'),
            IfAndOnlyIf(
                Var('a'),
                IfAndOnlyIf(
                    Var('b'),
                    Var('c')
                )
            )
        )

    def test_parsing_negation(self):
        self.assertEqual(parse_formula('~a'), Not(Var('a')))
        self.assertEqual(
            parse_formula('~a | b'),
            Or(Not(Var('a')), Var('b'))
        )
        self.assertEqual(
            parse_formula('~[a | b]'),
            Not(Or(Var('a'), Var('b')))
        )

    def test_parsing_binary_precedence(self):
        self.assertTupleEqual(
            parse_formula('x & y | z -> m'),
            IfThen(
                Or(
                    And(Var('x'), Var('y')),
                    Var('z')
                ),
                Var('m')
            )
        )
        self.assertTupleEqual(
            parse_formula('x | y -> m & z'),
            IfThen(
                Or(
                    Var('x'),
                    Var('y'),
                ),
                And(
                    Var('m'),
                    Var('z')
                )
            )
        )
        self.assertTupleEqual(
            parse_formula('[x | y] & z'),
            And(
                Or(Var('x'), Var('y')),
                Var('z')
            )
        )

    def test_parsing_lambda(self):
        self.assertTupleEqual(
            parse_formula('Lx.Ly.[x & y]'),
            Lambda(
                'x',
                Lambda(
                    'y',
                    And(Var('x'), Var('y'))
                )
            )
        )
        self.assertEqual(
            parse_formula('L x.L y.[x & y]'),
            Lambda(
                'x',
                Lambda(
                    'y',
                    And(Var('x'), Var('y'))
                )
            )
        )

    def test_parsing_call(self):
        self.assertTupleEqual(
            parse_formula('Happy(x)'),
            Call(Var('Happy'), Var('x'))
        )
        self.assertTupleEqual(
            parse_formula('Between(x, y & z, [Capital(france)])'),
            Call(
                Call(
                    Call(
                        Var('Between'),
                        Var('x')
                    ),
                    And(Var('y'), Var('z')),
                ),
                Call(Var('Capital'), Var('france')),
            )
        )
        self.assertTupleEqual(
            parse_formula('(Lx.x)(j)'),
            Call(
                Lambda('x', Var('x')),
                Var('j')
            )
        )
        self.assertTupleEqual(
            parse_formula('((Lx.Ly.x & y) (a)) (b)'),
            Call(
                Call(
                    Lambda(
                        'x',
                        Lambda('y', And(Var('x'), Var('y')))
                    ),
                    Var('a')
                ),
                Var('b')
            )
        )

    def test_parsing_for_all(self):
        self.assertTupleEqual(
            parse_formula('Ax.x & y'),
            ForAll('x', And(Var('x'), Var('y')))
        )
        self.assertTupleEqual(
            parse_formula('A x.x & y'),
            ForAll('x', And(Var('x'), Var('y')))
        )

    def test_parsing_exists(self):
        self.assertTupleEqual(
            parse_formula('Ex.x | y'),
            Exists('x', Or(Var('x'), Var('y')))
        )
        self.assertTupleEqual(
            parse_formula('E x.x | y'),
            Exists('x', Or(Var('x'), Var('y')))
        )

    def test_parsing_iota(self):
        self.assertTupleEqual(
            parse_formula('ix.Man(x)'),
            Iota('x', Call(Var('Man'), Var('x')))
        )
        self.assertTupleEqual(
            parse_formula('i x.Man(x)'),
            Iota('x', Call(Var('Man'), Var('x')))
        )


class FormulaParseErrorTest(unittest.TestCase):
    def test_missing_operand(self):
        with self.assertRaises(LarkError):
            parse_formula('a | ')
        with self.assertRaises(LarkError):
            parse_formula('b & ')
        with self.assertRaises(LarkError):
            parse_formula('| a')
        with self.assertRaises(LarkError):
            parse_formula('& b')

    def test_parsing_hanging_bracket(self):
        with self.assertRaises(LarkError):
            parse_formula('[x | y')

    def test_lambda_missing_body(self):
        with self.assertRaises(LarkError):
            parse_formula('Lx.')

    def test_for_all_missing_body(self):
        with self.assertRaises(LarkError):
            parse_formula('Ax.')

    def test_exists_missing_body(self):
        with self.assertRaises(LarkError):
            parse_formula('Ex.')

    def test_iota_missing_body(self):
        with self.assertRaises(LarkError):
            parse_formula('ix.')

    def test_call_with_no_arg(self):
        with self.assertRaises(LarkError):
            parse_formula('Happy()')

    def test_unknown_token(self):
        with self.assertRaises(LarkError):
            parse_formula('Lx.x?')

    def test_empty_string(self):
        with self.assertRaises(LarkError):
            parse_formula('')

    def test_blank(self):
        with self.assertRaises(LarkError):
            parse_formula('     \t    \n \r \f')


class TypeParseTest(unittest.TestCase):
    def test_parsing_atomic_types(self):
        self.assertEqual(parse_type('e'), TYPE_ENTITY)
        self.assertEqual(parse_type('t'), TYPE_TRUTH_VALUE)
        self.assertEqual(parse_type('v'), TYPE_EVENT)
        self.assertEqual(parse_type('s'), TYPE_WORLD)

    def test_parsing_compound_type(self):
        self.assertTupleEqual(
            parse_type('<e, t>'),
            ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE)
        )

    def test_parsing_abbreviated_compound_types(self):
        self.assertTupleEqual(
            parse_type('et'),
            ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE)
        )
        self.assertTupleEqual(
            parse_type('vt'),
            ComplexType(TYPE_EVENT, TYPE_TRUTH_VALUE)
        )

    def test_parsing_big_compound_type(self):
        self.assertTupleEqual(
            parse_type('<<e, t>, <e, <s, t>>>'),
            ComplexType(
                ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE),
                ComplexType(
                    TYPE_ENTITY,
                    ComplexType(TYPE_WORLD, TYPE_TRUTH_VALUE)
                )
            )
        )

    def test_parsing_big_compound_type_with_abbreviations(self):
        self.assertTupleEqual(
            parse_type('<et, <e, st>>'),
            ComplexType(
                ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE),
                ComplexType(
                    TYPE_ENTITY,
                    ComplexType(TYPE_WORLD, TYPE_TRUTH_VALUE)
                )
            )
        )


class TypeParseErrorTest(unittest.TestCase):
    def test_missing_opening_bracket(self):
        with self.assertRaises(LarkError):
            parse_type('e, t>')

    def test_missing_closing_bracket(self):
        with self.assertRaises(LarkError):
            parse_type('<e, t')

    def test_trailing_input(self):
        with self.assertRaises(LarkError):
            parse_type('<e, t> e')

    def test_missing_comma(self):
        with self.assertRaises(LarkError):
            parse_type('<e t>')

    def test_missing_output_type(self):
        with self.assertRaises(LarkError):
            parse_type('<e>')

    def test_invalid_abbreviation(self):
        with self.assertRaises(LarkError):
            parse_type('evt')

    def test_invalid_letter(self):
        with self.assertRaises(LarkError):
            parse_type('b')

    def test_unknown_token(self):
        with self.assertRaises(LarkError):
            parse_type('e?')

    def test_empty_string(self):
        with self.assertRaises(LarkError):
            parse_type('')

    def test_blank(self):
        with self.assertRaises(LarkError):
            parse_type('     \t    \n \r \f')


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
        self.assertEqual(
            str(Lambda('x', And(Var('a'), Var('x')))),
            'Lx.a & x'
        )
        # This formula is semantically invalid but that doesn't matter.
        self.assertEqual(
            str(
                And(
                    Lambda('x', Var('x')),
                    Lambda('y', Var('y'))
                )
            ),
            '[Lx.x] & [Ly.y]'
        )

    def test_call_to_str(self):
        self.assertEqual(
            str(
                Call(
                    Call(Var('P'), And(Var('a'), Var('b'))),
                    Lambda('x', Var('x'))
                )
            ),
            'P(a & b, Lx.x)'
        )
        self.assertEqual(str(Call(Var('P'), Var('x'))), 'P(x)')

    def test_for_all_to_str(self):
        self.assertEqual(
            str(ForAll('x', Call(Var('P'), Var('x')))),
            'Ax.P(x)'
        )

    def test_exists_to_str(self):
        self.assertEqual(
            str(Exists('x', Call(Var('P'), Var('x')))),
            'Ex.P(x)'
        )

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

    def test_nested_exists_and_for_all_to_str(self):
        self.assertEqual(
            str(
                And(
                    ForAll('x', Var('x')),
                    Exists('x', Var('x'))
                )
            ),
            '[Ax.x] & [Ex.x]'
        )

    def test_iota_to_str(self):
        self.assertEqual(str(Iota('x', Var('x'))), 'ix.x')


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
