"""The interpreter that assigns truth values to a logical formula given a model of the
world.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: August 2018
"""
from collections import namedtuple

from . import ast


WorldModel = namedtuple("WorldModel", ["individuals", "assignments"])


def interpret_formula(formula, model):
    """Given a logical formula and a model of the world, return the formula's denotation
    in the model.
    """
    if isinstance(formula, ast.Var):
        return model.assignments[formula.value]
    elif isinstance(formula, ast.And):
        return interpret_formula(formula.left, model) and interpret_formula(
            formula.right, model
        )
    elif isinstance(formula, ast.Or):
        return interpret_formula(formula.left, model) or interpret_formula(
            formula.right, model
        )
    elif isinstance(formula, ast.IfThen):
        return not interpret_formula(formula.left, model) or interpret_formula(
            formula.right, model
        )
    elif isinstance(formula, ast.Call):
        caller = interpret_formula(formula.caller, model)
        arg = interpret_formula(formula.arg, model)
        return arg in caller
    elif isinstance(formula, ast.ForAll):
        return len(satisfiers(formula.body, model, formula.symbol)) == len(
            model.individuals
        )
    elif isinstance(formula, ast.Exists):
        return len(satisfiers(formula.body, model, formula.symbol)) > 0
    elif isinstance(formula, ast.Not):
        return not interpret_formula(formula.operand, model)
    elif isinstance(formula, ast.Iota):
        sset = satisfiers(formula.body, model, formula.symbol)
        if len(sset) == 1:
            return sset.pop()
        else:
            return None
    else:
        # TODO: Handle LambdaNodes differently (they can't be interpreted, but they
        # should give a better error message).
        raise NotImplementedError(formula.__class__)


def satisfiers(formula, model, variable):
    individuals = set()
    old_value = model.assignments.get(variable)
    for individual in model.individuals:
        model.assignments[variable] = individual
        if interpret_formula(formula, model):
            individuals.add(individual)

    if old_value is None:
        del model.assignments[variable]
    else:
        model.assignments[variable] = old_value

    return individuals
