"""
Translation from English to the logical representation language.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: May 2019
"""
import itertools
from collections import OrderedDict

from . import ast
from .exceptions import CombinationError, LexiconError, ParseError
from .parser import parse_formula, parse_type


def translate_sentence(sentence, lexicon):
    """
    Translate `sentence`, a string containing English text, into a logical formula
    which represents its truth conditions.
    """
    terms = [lexicon.get(word, default_for_unknown(word)) for word in sentence.split()]
    all_possibilities = list(list(t) for t in itertools.product(*terms))
    in_progress = []
    finished = []
    for p in all_possibilities:
        if len(p) == 1:
            finished.append(p[0])
        else:
            in_progress.append(p)

    while in_progress:
        new_in_progress = []
        for terms in in_progress:
            for new_terms in step(terms):
                if len(new_terms) == 1:
                    finished.append(new_terms[0])
                else:
                    new_in_progress.append(new_terms)
        in_progress = new_in_progress

    for i in range(len(finished)):
        finished[i] = finished[i]._replace(formula=finished[i].formula.simplify())

    # Weed out duplicate translations by using OrderedDict to simulate an ordered set.
    return list(OrderedDict.fromkeys(finished).keys())


def step(terms):
    stepped_terms = []
    for i in range(len(terms) - 1):
        try:
            combined = combine(terms[i], terms[i + 1])
        except CombinationError:
            pass
        else:
            stepped_terms.append(terms[:i] + [combined] + terms[i + 2 :])
    return stepped_terms


def combine(term1, term2):
    """Attempt to combine the two terms by function application. If the terms' types are
    compatible, then a single term representing the denotation of the two terms combined
    is returned. If the types are not compatible, a CombinationError is raised.
    """
    if can_combine(term1, term2):
        return ast.SentenceNode(
            term1.text + " " + term2.text,
            ast.Call(term1.formula, term2.formula),
            term1.type.right,
        )
    elif can_combine(term2, term1):
        return ast.SentenceNode(
            # `text` should maintain linear order.
            term1.text + " " + term2.text,
            ast.Call(term2.formula, term1.formula),
            term2.type.right,
        )
    else:
        raise CombinationError


def can_combine(term1, term2):
    """Return True if the terms can be combined."""
    return isinstance(term1.type, ast.ComplexType) and term1.type.left == term2.type


def load_lexicon(lexicon_json):
    """Load the lexicon from a dictionary.

    If the lexicon is ill-formatted, a LexiconError is raised.
    """
    return {k: load_lexical_entry(k, v) for k, v in lexicon_json.items()}


def load_lexical_entry(key, values):
    trees = []
    for value in values:
        try:
            denotation = parse_formula(value["d"])
        except KeyError:
            raise LexiconError('entry for {} has no "d" field'.format(key))
        except ParseError as e:
            raise LexiconError("could not parse denotation of {} ({})".format(key, e))

        try:
            type_ = parse_type(value["t"])
        except KeyError:
            raise LexiconError('entry for {} has no "t" field'.format(key))
        except ParseError as e:
            raise LexiconError("could not parse type of {} ({})".format(key, e))

        trees.append(ast.SentenceNode(key, denotation, type_))

    return trees


def default_for_unknown(word):
    """Provide a default definition for words that are not in the lexicon."""
    proper_noun = ast.SentenceNode(word, ast.Var(word.lower()), ast.TYPE_ENTITY)
    single_place = ast.SentenceNode(
        word,
        ast.Lambda("x", ast.Call(ast.Var(word.title()), ast.Var("x"))),
        ast.ComplexType(ast.TYPE_ENTITY, ast.TYPE_TRUTH_VALUE),
    )
    double_place = ast.SentenceNode(
        word,
        ast.Lambda(
            "x",
            ast.Lambda(
                "y",
                ast.Call(ast.Call(ast.Var(word.title()), ast.Var("x")), ast.Var("y")),
            ),
        ),
        ast.ComplexType(
            ast.TYPE_ENTITY, ast.ComplexType(ast.TYPE_ENTITY, ast.TYPE_TRUTH_VALUE)
        ),
    )
    return [proper_noun, single_place, double_place]
