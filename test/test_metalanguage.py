import unittest

from montague.metalanguage import (
    AllNode, AndNode, CallNode, ExistsNode, IteratorWithMemory, LambdaNode,
    OrNode, Token, VarNode, parse_formula, tokenize,
)


class IteratorWithMemoryTest(unittest.TestCase):
    def test_next_and_push(self):
        L = [1, 2, 3]
        it = IteratorWithMemory(iter(L))
        self.assertEqual(1, next(it))
        it.push(7)
        self.assertEqual(7, next(it))
        self.assertEqual(2, next(it))


class TokenizeTest(unittest.TestCase):
    def test_tokenize_symbol(self):
        tokens = list(tokenize('a'))
        self.assertListEqual(tokens, [
            Token('SYMBOL', 'a', 1, 0),
        ])

    def test_tokenize_multiple_symbols(self):
        tokens = list(tokenize("a' b0 cccc"))
        self.assertListEqual(tokens, [
            Token('SYMBOL', 'a\'', 1, 0),
            Token('SYMBOL', 'b0', 1, 3),
            Token('SYMBOL', 'cccc', 1, 6),
        ])

    def test_tokenize_conjunction(self):
        tokens = list(tokenize('a&b'))
        self.assertListEqual(tokens, [
            Token('SYMBOL', 'a', 1, 0),
            Token('AND', '&', 1, 1),
            Token('SYMBOL', 'b', 1, 2),
        ])

    def test_tokenize_disjunction(self):
        tokens = list(tokenize('a|b'))
        self.assertListEqual(tokens, [
            Token('SYMBOL', 'a', 1, 0),
            Token('OR', '|', 1, 1),
            Token('SYMBOL', 'b', 1, 2),
        ])

    def test_tokenize_brackets(self):
        tokens = list(tokenize('[a]'))
        self.assertListEqual(tokens, [
            Token('LBRACKET', '[', 1, 0),
            Token('SYMBOL', 'a', 1, 1),
            Token('RBRACKET', ']', 1, 2),
        ])

    def test_tokenize_lambda_op(self):
        tokens = list(tokenize('L'))
        self.assertListEqual(tokens, [
            Token('LAMBDA', 'L', 1, 0),
        ])

    def test_tokenize_lambda(self):
        tokens = list(tokenize('Lx.x'))
        self.assertListEqual(tokens, [
            Token('LAMBDA', 'L', 1, 0),
            Token('SYMBOL', 'x', 1, 1),
            Token('DOT', '.', 1, 2),
            Token('SYMBOL', 'x', 1, 3),
        ])

    def test_tokenize_parentheses(self):
        tokens = list(tokenize('()'))
        self.assertListEqual(tokens, [
            Token('LPAREN', '(', 1, 0),
            Token('RPAREN', ')', 1, 1),
        ])

    def test_tokenize_comma(self):
        tokens = list(tokenize('a,b'))
        self.assertListEqual(tokens, [
            Token('SYMBOL', 'a', 1, 0),
            Token('COMMA', ',', 1, 1),
            Token('SYMBOL', 'b', 1, 2),
        ])

    def test_tokenize_keywords(self):
        tokens = list(tokenize('all exists'))
        self.assertListEqual(tokens, [
            Token('ALL', 'all', 1, 0),
            Token('EXISTS', 'exists', 1, 4),
        ])

    def test_tokenize_almost_keywords(self):
        tokens = list(tokenize('all_ exists_'))
        self.assertListEqual(tokens, [
            Token('SYMBOL', 'all_', 1, 0),
            Token('SYMBOL', 'exists_', 1, 5),
        ])


