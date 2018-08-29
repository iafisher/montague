import unittest

from montague.formula import (
    AllNode, AndNode, CallNode, ExistsNode, LambdaNode, OrNode, TypeNode,
    VarNode, parse_formula, parse_type, TYPE_ENTITY, TYPE_EVENT,
    TYPE_TRUTH_VALUE, unparse_formula, unparse_type,
)

from lark.exceptions import LarkError


class FormulaParseTest(unittest.TestCase):
    def test_parsing_symbol(self):
        tree = parse_formula('a')
        self.assertEqual(tree, VarNode('a'))

    def test_parsing_long_symbol(self):
        tree = parse_formula('s8DVY_BUvybJH-VDNS\'JhjS')
        self.assertEqual(tree, VarNode('s8DVY_BUvybJH-VDNS\'JhjS'))

    def test_parsing_conjunction(self):
        tree = parse_formula('a & a\'')
        self.assertEqual(tree, AndNode(VarNode('a'), VarNode('a\'')))

    def test_parsing_disjunction(self):
        tree = parse_formula('b | b0')
        self.assertEqual(tree, OrNode(VarNode('b'), VarNode('b0')))

    def test_parsing_precedence(self):
        tree = parse_formula('x & y | z')
        self.assertEqual(tree, OrNode(
            AndNode(VarNode('x'), VarNode('y')),
            VarNode('z')
        ))

    def test_parsing_precedence2(self):
        tree = parse_formula('x | y & z')
        self.assertEqual(tree, OrNode(
            VarNode('x'),
            AndNode(VarNode('y'), VarNode('z'))
        ))

    def test_parsing_brackets(self):
        tree = parse_formula('[x | y] & z')
        self.assertEqual(tree, AndNode(
            OrNode(VarNode('x'), VarNode('y')),
            VarNode('z')
        ))

    def test_parsing_lambda(self):
        tree = parse_formula('Lx.Ly.[x & y]')
        self.assertEqual(tree, LambdaNode('x',
            LambdaNode('y',
                AndNode(VarNode('x'), VarNode('y'))
            )
        ))

    def test_parsing_lambda2(self):
        tree = parse_formula('L x.L y.[x & y]')
        self.assertEqual(tree, LambdaNode('x',
            LambdaNode('y',
                AndNode(VarNode('x'), VarNode('y'))
            )
        ))

    def test_parsing_call(self):
        tree = parse_formula('Happy(x)')
        self.assertEqual(tree, CallNode('Happy', [VarNode('x')]))

    def test_parsing_call_with_no_args(self):
        tree = parse_formula('Happy()')
        self.assertEqual(tree, CallNode('Happy', []))

    def test_parsing_call_with_several_args(self):
        tree = parse_formula('Between(x, y & z, [Capital(france)])')
        self.assertEqual(tree, CallNode(
            'Between',
            [
                VarNode('x'),
                AndNode(VarNode('y'), VarNode('z')),
                CallNode('Capital', [VarNode('france')]),
            ]
        ))

    def test_parsing_forall(self):
        tree = parse_formula('Ax.x & y')
        self.assertEqual(tree, AllNode(
            'x',
            AndNode(VarNode('x'), VarNode('y')),
        ))

    def test_parsing_forall2(self):
        tree = parse_formula('A x.x & y')
        self.assertEqual(tree, AllNode(
            'x',
            AndNode(VarNode('x'), VarNode('y')),
        ))

    def test_parsing_exists(self):
        tree = parse_formula('Ex.x | y')
        self.assertEqual(tree, ExistsNode(
            'x',
            OrNode(VarNode('x'), VarNode('y')),
        ))

    def test_parsing_exists2(self):
        tree = parse_formula('E x.x | y')
        self.assertEqual(tree, ExistsNode(
            'x',
            OrNode(VarNode('x'), VarNode('y')),
        ))


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
        tree = parse_type('e')
        self.assertEqual(tree, TYPE_ENTITY)
        tree = parse_type('t')
        self.assertEqual(tree, TYPE_TRUTH_VALUE)
        tree = parse_type('v')
        self.assertEqual(tree, TYPE_EVENT)

    def test_parsing_compound_type(self):
        tree = parse_type('<e, t>')
        self.assertEqual(tree, TypeNode(TYPE_ENTITY, TYPE_TRUTH_VALUE))

    def test_parsing_abbreviated_compound_types(self):
        tree = parse_type('et')
        self.assertEqual(tree, TypeNode(TYPE_ENTITY, TYPE_TRUTH_VALUE))
        tree = parse_type('vt')
        self.assertEqual(tree, TypeNode(TYPE_EVENT, TYPE_TRUTH_VALUE))

    def test_parsing_big_compound_type(self):
        tree = parse_type('<<e, t>, <e, <e, t>>>')
        self.assertEqual(tree, TypeNode(
            TypeNode(
                TYPE_ENTITY,
                TYPE_TRUTH_VALUE
            ),
            TypeNode(
                TYPE_ENTITY,
                TypeNode(
                    TYPE_ENTITY,
                    TYPE_TRUTH_VALUE
                )
            )
        ))

    def test_parsing_big_compound_type_with_abbreviations(self):
        tree = parse_type('<et, <e, et>>')
        self.assertEqual(tree, TypeNode(
            TypeNode(
                TYPE_ENTITY,
                TYPE_TRUTH_VALUE
            ),
            TypeNode(
                TYPE_ENTITY,
                TypeNode(
                    TYPE_ENTITY,
                    TYPE_TRUTH_VALUE
                )
            )
        ))


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


