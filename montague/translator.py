"""Translation from English to the logical representation language.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: August 2018
"""
from collections import namedtuple

from lark.exceptions import LarkError

from .formula import (
    AllNode, AndNode, CallNode, ExistsNode, IfNode, LambdaNode, OrNode,
    TypeNode, VarNode, parse_formula, parse_type
)


LexiconEntry = namedtuple('LexiconEntry', ['denotation', 'type'])


def translate_sentence(sentence, lexicon):
    """Translate `sentence`, a string containing English text, into a logical
    formula which represents its truth conditions.

    If the sentence cannot be translated, a TranslationError is raised.
    """
    try:
        terms = [lexicon[t] for t in sentence.split()]
    except KeyError as e:
        raise TranslationError(f'Could not translate the word {e}')

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
            raise TranslationError('Could not translate the sentence')
        previous = len(terms)
    return LexiconEntry(simplify_formula(terms[0].denotation), terms[0].type)


def combine(term1, term2):
    """Attempt to combine the two terms by function application. If the terms'
    types are compatible, then a single term representing the denotation of the
    two terms combined is returned. If the types are not compatible, a
    CombinationError is raised.
    """
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
    """Return True if the terms can be combined."""
    return isinstance(term1.type, TypeNode) and term1.type.left == term2.type


def simplify_formula(tree):
    """Simplify the tree by lambda conversion."""
    if isinstance(tree, CallNode) and not isinstance(tree.caller, VarNode):
        caller = simplify_formula(tree.caller)
        arg = simplify_formula(tree.arg)
        if isinstance(caller, LambdaNode):
            return simplify_formula(
                caller.body.replace_variable(caller.parameter, arg)
            )
        else:
            return CallNode(tree.caller, arg)
    elif isinstance(tree, tuple):
        return tree.__class__(*map(simplify_formula, tree))
    else:
        return tree


class CombinationError(Exception):
    """When two expressions cannot be combined."""
    pass


class TranslationError(Exception):
    """When an English sentence cannot be translated into logic."""
    pass


class LexiconError(Exception):
    """When the lexicon is ill-formatted."""
    pass


def load_lexicon(lexicon_json):
    """Load the lexicon from a dictionary.

    If the lexicon is ill-formatted, a LexiconError is raised.
    """
    return {k: load_lexical_entry(k, v) for k, v in lexicon_json.items()}


def load_lexical_entry(key, value):
    try:
        denotation = parse_formula(value['d'])
    except KeyError:
        raise LexiconError(f'entry for {key} has no "d" field')
    except LarkError as e:
        raise LexiconError(f'could not parse denotation of {key} ({e})')

    try:
        type_ = parse_type(value['t'])
    except KeyError:
        raise LexiconError(f'entry for {key} has no "t" field')
    except LarkError as e:
        raise LexiconError(f'could not parse type of {key} ({e})')

    return LexiconEntry(denotation, type_)