class ParseTest(unittest.TestCase):
    def test_parsing_symbol(self):
        tree = parse_formula('a')
        self.assertIsInstance(tree, VarNode)
        self.assertEqual(tree.value, 'a')

    def test_parsing_another_symbol(self):
        tree = parse_formula("s8DVY_BUvybJH-VDNS'JhjS")
        self.assertIsInstance(tree, VarNode)
        self.assertEqual(tree.value, "s8DVY_BUvybJH-VDNS'JhjS")

    def test_parsing_conjunction(self):
        tree = parse_formula("a & a'")
        self.assertIsInstance(tree, AndNode)
        left = tree.left
        self.assertIsInstance(left, VarNode)
        self.assertEqual(left.value, 'a')
        right = tree.right
        self.assertIsInstance(right, VarNode)
        self.assertEqual(right.value, "a'")

    def test_parsing_disjunction(self):
        tree = parse_formula("b | b0")
        self.assertIsInstance(tree, OrNode)
        left = tree.left
        self.assertIsInstance(left, VarNode)
        self.assertEqual(left.value, 'b')
        right = tree.right
        self.assertIsInstance(right, VarNode)
        self.assertEqual(right.value, "b0")

    def test_parsing_precedence(self):
        tree = parse_formula('x & y | z')
        self.assertIsInstance(tree, OrNode)
        self.assertIsInstance(tree.left, AndNode)
        self.assertEqual(tree.left.left.value, 'x')
        self.assertEqual(tree.left.right.value, 'y')
        self.assertIsInstance(tree.right, VarNode)
        self.assertEqual(tree.right.value, 'z')

    def test_parsing_precedence2(self):
        tree = parse_formula('x | y & z')
        self.assertIsInstance(tree, OrNode)
        self.assertIsInstance(tree.left, VarNode)
        self.assertEqual(tree.left.value, 'x')
        self.assertIsInstance(tree.right, AndNode)
        self.assertEqual(tree.right.left.value, 'y')
        self.assertEqual(tree.right.right.value, 'z')

    def test_parsing_brackets(self):
        tree = parse_formula('[x | y] & z')
        self.assertIsInstance(tree, AndNode)
        self.assertIsInstance(tree.left, OrNode)
        self.assertEqual(tree.left.left.value, 'x')
        self.assertEqual(tree.left.right.value, 'y')
        self.assertIsInstance(tree.right, VarNode)
        self.assertEqual(tree.right.value, 'z')

    def test_parsing_lambda(self):
        tree = parse_formula('Lx.Ly.[x & y]')
        self.assertIsInstance(tree, LambdaNode)
        self.assertEqual(tree.parameter, 'x')
        self.assertIsInstance(tree.body, LambdaNode)
        self.assertEqual(tree.body.parameter, 'y')
        self.assertIsInstance(tree.body.body, AndNode)
        self.assertEqual(tree.body.body.left.value, 'x')
        self.assertEqual(tree.body.body.right.value, 'y')

    def test_parsing_call(self):
        tree = parse_formula('Happy(x)')
        self.assertIsInstance(tree, CallNode)
        self.assertEqual(tree.symbol, 'Happy')
        self.assertEqual(len(tree.args), 1)
        self.assertEqual(tree.args[0].value, 'x')

    def test_parsing_call_with_no_args(self):
        tree = parse_formula('Happy()')
        self.assertIsInstance(tree, CallNode)
        self.assertEqual(tree.symbol, 'Happy')
        self.assertEqual(len(tree.args), 0)

    def test_parsing_call_with_several_args(self):
        tree = parse_formula('Between(x, y & z, [Capital(france)])')
        self.assertIsInstance(tree, CallNode)
        self.assertEqual(tree.symbol, 'Between')
        self.assertEqual(len(tree.args), 3)
        self.assertIsInstance(tree.args[0], VarNode)
        self.assertIsInstance(tree.args[1], AndNode)
        self.assertIsInstance(tree.args[2], CallNode)

    def test_parsing_forall(self):
        tree = parse_formula('all x.x & y')
        self.assertIsInstance(tree, AllNode)
        self.assertEqual(tree.symbol, 'x')
        self.assertIsInstance(tree.body, AndNode)

    def test_parsing_exists(self):
        tree = parse_formula('exists x.x | y')
        self.assertIsInstance(tree, ExistsNode)
        self.assertEqual(tree.symbol, 'x')
        self.assertIsInstance(tree.body, OrNode)


class ParseErrorTest(unittest.TestCase):
    def test_missing_operand(self):
        with self.assertRaises(RuntimeError):
            parse_formula('a | ')
        with self.assertRaises(RuntimeError):
            parse_formula('b & ')
        with self.assertRaises(RuntimeError):
            parse_formula('| a')
        with self.assertRaises(RuntimeError):
            parse_formula('& b')

    def test_parsing_hanging_bracket(self):
        with self.assertRaises(RuntimeError):
            parse_formula('[x | y')

    def test_lambda_missing_body(self):
        with self.assertRaises(RuntimeError):
            parse_formula('Lx.')
