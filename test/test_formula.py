import unittest

from montague.formula import (
    AllNode, AndNode, CallNode, ExistsNode, IfNode, LambdaNode, OrNode,
    TypeNode, VarNode, parse_formula, parse_type, TYPE_ENTITY, TYPE_EVENT,
    TYPE_TRUTH_VALUE, TYPE_WORLD,
)

from lark.exceptions import LarkError


class FormulaParseTest(unittest.TestCase):
    def test_parsing_symbol(self):
        tree = parse_formula('a')
        self.assertTupleEqual(tree, VarNode('a'))

    def test_parsing_long_symbol(self):
        tree = parse_formula('s8DVY_BUvybJH-VDNS\'JhjS')
        self.assertTupleEqual(tree, VarNode('s8DVY_BUvybJH-VDNS\'JhjS'))

    def test_parsing_conjunction(self):
        tree = parse_formula('a & a\'')
        self.assertTupleEqual(tree, AndNode(VarNode('a'), VarNode('a\'')))

    def test_parsing_multiple_conjunction(self):
        tree = parse_formula('a & b & c')
        self.assertTupleEqual(
            tree,
            AndNode(
                VarNode('a'),
                AndNode(
                    VarNode('b'),
                    VarNode('c')
                )
            )
        )

    def test_parsing_disjunction(self):
        tree = parse_formula('b | b0')
        self.assertTupleEqual(tree, OrNode(VarNode('b'), VarNode('b0')))

    def test_parsing_multi_disjunction(self):
        tree = parse_formula('a | b | c')
        self.assertTupleEqual(
            tree,
            OrNode(
                VarNode('a'),
                OrNode(
                    VarNode('b'),
                    VarNode('c')
                )
            )
        )

    def test_parsing_implication(self):
        tree = parse_formula('a -> b')
        self.assertTupleEqual(tree, IfNode(VarNode('a'), VarNode('b')))

    def test_parsing_multi_implication(self):
        tree = parse_formula('a -> b -> c')
        self.assertTupleEqual(
            tree,
            IfNode(
                VarNode('a'),
                IfNode(
                    VarNode('b'),
                    VarNode('c')
                )
            )
        )

    def test_parsing_precedence(self):
        tree = parse_formula('x & y | z -> m')
        self.assertTupleEqual(
            tree,
            IfNode(
                OrNode(
                    AndNode(VarNode('x'), VarNode('y')),
                    VarNode('z')
                ),
                VarNode('m')
            )
        )

    def test_parsing_precedence2(self):
        tree = parse_formula('x | y -> m & z')
        self.assertTupleEqual(
            tree,
            IfNode(
                OrNode(
                    VarNode('x'),
                    VarNode('y'),
                ),
                AndNode(
                    VarNode('m'),
                    VarNode('z')
                )
            )
        )

    def test_parsing_brackets(self):
        tree = parse_formula('[x | y] & z')
        self.assertTupleEqual(
            tree,
            AndNode(
                OrNode(VarNode('x'), VarNode('y')),
                VarNode('z')
            )
        )

    def test_parsing_lambda(self):
        tree = parse_formula('Lx.Ly.[x & y]')
        self.assertTupleEqual(
            tree,
            LambdaNode(
                'x',
                LambdaNode(
                    'y',
                    AndNode(VarNode('x'), VarNode('y'))
                )
            )
        )

    def test_parsing_lambda2(self):
        tree = parse_formula('L x.L y.[x & y]')
        self.assertEqual(
            tree,
            LambdaNode(
                'x',
                LambdaNode(
                    'y',
                    AndNode(VarNode('x'), VarNode('y'))
                )
            )
        )

    def test_parsing_call(self):
        tree = parse_formula('Happy(x)')
        self.assertTupleEqual(tree, CallNode(VarNode('Happy'), VarNode('x')))

    def test_parsing_call_with_several_args(self):
        tree = parse_formula('Between(x, y & z, [Capital(france)])')
        self.assertTupleEqual(
            tree,
            CallNode(
                CallNode(
                    CallNode(
                        VarNode('Between'),
                        VarNode('x')
                    ),
                    AndNode(VarNode('y'), VarNode('z')),
                ),
                CallNode(VarNode('Capital'), VarNode('france')),
            )
        )

    def test_parsing_call_with_lambda(self):
        tree = parse_formula('(Lx.x)(j)')
        self.assertTupleEqual(
            tree,
            CallNode(
                LambdaNode('x', VarNode('x')),
                VarNode('j')
            )
        )

    def test_parsing_call_with_multiple_lambdas(self):
        tree = parse_formula('((Lx.Ly.x & y) (a)) (b)')
        self.assertTupleEqual(
            tree,
            CallNode(
                CallNode(
                    LambdaNode(
                        'x',
                        LambdaNode('y', AndNode(VarNode('x'), VarNode('y')))
                    ),
                    VarNode('a')
                ),
                VarNode('b')
            )
        )

    def test_parsing_forall(self):
        tree = parse_formula('Ax.x & y')
        self.assertTupleEqual(
            tree,
            AllNode(
                'x',
                AndNode(VarNode('x'), VarNode('y')),
            )
        )

    def test_parsing_forall2(self):
        tree = parse_formula('A x.x & y')
        self.assertTupleEqual(
            tree,
            AllNode(
                'x',
                AndNode(VarNode('x'), VarNode('y')),
            )
        )

    def test_parsing_exists(self):
        tree = parse_formula('Ex.x | y')
        self.assertTupleEqual(
            tree,
            ExistsNode(
                'x',
                OrNode(VarNode('x'), VarNode('y')),
            )
        )

    def test_parsing_exists2(self):
        tree = parse_formula('E x.x | y')
        self.assertTupleEqual(
            tree,
            ExistsNode(
                'x',
                OrNode(VarNode('x'), VarNode('y')),
            )
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

    def test_unknown_token(self):
        with self.assertRaises(LarkError):
            parse_formula('Lx.x?')

    def test_empty_string(self):
        with self.assertRaises(LarkError):
            parse_formula('')


class TypeParseTest(unittest.TestCase):
    def test_parsing_atomic_types(self):
        self.assertEqual(parse_type('e'), TYPE_ENTITY)
        self.assertEqual(parse_type('t'), TYPE_TRUTH_VALUE)
        self.assertEqual(parse_type('v'), TYPE_EVENT)
        self.assertEqual(parse_type('s'), TYPE_WORLD)

    def test_parsing_compound_type(self):
        tree = parse_type('<e, t>')
        self.assertTupleEqual(tree, TypeNode(TYPE_ENTITY, TYPE_TRUTH_VALUE))

    def test_parsing_abbreviated_compound_types(self):
        self.assertTupleEqual(
            parse_type('et'),
            TypeNode(TYPE_ENTITY, TYPE_TRUTH_VALUE)
        )
        self.assertTupleEqual(
            parse_type('vt'),
            TypeNode(TYPE_EVENT, TYPE_TRUTH_VALUE)
        )

    def test_parsing_big_compound_type(self):
        tree = parse_type('<<e, t>, <e, <s, t>>>')
        self.assertTupleEqual(
            tree,
            TypeNode(
                TypeNode(
                    TYPE_ENTITY,
                    TYPE_TRUTH_VALUE
                ),
                TypeNode(
                    TYPE_ENTITY,
                    TypeNode(
                        TYPE_WORLD,
                        TYPE_TRUTH_VALUE
                    )
                )
            )
        )

    def test_parsing_big_compound_type_with_abbreviations(self):
        tree = parse_type('<et, <e, st>>')
        self.assertTupleEqual(
            tree,
            TypeNode(
                TypeNode(
                    TYPE_ENTITY,
                    TYPE_TRUTH_VALUE
                ),
                TypeNode(
                    TYPE_ENTITY,
                    TypeNode(
                        TYPE_WORLD,
                        TYPE_TRUTH_VALUE
                    )
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


class FormulaToStrTest(unittest.TestCase):
    def test_variable_to_str(self):
        self.assertEqual(str(VarNode('a')), 'a')

    def test_and_to_str(self):
        unparsed = str(AndNode(VarNode('a'), VarNode('b')))
        self.assertEqual(unparsed, 'a & b')

    def test_or_to_str(self):
        unparsed = str(OrNode(VarNode('a'), VarNode('b')))
        self.assertEqual(unparsed, 'a | b')

    def test_if_to_str(self):
        unparsed = str(IfNode(VarNode('a'), VarNode('b')))
        self.assertEqual(unparsed, 'a -> b')

    def test_lambda_to_str(self):
        unparsed = str(LambdaNode('x', AndNode(VarNode('a'), VarNode('x'))))
        self.assertEqual(unparsed, 'Lx.a & x')

    def test_call_to_str(self):
        unparsed = str(
            CallNode(
                CallNode(
                    VarNode('P'),
                    AndNode(VarNode('a'), VarNode('b'))
                ),
                LambdaNode('x', VarNode('x'))
            )
        )
        self.assertEqual(unparsed, 'P(a & b, Lx.x)')

    def test_call_with_one_arg_to_str(self):
        unparsed = str(CallNode(VarNode('P'), VarNode('x')))
        self.assertEqual(unparsed, 'P(x)')

    def test_forall_to_str(self):
        unparsed = str(AllNode('x', CallNode(VarNode('P'), VarNode('x'))))
        self.assertEqual(unparsed, 'Ax.P(x)')

    def test_exists_to_str(self):
        unparsed = str(ExistsNode('x', CallNode(VarNode('P'), VarNode('x'))))
        self.assertEqual(unparsed, 'Ex.P(x)')


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
        self.assertEqual(str(TypeNode(TYPE_ENTITY, TYPE_TRUTH_VALUE)), '<e, t>')

    def test_deeply_recursive_type_to_str(self):
        typ = TypeNode(
            TYPE_EVENT,
            TypeNode(
                TypeNode(
                    TYPE_ENTITY,
                    TYPE_TRUTH_VALUE
                ),
                TypeNode(
                    TYPE_ENTITY,
                    TYPE_TRUTH_VALUE
                )
            )
        )
        self.assertEqual(str(typ), '<v, <<e, t>, <e, t>>>')

    def test_recursive_type_to_concise_str(self):
        typ = TypeNode(TYPE_ENTITY, TYPE_TRUTH_VALUE)
        self.assertEqual(typ.concise_str(), 'et')

    def test_deeply_recursive_type_to_concise_str(self):
        typ = TypeNode(
            TYPE_EVENT,
            TypeNode(
                TypeNode(
                    TYPE_ENTITY,
                    TYPE_TRUTH_VALUE
                ),
                TypeNode(
                    TYPE_ENTITY,
                    TYPE_TRUTH_VALUE
                )
            )
        )
        self.assertEqual(typ.concise_str(), '<v, <et, et>>')
