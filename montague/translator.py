"""Translation from English to the logical representation language.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: August 2018
"""
from collections import namedtuple

from .formula import (
    AllNode, AndNode, CallNode, ExistsNode, IfNode, LambdaNode, OrNode,
    TypeNode, VarNode, parse_formula, parse_type
)


LexiconEntry = namedtuple('LexiconEntry', ['denotation', 'type'])


def translate_sentence(sentence, lexicon):
    terms = [lexicon[t] for t in sentence.split()]
    previous = len(terms)
    while len(terms) > 1:
        new_terms = []
        i = 0
        while i < len(terms) - 1:
            try:
                new_terms.append(combine(terms[i], terms[i+1]))
                i += 2
            except CombinationError:
                new_terms.append(terms[i])
                i += 1
        if i == len(terms) - 1:
            new_terms.append(terms[i])
        terms = new_terms
        if len(terms) == previous:
            raise Exception('Could not combine lexical items', terms)
        previous = len(terms)
    return LexiconEntry(simplify_formula(terms[0].denotation), terms[0].type)


def combine(term1, term2):
    if can_combine(term1, term2):
        pass
    elif can_combine(term2, term1):
        term1, term2 = term2, term1
    else:
        raise CombinationError
    return LexiconEntry(
        CallNode(term1.denotation, term2.denotation),
        term1.type.right
    )


def can_combine(term1, term2):
    return isinstance(term1.type, TypeNode) and term1.type.left == term2.type


def replace_variable(formula, variable, replacement):
    if isinstance(formula, VarNode):
        return replacement if formula.value == variable else formula
    elif isinstance(formula, AndNode):
        return AndNode(
            replace_variable(formula.left, variable, replacement),
            replace_variable(formula.right, variable, replacement)
        )
    elif isinstance(formula, OrNode):
        return OrNode(
            replace_variable(formula.left, variable, replacement),
            replace_variable(formula.right, variable, replacement)
        )
    elif isinstance(formula, IfNode):
        return IfNode(
            replace_variable(formula.left, variable, replacement),
            replace_variable(formula.right, variable, replacement)
        )
    elif isinstance(formula, LambdaNode):
        if formula.parameter != variable:
            return LambdaNode(
                formula.parameter,
                replace_variable(formula.body, variable, replacement)
            )
        else:
            return formula
    elif isinstance(formula, CallNode):
        return CallNode(
            replace_variable(formula.caller, variable, replacement),
            replace_variable(formula.arg, variable, replacement)
        )
    elif isinstance(formula, AllNode):
        if formula.symbol != variable:
            return AllNode(
                formula.symbol,
                replace_variable(formula.body, variable, replacement)
            )
        else:
            return formula
    elif isinstance(formula, ExistsNode):
        if formula.symbol != variable:
            return ExistsNode(
                formula.symbol,
                replace_variable(formula.body, variable, replacement)
            )
        else:
            return formula
    elif isinstance(formula, VarNode):
        return formula
    else:
        raise Exception('Unhandled class', formula.__class__)


def simplify_formula(tree):
    if isinstance(tree, CallNode) and not isinstance(tree.caller, VarNode):
        caller = simplify_formula(tree.caller)
        arg = simplify_formula(tree.arg)
        if isinstance(caller, LambdaNode):
            return simplify_formula(
                replace_variable(caller.body, caller.parameter, arg)
            )
        else:
            return CallNode(tree.caller, arg)
    elif isinstance(tree, tuple):
        return tree.__class__(*map(simplify_formula, tree))
    else:
        return tree


class CombinationError(Exception):
    pass


def load_lexicon(lexicon_json):
    return {k: load_lexical_entry(v) for k, v in lexicon_json.items()}


def load_lexical_entry(entry_json):
    return LexiconEntry(
        parse_formula(entry_json['d']),
        parse_type(entry_json['t'])
    )
