import unittest

from montague.metalanguage.formula import (
    AllNode, AndNode, CallNode, ExistsNode, LambdaNode, OrNode, VarNode,
    parse_formula,
)

from lark.exceptions import LarkError


class ParseTest(unittest.TestCase):
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


class ParseErrorTest(unittest.TestCase):
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
