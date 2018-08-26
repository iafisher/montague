"""The parser for the Montague system.

Grammar for formulas:

    formula := e
             | lambda

    e := e AND e
       | e OR e
       | SYMBOL
       | [ e ]
       | lambda
       | call
       | forall
       | exists

    lambda := LAMBDA SYMBOL DOT e

    forall := ALL SYMBOL DOT e

    exists := exists SYMBOL DOT e

    call    := SYMBOL LPAREN [ arglist ] RPAREN
    arglist := arglist COMMA e
             | e

    AND     := the symbol "&"
    OR      := the symbol "|"
    SYMBOL  := a letter followed by zero or more letters, digits, underscores,
               hyphens, and apostrophes. "L" is not a valid symbol as it already
               stands for the lambda operator.

AND binds more tightly than OR.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: August 2018
"""
import re
import unittest
from collections import namedtuple


VarNode = namedtuple('VarNode', 'value')
AndNode = namedtuple('AndNode', ['left', 'right'])
OrNode = namedtuple('OrNode', ['left', 'right'])
LambdaNode = namedtuple('LambdaNode', ['parameter', 'body'])
CallNode = namedtuple('CallNode', ['symbol', 'args'])
AllNode = namedtuple('AllNode', ['symbol', 'body'])
ExistsNode = namedtuple('ExistsNode', ['symbol', 'body'])


def parse_formula(formula):
    """Parse the formula into a tree. Returns an object of one of the Node
    classes. The grammar below is the grammar that the recursive-descent parser
    actually implements. It is equivalent to, though more difficult to read
    than, the grammar in the module docstring.

      formula := e
               | lambda

      e := term { OR term }
         | lambda
         | forall
         | exists

      lambda := LAMBDA SYMBOL DOT e

      forall := ALL SYMBOL DOT e

      exists := exists SYMBOL DOT e

      term   := factor { AND factor }
      factor := SYMBOL call-postfix
              | LBRACKET e RBRACKET
              | call

      call-postfix := LPAREN [ arglist ] RPAREN
                    | <nothing>

      arglist := arglist COMMA e
               | e

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
        tkn = next(tz)
    except StopIteration:
        return tree
    else:
        raise RuntimeError(f'trailing tokens in formula, line {tkn.line} column'
            f' {tkn.column}') from None


def match_e(tz):
    tkn = next(tz)
    tz.push(tkn)
    if tkn.typ == 'LAMBDA':
        return match_lambda(tz)
    elif tkn.typ == 'ALL':
        return match_forall(tz)
    elif tkn.typ == 'EXISTS':
        return match_exists(tz)
    else:
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


def match_lambda(tz):
    expect_token(tz, ('LAMBDA',), 'L')
    tkn = expect_token(tz, ('SYMBOL',), 'symbol')
    parameter = VarNode(tkn.value)
    expect_token(tz, ('DOT',), '.')
    body = match_e(tz)
    return LambdaNode(parameter, body)


def match_forall(tz):
    expect_token(tz, ('ALL',), 'L')
    tkn = expect_token(tz, ('SYMBOL',), 'symbol')
    parameter = VarNode(tkn.value)
    expect_token(tz, ('DOT',), '.')
    body = match_e(tz)
    return AllNode(parameter, body)


def match_exists(tz):
    expect_token(tz, ('EXISTS',), 'L')
    tkn = expect_token(tz, ('SYMBOL',), 'symbol')
    parameter = VarNode(tkn.value)
    expect_token(tz, ('DOT',), '.')
    body = match_e(tz)
    return ExistsNode(parameter, body)


def match_symbol_postfix(tz):
    try:
        tkn = next(tz)
    except StopIteration:
        return None
    if tkn.typ != 'LPAREN':
        tz.push(tkn)
        return None
    args = match_arglist(tz)
    expect_token(tz, ('RPAREN',), ')')
    return args


def match_arglist(tz):
    args = []
    while True:
        tkn = next(tz)
        tz.push(tkn)
        if tkn.typ == 'RPAREN':
            return args
        e = match_e(tz)
        args.append(e)
        tkn = expect_token(tz, ('RPAREN', 'COMMA'), ', or )')
        if tkn.typ == 'RPAREN':
            tz.push(tkn)
            return args
        else:
            continue


def match_term(tz):
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
    tkn = expect_token(tz, ('SYMBOL', 'LBRACKET'), 'symbol')
    if tkn.typ == 'SYMBOL':
        postfix = match_symbol_postfix(tz)
        if postfix is None:
            return VarNode(tkn.value)
        else:
            return CallNode(VarNode(tkn.value), postfix)
    else:
        e = match_e(tz)
        expect_token(tz, 'RBRACKET', ']')
        return e


def expect_token(tz, typs, msg):
    tkn = next(tz)
    if tkn.typ not in typs:
        raise RuntimeError(f'expected {msg}, got {tkn.value}, line {tkn.line}')
    return tkn


Token = namedtuple('Token', ['typ', 'value', 'line', 'column'])
_TOKENS = [
    ('LAMBDA', r'L'),
    ('ALL', r'all\b'),
    ('EXISTS', r'exists\b'),
    ('SYMBOL', r"[A-Za-z][A-Za-z0-9_'-]*"),
    ('AND', r'&'),
    ('OR', r'\|'),
    ('LBRACKET', r'\['),
    ('RBRACKET', r'\]'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('COMMA', r','),
    ('DOT', r'\.'),
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
