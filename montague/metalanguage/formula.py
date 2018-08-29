"""The parser for Montague's logical metalanguage.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: August 2018
"""
from collections import namedtuple

from lark import Lark, Transformer


VarNode = namedtuple('VarNode', 'value')
AndNode = namedtuple('AndNode', ['left', 'right'])
OrNode = namedtuple('OrNode', ['left', 'right'])
LambdaNode = namedtuple('LambdaNode', ['parameter', 'body'])
CallNode = namedtuple('CallNode', ['symbol', 'args'])
AllNode = namedtuple('AllNode', ['symbol', 'body'])
ExistsNode = namedtuple('ExistsNode', ['symbol', 'body'])


class TreeToFormula(Transformer):
    def expr(self, matches):
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
        return CallNode(matches[0], matches[1:])


parser = Lark('''
    ?start: expr

    ?expr: term ( OR term )*

    ?term: factor ( AND factor )*
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

    %import common.WS
    %ignore WS
''', parser='lalr', transformer=TreeToFormula())


def parse_formula(formula):
    return parser.parse(formula)
