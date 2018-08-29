"""Translation from English to the logical representation language.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: August 2018
"""
from collections import namedtuple

from .formula import (
    AllNode, AndNode, CallNode, ExistsNode, LambdaNode, OrNode, TypeNode,
    VarNode, parse_formula, parse_type
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
    return terms[0]


def combine(term1, term2):
    if can_combine(term1, term2):
        pass
    elif can_combine(term2, term1):
        term1, term2 = term2, term1
    else:
        raise CombinationError
    return LexiconEntry(
        replace_variable(term1.denotation.body, term1.denotation.parameter,
            term2.denotation),
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
    elif isinstance(formula, LambdaNode) and formula.parameter != variable:
        return LambdaNode(
            formula.parameter,
            replace_variable(formula.body, variable, replacement)
        )
    elif isinstance(formula, CallNode):
        return CallNode(
            replace_variable(formula.symbol, variable, replacement),
            [replace_variable(a, variable, replacement) for a in formula.args]
        )
    elif isinstance(formula, AllNode) and formula.symbol != variable:
        return AllNode(
            formula.symbol,
            replace_variable(formula.body, variable, replacement)
        )
    elif isinstance(formula, ExistsNode) and formula.symbol != variable:
        return ExistsNode(
            formula.symbol,
            replace_variable(formula.body, variable, replacement)
        )
    else:
        return formula


class CombinationError(Exception):
    pass


def load_lexicon(lexicon_json):
    return {k: load_lexical_entry(v) for k, v in lexicon_json.items()}


def load_lexical_entry(entry_json):
    return LexiconEntry(
        parse_formula(entry_json['d']),
        parse_type(entry_json['t'])
    )
