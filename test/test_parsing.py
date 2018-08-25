import unittest

from montague.parsing import (
    AndNode, CallNode, IteratorWithMemory, LambdaNode, OrNode, VarNode,
    parse_formula, tokenize,
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
        tz = tokenize('a')
        tkn = next(tz)
        self.assertEqual(tkn.typ, 'SYMBOL')
        self.assertEqual(tkn.value, 'a')
        self.assertEqual(tkn.line, 1)
        self.assertEqual(tkn.column, 0)

        with self.assertRaises(StopIteration):
            next(tz)

    def test_tokenize_multiple_symbols(self):
        tokens = list(tokenize("a' b0 cccc"))
        self.assertEqual(len(tokens), 3)

        self.assertEqual(tokens[0].typ, 'SYMBOL')
        self.assertEqual(tokens[0].value, "a'")
        self.assertEqual(tokens[0].line, 1)
        self.assertEqual(tokens[0].column, 0)

        self.assertEqual(tokens[1].typ, 'SYMBOL')
        self.assertEqual(tokens[1].value, 'b0')
        self.assertEqual(tokens[1].line, 1)
        self.assertEqual(tokens[1].column, 3)

        self.assertEqual(tokens[2].typ, 'SYMBOL')
        self.assertEqual(tokens[2].value, 'cccc')
        self.assertEqual(tokens[2].line, 1)
        self.assertEqual(tokens[2].column, 6)

    def test_tokenize_conjunction(self):
        tokens = list(tokenize('a&b'))
        self.assertEqual(len(tokens), 3)

        self.assertEqual(tokens[0].typ, 'SYMBOL')
        self.assertEqual(tokens[0].value, 'a')
        self.assertEqual(tokens[1].typ, 'AND')
        self.assertEqual(tokens[1].value, '&')
        self.assertEqual(tokens[2].typ, 'SYMBOL')
        self.assertEqual(tokens[2].value, 'b')

    def test_tokenize_disjunction(self):
        tokens = list(tokenize('a|b'))
        self.assertEqual(len(tokens), 3)

        self.assertEqual(tokens[0].typ, 'SYMBOL')
        self.assertEqual(tokens[0].value, 'a')
        self.assertEqual(tokens[1].typ, 'OR')
        self.assertEqual(tokens[1].value, '|')
        self.assertEqual(tokens[2].typ, 'SYMBOL')
        self.assertEqual(tokens[2].value, 'b')

    def test_tokenize_brackets(self):
        tokens = list(tokenize('[a]'))
        self.assertEqual(len(tokens), 3)

        self.assertEqual(tokens[0].typ, 'LBRACKET')
        self.assertEqual(tokens[0].value, '[')
        self.assertEqual(tokens[2].typ, 'RBRACKET')
        self.assertEqual(tokens[2].value, ']')

    def test_tokenize_lambda_op(self):
        tokens = list(tokenize('L'))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].typ, 'LAMBDA')
        self.assertEqual(tokens[0].value, 'L')

    def test_tokenize_lambda(self):
        tokens = list(tokenize('Lx.x'))
        self.assertEqual(len(tokens), 4)

        self.assertEqual(tokens[0].typ, 'LAMBDA')
        self.assertEqual(tokens[0].value, 'L')
        self.assertEqual(tokens[1].typ, 'SYMBOL')
        self.assertEqual(tokens[1].value, 'x')
        self.assertEqual(tokens[2].typ, 'DOT')
        self.assertEqual(tokens[2].value, '.')
        self.assertEqual(tokens[3].typ, 'SYMBOL')
        self.assertEqual(tokens[3].value, 'x')

    def test_tokenize_parentheses(self):
        tokens = list(tokenize('()'))
        self.assertEqual(len(tokens), 2)

        self.assertEqual(tokens[0].typ, 'LPAREN')
        self.assertEqual(tokens[0].value, '(')
        self.assertEqual(tokens[1].typ, 'RPAREN')
        self.assertEqual(tokens[1].value, ')')

    def test_tokenize_comma(self):
        tokens = list(tokenize('a,b'))
        self.assertEqual(len(tokens), 3)

        self.assertEqual(tokens[0].typ, 'SYMBOL')
        self.assertEqual(tokens[2].typ, 'SYMBOL')
        self.assertEqual(tokens[1].typ, 'COMMA')
        self.assertEqual(tokens[1].value, ',')


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
        self.assertEqual(tree.parameter.value, 'x')
        self.assertIsInstance(tree.body, LambdaNode)
        self.assertEqual(tree.body.parameter.value, 'y')
        self.assertIsInstance(tree.body.body, AndNode)
        self.assertEqual(tree.body.body.left.value, 'x')
        self.assertEqual(tree.body.body.right.value, 'y')

    def test_parsing_call(self):
        tree = parse_formula('Happy(x)')
        self.assertIsInstance(tree, CallNode)
        self.assertEqual(tree.symbol.value, 'Happy')
        self.assertEqual(len(tree.args), 1)
        self.assertEqual(tree.args[0].value, 'x')

    def test_parsing_call_with_no_args(self):
        tree = parse_formula('Happy()')
        self.assertIsInstance(tree, CallNode)
        self.assertEqual(tree.symbol.value, 'Happy')
        self.assertEqual(len(tree.args), 0)

    def test_parsing_call_with_several_args(self):
        tree = parse_formula('Between(x, y & z, [Capital(france)])')
        self.assertIsInstance(tree, CallNode)
        self.assertEqual(tree.symbol.value, 'Between')
        self.assertEqual(len(tree.args), 3)
        self.assertIsInstance(tree.args[0], VarNode)
        self.assertIsInstance(tree.args[1], AndNode)
        self.assertIsInstance(tree.args[2], CallNode)


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
