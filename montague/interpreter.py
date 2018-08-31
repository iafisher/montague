"""The interpreter that assigns truth values to a logical formula given a model
of the world.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: August 2018
"""
from collections import namedtuple

from .formula import (
    ForAllNode, AndNode, CallNode, ExistsNode, IfThenNode, NotNode, OrNode,
    VarNode,
)


WorldModel = namedtuple('WorldModel', ['individuals', 'assignments'])


def interpret_formula(formula, model):
    """Given a logical formula and a model of the world, return the formula's
    denotation in the model.
    """
    if isinstance(formula, VarNode):
        return model.assignments[formula.value]
    elif isinstance(formula, AndNode):
        return interpret_formula(formula.left, model) \
            and interpret_formula(formula.right, model)
    elif isinstance(formula, OrNode):
        return interpret_formula(formula.left, model) \
            or interpret_formula(formula.right, model)
    elif isinstance(formula, IfThenNode):
        return not interpret_formula(formula.left, model) \
            or interpret_formula(formula.right, model)
    elif isinstance(formula, CallNode):
        caller = interpret_formula(formula.caller, model)
        arg = interpret_formula(formula.arg, model)
        return arg in caller
    elif isinstance(formula, ForAllNode):
        old_value = model.assignments.get(formula.symbol)
        # Check that every assignment of an individual to the universal variable
        # results in a true proposition.
        for individual in model.individuals:
            model.assignments[formula.symbol] = individual
            if not interpret_formula(formula.body, model):
                model.assignments[formula.symbol] = old_value
                return False
        model.assignments[formula.symbol] = old_value
        return True
    elif isinstance(formula, ExistsNode):
        old_value = model.assignments.get(formula.symbol)
        # Check that any assignment of an individual to the existential variable
        # results in a true proposition.
        for individual in model.individuals:
            model.assignments[formula.symbol] = individual
            if interpret_formula(formula.body, model):
                model.assignments[formula.symbol] = old_value
                return True
        model.assignments[formula.symbol] = old_value
        return False
    elif isinstance(formula, NotNode):
        return not interpret_formula(formula.operand, model)
    else:
        # TODO: Handle LambdaNodes differently (they can't be interpreted, but
        # they should give a better error message).
        raise Exception('Unhandled class', formula.__class__)
