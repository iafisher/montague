"""A natural-language understanding system.

Grammar for formulas:

    formula := e

    e := e AND e | e OR e | ID

    AND := the symbol "&"
    OR  := the symbol "|"
    ID  := a letter followed by zero or more letters, digits, underscores,
           hyphens, and apostrophes

AND binds more tightly than OR.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: August 2018
"""
import re
import sys
import unittest
from collections import namedtuple


VarNode = namedtuple('VarNode', 'value')
AndNode = namedtuple('AndNode', ['left', 'right'])
OrNode = namedtuple('OrNode', ['left', 'right'])


def parse_formula(formula):
    """Parse the formula into a tree. Returns an object of one of the Node
    classes. The grammar below is the grammar that the recursive-descent parser
    actually implements. It is equivalent to, though more difficult to read,
    than the grammar in the module docstring.

      formula := e

      e      := term { OR term }
      term   := factor { AND factor }
      factor := ID

    For the definition of the tokens, see the _TOKENS global variable in this
    module.
    """
    tz = IteratorWithMemory(tokenize(formula))
    try:
        tree = match_e(tz)
    except StopIteration:
        raise RuntimeError('premature end of formula') from None

    # Make sure there are no trailing tokens in the formula.
    try:
        next(tz)
    except StopIteration:
        return tree
    else:
        raise RuntimeError('trailing tokens in formula') from None


def match_e(tz):
    """  e := term { OR term }  """
    left_term = match_term(tz)
    try:
        tkn = next(tz)
    except StopIteration:
        return left_term
    else:
        if tkn.typ == 'OR':
            right_term = match_term(tz)
            return OrNode(left_term, right_term)
        else:
            tz.push(tkn)
            return left_term


def match_term(tz):
    """  term := factor { AND factor }  """
    left_factor = match_factor(tz)
    try:
        tkn = next(tz)
    except StopIteration:
        return left_factor
    else:
        if tkn.typ == 'AND':
            right_factor = match_factor(tz)
            return AndNode(left_factor, right_factor)
        else:
            tz.push(tkn)
            return left_factor


def match_factor(tz):
    """  factor := SYMBOL  """
    tkn = next(tz)
    if tkn.typ == 'SYMBOL':
        return VarNode(tkn.value)
    else:
        raise RuntimeError(f'expected symbol, got {tkn.value}, line {tkn.line}')


Token = namedtuple('Token', ['typ', 'value', 'line', 'column'])
_TOKENS = [
    ('SYMBOL', r"[A-Za-z][A-Za-z0-9_'-]*"),
    ('AND', r'&'),
    ('OR', r'\|'),
    ('NEWLINE', r'\n'),
    ('SKIP', r'\s+'),
    ('MISMATCH', r'.'),
]
_TOKEN_REGEX = re.compile('|'.join('(?P<%s>%s)' % p for p in _TOKENS))


def tokenize(formula):
    """Return an iterator over the tokens of the formula.

    Based on https://docs.python.org/3.6/library/re.html#writing-a-tokenizer
    """
    lineno = 1
    line_start = 0
    for mo in _TOKEN_REGEX.finditer(formula):
        kind = mo.lastgroup
        value = mo.group(kind)
        if kind == 'NEWLINE':
            line_start = mo.end()
            line_num += 1
        elif kind == 'SKIP':
            pass
        elif kind == 'MISMATCH':
            raise RuntimeError(f'{value!r} not expected on line {lineno}')
        else:
            column = mo.start() - line_start
            yield Token(kind, value, lineno, column)


class IteratorWithMemory:
    """A wrapper for any iterator that implements a push method to remember a
    single value and return it on the subsequent call to __next__.
    """

    def __init__(self, iterator):
        self.iterator = iterator
        self.memory = None

    def __iter__(self):
        return self

    def __next__(self):
        if self.memory is not None:
            ret = self.memory
            self.memory = None
            return ret
        else:
            return next(self.iterator)

    def push(self, val):
        self.memory = val


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
        left = tree.left
        self.assertIsInstance(left, AndNode)
        self.assertEqual(left.left.value, 'x')
        self.assertEqual(left.right.value, 'y')
        right = tree.right
        self.assertIsInstance(right, VarNode)
        self.assertEqual(right.value, 'z')


if __name__ == '__main__':
    if len(sys.argv) >= 2 and 'test' in sys.argv:
        unittest.main(argv=sys.argv[:1])
    else:
        print('Enter a formula to see its parse tree. Press Ctrl+C to quit.\n')
        while True:
            try:
                formula = input('>>> ')
            except (EOFError, KeyboardInterrupt):
                print()
                break

            print(parse_formula(formula))
