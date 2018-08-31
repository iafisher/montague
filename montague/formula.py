"""The parser for Montague's logical representation language, including type
expressions.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: August 2018
"""
from collections import namedtuple
from enum import Enum

from lark import Lark, Transformer


class VarNode(namedtuple('VarNode', 'value')):
    def __str__(self):
        return self.value


class AndNode(namedtuple('AndNode', ['left', 'right'])):
    def __str__(self):
        return f'{self.left} & {self.right}'


class OrNode(namedtuple('OrNode', ['left', 'right'])):
    def __str__(self):
        return f'{self.left} | {self.right}'


class IfNode(namedtuple('IfNode', ['left', 'right'])):
    def __str__(self):
        return f'{self.left} -> {self.right}'


class NotNode(namedtuple('NotNode', ['operand'])):
    def __str__(self):
        if isinstance(self.operand, VarNode):
            return f'~{self.operand}'
        else:
            return f'~[{self.operand}]'


class LambdaNode(namedtuple('LambdaNode', ['parameter', 'body'])):
    def __str__(self):
        return f'L{self.parameter}.{self.body}'


class CallNode(namedtuple('CallNode', ['caller', 'arg'])):
    def __str__(self):
        args = [str(self.arg)]
        func = self.caller
        while isinstance(func, CallNode):
            args.append(str(func.arg))
            func = func.caller
        args = ', '.join(reversed(args))
        if isinstance(func, VarNode):
            return f'{func}({args})'
        else:
            return f'({func})({args})'


class AllNode(namedtuple('AllNode', ['symbol', 'body'])):
    def __str__(self):
        return f'A{self.symbol}.{self.body}'


class ExistsNode(namedtuple('ExistsNode', ['symbol', 'body'])):
    def __str__(self):
        return f'E{self.symbol}.{self.body}'


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
        func = CallNode(matches[0], matches[1])
        for i in range(2, len(matches)):
            func = CallNode(func, matches[i])
        return func

    def not_e(self, matches):
        return NotNode(matches[1])


formula_parser = Lark('''
    ?start: expr

    ?expr: ifterm | ifterm IMPLIES expr

    ?ifterm: term | term OR ifterm
    ?term: factor | factor AND term
    ?factor: variable
           | "[" expr "]"
           | call
           | lambda_
           | forall
           | exists
           | NOT factor  -> not_e

    call: variable "(" _arglist? ")" | "(" expr ")" "(" _arglist? ")"
    _arglist: ( expr "," )* expr

    lambda_: "L" SYMBOL "." expr
    forall: "A" SYMBOL "." expr
    exists: "E" SYMBOL "." expr

    variable: SYMBOL

    SYMBOL: /[B-DF-KM-Za-z][A-Za-z0-9_'-]*/
    OR: "|"
    AND: "&"
    IMPLIES: "->"
    NOT: "~"

    %import common.WS
    %ignore WS
''', parser='lalr', transformer=TreeToFormula())


def parse_formula(formula):
    return formula_parser.parse(formula)


class TypeNode(namedtuple('TypeNode', ['left', 'right'])):
    def __str__(self):
        return f'<{self.left}, {self.right}>'

    def concise_str(self):
        left = self.left
        if isinstance(self.left, AtomicType) \
           and isinstance(self.right, AtomicType):
            return f'{self.left}{self.right}'
        else:
            return f'<{self.left.concise_str()}, {self.right.concise_str()}>'


class AtomicType(str):
    def concise_str(self):
        return self


TYPE_ENTITY = AtomicType('e')
TYPE_TRUTH_VALUE = AtomicType('t')
TYPE_EVENT = AtomicType('v')
TYPE_WORLD = AtomicType('s')


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
        | /[evst]{1,2}/

    %import common.WS
    %ignore WS
''', parser='lalr', transformer=TreeToType())


def parse_type(typestring):
    return type_parser.parse(typestring)
