"""The parser for Montague's logical representation language, including type
expressions.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: August 2018
"""
from collections import namedtuple
from enum import Enum

from lark import Lark, Transformer


VarNode = namedtuple('VarNode', 'value')
AndNode = namedtuple('AndNode', ['left', 'right'])
OrNode = namedtuple('OrNode', ['left', 'right'])
IfNode = namedtuple('IfNode', ['left', 'right'])
LambdaNode = namedtuple('LambdaNode', ['parameter', 'body'])
CallNode = namedtuple('CallNode', ['symbol', 'args'])
AllNode = namedtuple('AllNode', ['symbol', 'body'])
ExistsNode = namedtuple('ExistsNode', ['symbol', 'body'])


class TreeToFormula(Transformer):
    def expr(self, matches):
        return IfNode(matches[0], matches[2])

    def ifterm(self, matches):
        return OrNode(matches[0], matches[2])

    def term(self, matches):
        return AndNode(matches[0], matches[2])

    def variable(self, matches):
        return VarNode(matches[0])

    def lambda_(self, matches):
        return LambdaNode(matches[0], matches[1])

    def forall(self, matches):
        return AllNode(matches[0], matches[1])

    def exists(self, matches):
        return ExistsNode(matches[0], matches[1])

    def call(self, matches):
        return CallNode(VarNode(matches[0]), matches[1:])


formula_parser = Lark('''
    ?start: expr

    ?expr: ifterm | ifterm IMPLIES expr

    ?ifterm: term | term OR ifterm
    ?term: factor | factor AND term
    ?factor: variable | "[" expr "]" | call | lambda_ | forall | exists

    call: SYMBOL "(" _arglist? ")"
    _arglist: ( expr "," )* expr

    lambda_: "L" SYMBOL "." expr
    forall: "A" SYMBOL "." expr
    exists: "E" SYMBOL "." expr

    variable: SYMBOL

    SYMBOL: /[B-DF-KM-Za-z][A-Za-z0-9_'-]*/
    OR: "|"
    AND: "&"
    IMPLIES: "->"

    %import common.WS
    %ignore WS
''', parser='lalr', transformer=TreeToFormula())


def parse_formula(formula):
    return formula_parser.parse(formula)


TypeNode = namedtuple('TypeNode', ['left', 'right'])


TYPE_ENTITY = 'e'
TYPE_TRUTH_VALUE = 't'
TYPE_EVENT = 'v'


class TreeToType(Transformer):
    def type(self, matches):
        if len(matches) == 2:
            return TypeNode(matches[0], matches[1])
        else:
            if len(matches[0]) == 2:
                return TypeNode(matches[0][0], matches[0][1])
            else:
                return matches[0]


type_parser = Lark('''
    ?start: type

    type: "<" type "," type ">"
        | /[evt]{1,2}/

    %import common.WS
    %ignore WS
''', parser='lalr', transformer=TreeToType())


def parse_type(typestring):
    return type_parser.parse(typestring)


def unparse_formula(tree):
    if isinstance(tree, ExistsNode):
        return f'E{tree.symbol}.{unparse_formula(tree.body)}'
    elif isinstance(tree, AllNode):
        return f'A{tree.symbol}.{unparse_formula(tree.body)}'
    elif isinstance(tree, LambdaNode):
        return f'L{tree.parameter}.{unparse_formula(tree.body)}'
    elif isinstance(tree, CallNode):
        args = ', '.join(map(unparse_formula, tree.args))
        return f'{unparse_formula(tree.symbol)}({args})'
    elif isinstance(tree, OrNode):
        return f'{unparse_formula(tree.left)} | {unparse_formula(tree.right)}'
    elif isinstance(tree, AndNode):
        return f'{unparse_formula(tree.left)} & {unparse_formula(tree.right)}'
    elif isinstance(tree, IfNode):
        return f'{unparse_formula(tree.left)} -> {unparse_formula(tree.right)}'
    else:
        return tree.value


def unparse_type(tree, *, concise=False):
    if isinstance(tree, TypeNode):
        if concise and not isinstance(tree.left, TypeNode) \
            and not isinstance(tree.right, TypeNode):
            return tree.left + tree.right
        else:
            left = unparse_type(tree.left, concise=concise)
            right = unparse_type(tree.right, concise=concise)
            return f'<{left}, {right}>'
    else:
        return tree