class UnparseFormulaTest(unittest.TestCase):
    def test_unparse_variable(self):
        unparsed = unparse_formula(VarNode('a'))
        self.assertEqual(unparsed, 'a')

    def test_unparse_and(self):
        unparsed = unparse_formula(AndNode(VarNode('a'), VarNode('b')))
        self.assertEqual(unparsed, 'a & b')

    def test_unparse_or(self):
        unparsed = unparse_formula(OrNode(VarNode('a'), VarNode('b')))
        self.assertEqual(unparsed, 'a | b')

    def test_unparse_lambda(self):
        unparsed = unparse_formula(LambdaNode('x',
            AndNode(VarNode('a'), VarNode('x'))
        ))
        self.assertEqual(unparsed, 'Lx.a & x')

    def test_unparse_call(self):
        unparsed = unparse_formula(CallNode('P', [
            AndNode(VarNode('a'), VarNode('b')),
            LambdaNode('x', VarNode('x'))
        ]))
        self.assertEqual(unparsed, 'P(a & b, Lx.x)')

    def test_unparse_call_no_args(self):
        unparsed = unparse_formula(CallNode('P', []))
        self.assertEqual(unparsed, 'P()')

    def test_unparse_call_one_arg(self):
        unparsed = unparse_formula(CallNode('P', [VarNode('x')]))
        self.assertEqual(unparsed, 'P(x)')

    def test_unparse_forall(self):
        unparsed = unparse_formula(AllNode('x', CallNode('P', [VarNode('x')])))
        self.assertEqual(unparsed, 'Ax.P(x)')

    def test_unparse_exists(self):
        unparsed = unparse_formula(ExistsNode('x',
            CallNode('P', [VarNode('x')]))
        )
        self.assertEqual(unparsed, 'Ex.P(x)')


class UnparseTypeTest(unittest.TestCase):
    def test_unparse_entity(self):
        unparsed = unparse_type(TYPE_ENTITY)
        self.assertEqual(unparsed, 'e')

    def test_unparse_event(self):
        unparsed = unparse_type(TYPE_EVENT)
        self.assertEqual(unparsed, 'v')

    def test_unparse_truth(self):
        unparsed = unparse_type(TYPE_TRUTH_VALUE)
        self.assertEqual(unparsed, 't')

    def test_unparse_recursive_type(self):
        unparsed = unparse_type(TypeNode(
            TYPE_ENTITY,
            TYPE_TRUTH_VALUE
        ))
        self.assertEqual(unparsed, '<e, t>')

    def test_unparse_deeply_recursive_type(self):
        unparsed = unparse_type(TypeNode(
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
        ))
        self.assertEqual(unparsed, '<v, <<e, t>, <e, t>>>')

    def test_concisely_unparse_atomic_types(self):
        self.assertEqual(unparse_type(TYPE_ENTITY, concise=True), 'e')
        self.assertEqual(unparse_type(TYPE_EVENT, concise=True), 'v')
        self.assertEqual(unparse_type(TYPE_TRUTH_VALUE, concise=True), 't')

    def test_concisely_unparse_recursive_type(self):
        unparsed = unparse_type(TypeNode(
            TYPE_ENTITY,
            TYPE_TRUTH_VALUE
        ), concise=True)
        self.assertEqual(unparsed, 'et')

    def test_concisely_unparse_deeply_recursive_type(self):
        unparsed = unparse_type(TypeNode(
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
        ), concise=True)
        self.assertEqual(unparsed, '<v, <et, et>>')
