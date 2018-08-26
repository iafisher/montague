"""The parser for type-strings.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: August 2018
"""
import re
from collections import namedtuple
from enum import Enum

from .utils import IteratorWithMemory, expect_token, tokenize


class semtype(Enum):
    ENTITY = 1
    TRUTH_VALUE = 2
    EVENT = 3


TypeNode = namedtuple('TypeNode', ['left', 'right'])


def parse_type(typestring):
    """Parse a type string into a TypeNode or semtype object."""
    tz = IteratorWithMemory(tokenize_type(typestring))
    try:
        tree = match_type(tz)
    except StopIteration:
        raise RuntimeError('premature end of type') from None

    # Make sure there are no trailing tokens in the formula.
    try:
        tkn = next(tz)
    except StopIteration:
        return tree
    else:
        raise RuntimeError(f'trailing tokens in type, line {tkn.line} column'
            f' {tkn.column}') from None


def match_type(tz):
    tkn = expect_token(tz, ('LANGLE', 'ATOM', 'COMPOUND'), '< or atomic type')
    if tkn.typ == 'COMPOUND':
        return TypeNode(
            letter_to_type(tkn.value[0]),
            letter_to_type(tkn.value[1])
        )
    elif tkn.typ == 'LANGLE':
        left = match_type(tz)
        expect_token(tz, ('COMMA',), ',')
        right = match_type(tz)
        expect_token(tz, ('RANGLE',), '>')
        return TypeNode(left, right)
    else:
        return letter_to_type(tkn.value)


def letter_to_type(letter):
    if letter == 'e':
        return semtype.ENTITY
    elif letter == 'v':
        return semtype.EVENT
    elif letter == 't':
        return semtype.TRUTH_VALUE
    else:
        raise RuntimeError(f'invalid type letter "{letter}"')


_TOKENS = [
    ('LANGLE', r'<'),
    ('RANGLE', r'>'),
    ('COMMA', r','),
    ('COMPOUND', r'[evt]{2}'),
    ('ATOM', r'[evt]'),
    ('NEWLINE', r'\n'),
    ('SKIP', r'\s+'),
    ('MISMATCH', r'.'),
]
_TOKEN_REGEX = re.compile('|'.join('(?P<%s>%s)' % p for p in _TOKENS))


def tokenize_type(typestring):
    """Return an iterator over the tokens of the type."""
    return tokenize(typestring, _TOKEN_REGEX)
