import unittest

from montague.ast import *
from montague.exceptions import ParseError
from montague.parser import parse_formula, parse_type


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
        self.assertTupleEqual(
            parse_formula('λx.λy.[x & y]'),
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
        self.assertTupleEqual(
            parse_formula('∀x.x & y'),
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
        self.assertTupleEqual(
            parse_formula('∃x.x | y'),
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
        # The actual Unicode iota character may be used.
        self.assertTupleEqual(
            parse_formula('ιx.Man(x)'),
            Iota('x', Call(Var('Man'), Var('x')))
        )


class FormulaParseErrorTest(unittest.TestCase):
    def test_missing_operand(self):
        with self.assertRaises(ParseError):
            parse_formula('a | ')
        with self.assertRaises(ParseError):
            parse_formula('b & ')
        with self.assertRaises(ParseError):
            parse_formula('| a')
        with self.assertRaises(ParseError):
            parse_formula('& b')

    def test_parsing_hanging_bracket(self):
        with self.assertRaises(ParseError):
            parse_formula('[x | y')

    def test_lambda_missing_body(self):
        with self.assertRaises(ParseError):
            parse_formula('Lx.')

    def test_for_all_missing_body(self):
        with self.assertRaises(ParseError):
            parse_formula('Ax.')

    def test_exists_missing_body(self):
        with self.assertRaises(ParseError):
            parse_formula('Ex.')

    def test_iota_missing_body(self):
        with self.assertRaises(ParseError):
            parse_formula('ix.')

    def test_call_with_no_arg(self):
        with self.assertRaises(ParseError):
            parse_formula('Happy()')

    def test_unknown_token(self):
        with self.assertRaises(ParseError):
            parse_formula('Lx.x?')

    def test_empty_string(self):
        with self.assertRaises(ParseError):
            parse_formula('')

    def test_blank(self):
        with self.assertRaises(ParseError):
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

    def test_types_are_AtomicType_class(self):
        typ = parse_type('<et, et>')
        self.assertIsInstance(typ.left.left, AtomicType)
        self.assertIsInstance(typ.left.right, AtomicType)
        self.assertIsInstance(typ.right.left, AtomicType)
        self.assertIsInstance(typ.right.right, AtomicType)

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
        with self.assertRaises(ParseError):
            parse_type('e, t>')

    def test_missing_closing_bracket(self):
        with self.assertRaises(ParseError):
            parse_type('<e, t')

    def test_trailing_input(self):
        with self.assertRaises(ParseError):
            parse_type('<e, t> e')

    def test_missing_comma(self):
        with self.assertRaises(ParseError):
            parse_type('<e t>')

    def test_missing_output_type(self):
        with self.assertRaises(ParseError):
            parse_type('<e>')

    def test_invalid_abbreviation(self):
        with self.assertRaises(ParseError):
            parse_type('evt')

    def test_invalid_letter(self):
        with self.assertRaises(ParseError):
            parse_type('b')

    def test_unknown_token(self):
        with self.assertRaises(ParseError):
            parse_type('e?')

    def test_empty_string(self):
        with self.assertRaises(ParseError):
            parse_type('')

    def test_blank(self):
        with self.assertRaises(ParseError):
            parse_type('     \t    \n \r \f')
