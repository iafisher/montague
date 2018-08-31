"""The parser for Montague's logical representation language, including type
expressions.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: August 2018
"""
from collections import namedtuple
from enum import Enum

from lark import Lark, Transformer


# Below are defined the classes to represent logical formulas as trees.


class Node:
    def replace_variable(self, variable, replacement):
        """Replace all unbound instances of `variable`, a string, with
        `replacement`.

        The default implementation recursively replaces the variable in all
        children. Subclasses may need to override this implementation.
        """
        return self.__class__(
            *[(c.replace_variable(variable, replacement) if isinstance(c, Node)
               else c) for c in self]
        )

    def simplify(self):
        """Simplify the tree by lambda conversion.

        The default implementation recursively simplifies each child. Subclasses
        may need to override this implementation.
        """
        return self.__class__(*[(c.simplify() if isinstance(c, Node) else c)
            for c in self])


class VarNode(Node, namedtuple('VarNode', ['value'])):
    prec = 1

    def __str__(self):
        return self.value

    def replace_variable(self, variable, replacement):
        return self if variable != self.value else replacement


class AndNode(Node, namedtuple('AndNode', ['left', 'right'])):
    prec = 2

    def __str__(self):
        # wrapb applies brackets if needed for the proper precedence.
        left = wrapb(self, self.left, False)
        right = wrapb(self, self.right, True)
        return f'{left} & {right}'


class OrNode(Node, namedtuple('OrNode', ['left', 'right'])):
    prec = 3

    def __str__(self):
        left = wrapb(self, self.left, False)
        right = wrapb(self, self.right, True)
        return f'{left} | {right}'


class IfNode(Node, namedtuple('IfNode', ['left', 'right'])):
    prec = 4

    def __str__(self):
        left = wrapb(self, self.left, False)
        right = wrapb(self, self.right, True)
        return f'{left} -> {right}'


class NotNode(Node, namedtuple('NotNode', ['operand'])):
    prec = 1

    def __str__(self):
        operand = wrapb(self, self.operand, False)
        return f'~{operand}'


class LambdaNode(Node, namedtuple('LambdaNode', ['parameter', 'body'])):
    prec = 5

    def __str__(self):
        return f'L{self.parameter}.{self.body}'

    def replace_variable(self, variable, replacement):
        if variable != self.parameter:
            return LambdaNode(
                self.parameter,
                self.body.replace_variable(variable, replacement)
            )
        else:
            return self


class CallNode(Node, namedtuple('CallNode', ['caller', 'arg'])):
    prec = 1

    def __str__(self):
        # To make string representations more natural, F(x)(y) is printed as
        # F(x, y), which is why this method is more complicated than you would
        # expect.
        args = [str(self.arg)]
        func = self.caller
        while isinstance(func, CallNode):
            args.append(str(func.arg))
            func = func.caller
        args = ', '.join(reversed(args))
        if isinstance(func, VarNode):
            return f'{func}({args})'
        else:
            # Syntactically, a non-constant function must be in parentheses in
            # a call expression.
            return f'({func})({args})'

    def simplify(self):
        caller = self.caller.simplify()
        arg = self.arg.simplify()
        if isinstance(caller, LambdaNode):
            return caller.body.replace_variable(caller.parameter, arg) \
                .simplify()
        else:
            return CallNode(self.caller, arg)


class AllNode(Node, namedtuple('AllNode', ['symbol', 'body'])):
    prec = 5

    def __str__(self):
        return f'A{self.symbol}.{self.body}'

    def replace_variable(self, variable, replacement):
        if variable != self.symbol:
            return AllNode(
                self.symbol,
                self.body.replace_variable(variable, replacement)
            )
        else:
            return self


class ExistsNode(Node, namedtuple('ExistsNode', ['symbol', 'body'])):
    prec = 5

    def __str__(self):
        return f'E{self.symbol}.{self.body}'

    def replace_variable(self, variable, replacement):
        if variable != self.symbol:
            return ExistsNode(
                self.symbol,
                self.body.replace_variable(variable, replacement)
            )
        else:
            return self


class TreeToFormula(Transformer):
    """Transform Lark's parse tree into a formula tree with objects of the Node
    classes.
    """

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
        # The parse tree allows n-ary functions but the AST only allows unary
        # functions. This methods converts the former to the latter, e.g.
        # F(x, y, z) becomes F(x)(y)(z), three nested CallNodes.
        func = CallNode(matches[0], matches[1])
        for i in range(2, len(matches)):
            func = CallNode(func, matches[i])
        return func

    def not_e(self, matches):
        return NotNode(matches[1])


# The grammar of the logical language.
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
    """Parse `formula`, a string, into a tree of objects of the Node classes.

    If the string cannot be parsed, a LarkError is raised.
    """
    return formula_parser.parse(formula)


# Below are defined the classes to represent semantic types as trees.


class TypeNode(namedtuple('TypeNode', ['left', 'right'])):
    def __str__(self):
        return f'<{self.left}, {self.right}>'

    def concise_str(self):
        """Convert the type to a string, recursively abbreviating '<x, y>' as
        'xy' as long as 'x' and 'y' are atomic types.

           >>> typ = TypeNode(TYPE_ENTITY, TYPE_TRUTH_VALUE)
           >>> str(typ)
           '<e, t>'
           >>> typ.concise_str()
           'et'
        """
        left = self.left
        if isinstance(self.left, AtomicType) \
           and isinstance(self.right, AtomicType):
            return f'{self.left}{self.right}'
        else:
            return f'<{self.left.concise_str()}, {self.right.concise_str()}>'


class AtomicType(str):
    def concise_str(self):
        return self


# Constants for the recognized atomic types.
TYPE_ENTITY = AtomicType('e')
TYPE_TRUTH_VALUE = AtomicType('t')
TYPE_EVENT = AtomicType('v')
TYPE_WORLD = AtomicType('s')


class TreeToType(Transformer):
    """Transform Lark's parse tree into a type tree with TypeNode and AtomicType
    objects.
    """
    def type(self, matches):
        if len(matches) == 2:
            return TypeNode(matches[0], matches[1])
        else:
            if len(matches[0]) == 2:
                return TypeNode(matches[0][0], matches[0][1])
            else:
                return matches[0]


# The grammar of the type mini-language.
type_parser = Lark('''
    ?start: type

    type: "<" type "," type ">"
        | /[evst]{1,2}/

    %import common.WS
    %ignore WS
''', parser='lalr', transformer=TreeToType())


def parse_type(typestring):
    """Parse `typestring` into a tree of TypeNode and AtomicType objects.

    If the string cannot be parsed, a LarkError is raised.
    """
    return type_parser.parse(typestring)


def wrapb(parent, child, right):
    """Return the child node as a string, wrapped in brackets if its precedence
    is higher than the parent node.
    """
    if child.prec > parent.prec or child.prec == parent.prec and right:
        return f'[{child}]'
    else:
        return str(child)
