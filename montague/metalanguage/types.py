"""The parser for type-strings.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: August 2018
"""
from collections import namedtuple
from enum import Enum

from lark import Lark, Transformer


TypeNode = namedtuple('TypeNode', ['left', 'right'])


class semtype(Enum):
    ENTITY = 1
    TRUTH_VALUE = 2
    EVENT = 3


class TreeToType(Transformer):
    def type(self, matches):
        if len(matches) == 2:
            return TypeNode(matches[0], matches[1])
        else:
            if len(matches[0]) == 2:
                left = letter_to_type[matches[0][0]]
                right = letter_to_type[matches[0][1]]
                return TypeNode(left, right)
            else:
                return letter_to_type[matches[0]]


parser = Lark('''
    ?start: type

    type: "<" type "," type ">"
        | /[evt]/
        | /[evt]{2}/

    %import common.WS
    %ignore WS
''', parser='lalr', transformer=TreeToType())


def parse_type(typestring):
    return parser.parse(typestring)


letter_to_type = {
    'e': semtype.ENTITY,
    'v': semtype.EVENT,
    't': semtype.TRUTH_VALUE
}
