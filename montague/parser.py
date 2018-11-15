"""The parser for Montague's logical representation language, including type
expressions.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: September 2018
"""
from collections import namedtuple

from lark import Lark, Transformer
from lark.exceptions import LarkError

from .ast import *
from .exceptions import ParseError


class TreeToFormula(Transformer):
    """Transform Lark's parse tree into a formula tree with Formula objects."""

    def expr(self, matches):
        if matches[1] == '->':
            return IfThen(matches[0], matches[2])
        elif matches[1] == '<->':
            return IfAndOnlyIf(matches[0], matches[2])
        else:
            raise NotImplementedError

    def ifterm(self, matches):
        return Or(matches[0], matches[2])

    def term(self, matches):
        return And(matches[0], matches[2])

    def variable(self, matches):
        return Var(matches[0])

    def lambda_(self, matches):
        return Lambda(matches[1], matches[2])

    def forall(self, matches):
        return ForAll(matches[1], matches[2])

    def exists(self, matches):
        return Exists(matches[1], matches[2])

    def call(self, matches):
        # The parse tree allows n-ary functions but the AST only allows unary
        # functions. This methods converts the former to the latter, e.g.
        # F(x, y, z) becomes F(x)(y)(z), three nested CallNodes.
        func = Call(matches[0], matches[1])
        for i in range(2, len(matches)):
            func = Call(func, matches[i])
        return func

    def iota(self, matches):
        return Iota(matches[1], matches[2])

    def not_e(self, matches):
        return Not(matches[1])


# The grammar of the logical language.
formula_parser = Lark(
    '''
    ?start: expr

    ?expr: ifterm | ifterm IMPLIES expr | ifterm IFF expr

    ?ifterm: term | term OR ifterm
    ?term: factor | factor AND term
    ?factor: variable
           | "[" expr "]"
           | call
           | lambda_
           | forall
           | exists
           | iota
           | NOT factor  -> not_e

    call: variable "(" _arglist ")" | "(" expr ")" "(" _arglist ")"
    _arglist: ( expr "," )* expr

    lambda_: LAMBDA SYMBOL "." expr
    forall: FORALL SYMBOL "." expr
    exists: EXISTS SYMBOL "." expr
    iota: IOTA SYMBOL "." expr

    variable: SYMBOL

    SYMBOL: /[B-DF-KM-Za-hj-z][A-Za-z0-9_'-]*/
    OR: "|"
    AND: "&"
    IMPLIES: "->"
    IFF: "<->"
    NOT: "~"

    LAMBDA: "L" | "λ"
    FORALL: "A" | "∀"
    EXISTS: "E" | "∃"
    IOTA: "i" | "ι"

    %import common.WS
    %ignore WS
''',
    parser='lalr',
    transformer=TreeToFormula(),
)


def parse_formula(formula):
    """Parse `formula`, a string, into a tree of Formula objects.

    If the string cannot be parsed, a montague.exceptions.ParseError is raised.
    """
    try:
        return formula_parser.parse(formula)
    except LarkError as e:
        raise ParseError(str(e)) from None


class TreeToType(Transformer):
    """Transform Lark's parse tree into a type tree with ComplexType and
    AtomicType objects.
    """

    def type(self, matches):
        if len(matches) == 2:
            return ComplexType(matches[0], matches[1])
        elif len(matches) == 1:
            if len(matches[0]) == 2:
                return ComplexType(AtomicType(matches[0][0]), AtomicType(matches[0][1]))
            else:
                return AtomicType(matches[0])
        else:
            raise NotImplementedError


# The grammar of the type mini-language.
type_parser = Lark(
    '''
    ?start: type

    type: "<" type "," type ">"
        | /[evst]{1,2}/

    %import common.WS
    %ignore WS
''',
    parser='lalr',
    transformer=TreeToType(),
)


def parse_type(typestring):
    """Parse `typestring` into a tree of ComplexType and AtomicType objects.

    If the string cannot be parsed, a montague.exceptions.ParseError is raised.
    """
    try:
        return type_parser.parse(typestring)
    except LarkError as e:
        raise ParseError(str(e)) from None
