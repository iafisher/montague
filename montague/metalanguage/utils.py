"""Utility functions for the various metalanguage parsers.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: August 2018
"""
from collections import namedtuple


Token = namedtuple('Token', ['typ', 'value', 'line', 'column'])


def expect_token(tz, typs, msg):
    tkn = next(tz)
    if tkn.typ not in typs:
        raise RuntimeError(f'expected {msg}, got "{tkn.value}", line {tkn.line}'
            f' column {tkn.column}')
    return tkn


def tokenize(text, token_regex):
    """Return an iterator over the tokens of the string.

    Based on https://docs.python.org/3.6/library/re.html#writing-a-tokenizer
    """
    lineno = 1
    line_start = 0
    for mo in token_regex.finditer(text):
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
