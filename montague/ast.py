"""The representation of logical formulas, semantic types and sentences as
trees.

Logical formulas: Formula subclasses
Semantic types: ComplexType and AtomicType
Sentences: SentenceNode

Author:  Ian Fisher (iafisher@protonmail.com)
Version: September 2018
"""
from collections import namedtuple


# Below are defined the classes to represent logical formulas as trees.


class Formula:
    def replace_variable(self, variable, replacement):
        """Replace all unbound instances of `variable`, a string, with
        `replacement`.

        The default implementation recursively replaces the variable in all
        children. Subclasses may need to override this implementation.
        """
        children = [
            c.replace_variable(variable, replacement) if isinstance(c, Formula) else c
            for c in self
        ]
        return self.__class__(*children)

    def simplify(self):
        """Simplify the tree by lambda conversion.

        The default implementation recursively simplifies each child. Subclasses
        may need to override this implementation.
        """
        children = [c.simplify() if isinstance(c, Formula) else c for c in self]
        return self.__class__(*children)

    def ascii_str(self):
        """Render the formula as a string containing only ASCII characters.

        The default implementation falls back to __str__. Subclasses whose
        __str__ contains non-ASCII characters should override this method.
        """
        return str(self)


class Var(Formula, namedtuple('Var', ['value'])):
    prec = 1

    def __str__(self):
        return self.value

    def replace_variable(self, variable, replacement):
        return self if variable != self.value else replacement


class And(Formula, namedtuple('And', ['left', 'right'])):
    prec = 2

    def __str__(self):
        # wrapb applies brackets if needed for the proper precedence.
        left = wrapb(self, self.left)
        right = wrapb(self, self.right)
        return left + ' & ' + right


class Or(Formula, namedtuple('Or', ['left', 'right'])):
    prec = 3

    def __str__(self):
        left = wrapb(self, self.left)
        right = wrapb(self, self.right)
        return left + ' | ' + right


class IfThen(Formula, namedtuple('IfThen', ['left', 'right'])):
    prec = 4

    def __str__(self):
        left = wrapb(self, self.left)
        right = wrapb(self, self.right)
        return left + ' -> ' + right


class IfAndOnlyIf(Formula, namedtuple('IfAndOnlyIf', ['left', 'right'])):
    prec = 4

    def __str__(self):
        left = wrapb(self, self.left)
        right = wrapb(self, self.right)
        return left + ' <-> ' + right


class Not(Formula, namedtuple('Not', ['operand'])):
    prec = 1

    def __str__(self):
        operand = wrapb(self, self.operand)
        return '~' + operand


class Lambda(Formula, namedtuple('Lambda', ['parameter', 'body'])):
    prec = 5

    def __str__(self):
        return 'λ{0.parameter}.{0.body}'.format(self)

    def ascii_str(self):
        return 'L{0.parameter}.{0.body}'.format(self)

    def replace_variable(self, variable, replacement):
        if variable != self.parameter:
            return Lambda(
                self.parameter, self.body.replace_variable(variable, replacement)
            )
        else:
            return self


class Call(Formula, namedtuple('Call', ['caller', 'arg'])):
    prec = 1

    def __str__(self):
        # To make string representations more natural, F(x)(y) is printed as
        # F(x, y), which is why this method is more complicated than you would
        # expect.
        args = [str(self.arg)]
        func = self.caller
        while isinstance(func, Call):
            args.append(str(func.arg))
            func = func.caller
        args = ', '.join(reversed(args))
        if isinstance(func, Var):
            return '{}({})'.format(func, args)
        else:
            # Syntactically, a non-constant function must be in parentheses in
            # a call expression.
            return '({})({})'.format(func, args)

    def simplify(self):
        caller = self.caller.simplify()
        arg = self.arg.simplify()
        if isinstance(caller, Lambda):
            return caller.body.replace_variable(caller.parameter, arg).simplify()
        else:
            return Call(self.caller, arg)


class ForAll(Formula, namedtuple('ForAll', ['symbol', 'body'])):
    prec = 5

    def __str__(self):
        return '∀ {0.symbol}.{0.body}'.format(self)

    def ascii_str(self):
        return 'A{0.symbol}.{0.body}'.format(self)

    def replace_variable(self, variable, replacement):
        if variable != self.symbol:
            return ForAll(
                self.symbol, self.body.replace_variable(variable, replacement)
            )
        else:
            return self


class Exists(Formula, namedtuple('Exists', ['symbol', 'body'])):
    prec = 5

    def __str__(self):
        return '∃ {0.symbol}.{0.body}'.format(self)

    def ascii_str(self):
        return 'E{0.symbol}.{0.body}'.format(self)

    def replace_variable(self, variable, replacement):
        if variable != self.symbol:
            return Exists(
                self.symbol, self.body.replace_variable(variable, replacement)
            )
        else:
            return self


class Iota(Formula, namedtuple('Iota', ['symbol', 'body'])):
    prec = 5

    def __str__(self):
        return 'ι{0.symbol}.{0.body}'.format(self)

    def ascii_str(self):
        # 'i' instead of 'ι'
        return 'i{0.symbol}.{0.body}'.format(self)

    def replace_variable(self, variable, replacement):
        if variable != self.symbol:
            return Iota(self.symbol, self.body.replace_variable(variable, replacement))
        else:
            return self


# Below are defined the classes to represent semantic types as trees.


class ComplexType(namedtuple('ComplexType', ['left', 'right'])):
    def __str__(self):
        return '<{0.left}, {0.right}>'.format(self)

    def concise_str(self):
        """Convert the type to a string, recursively abbreviating '<x, y>' as
        'xy' as long as 'x' and 'y' are atomic types.

           >>> typ = ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE)
           >>> str(typ)
           '<e, t>'
           >>> typ.concise_str()
           'et'
        """
        if isinstance(self.left, AtomicType) and isinstance(self.right, AtomicType):
            return '{0.left}{0.right}'.format(self)
        else:
            return '<{}, {}>'.format(self.left.concise_str(), self.right.concise_str())


class AtomicType(str):
    def concise_str(self):
        return self


# Constants for the recognized atomic types.
TYPE_ENTITY = AtomicType('e')
TYPE_TRUTH_VALUE = AtomicType('t')
TYPE_EVENT = AtomicType('v')
TYPE_WORLD = AtomicType('s')


# The class to represent English sentences as logical formulas. `text` is the
# English text corresponding to the node.
SentenceNode = namedtuple('SentenceNode', ['text', 'formula', 'type'])


def wrapb(parent, child):
    """Return the child node as a string, wrapped in brackets if its precedence
    is higher than the parent node.
    """
    if child.prec > parent.prec:
        return '[{}]'.format(child)
    else:
        return str(child)
