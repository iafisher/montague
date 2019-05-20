"""Translation from English to the logical representation language.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: September 2018
"""
from . import ast
from .exceptions import CombinationError, LexiconError, ParseError, TranslationError
from .parser import parse_formula, parse_type


def translate_sentence(sentence, lexicon):
    """Translate `sentence`, a string containing English text, into a logical formula
    which represents its truth conditions.

    If the sentence cannot be translated, a TranslationError is raised.
    """
    terms = [lexicon.get(word, default_for_unknown(word)) for word in sentence.split()]

    previous = len(terms)
    while len(terms) > 1:
        new_terms = []
        i = 0
        while i < len(terms) - 1:
            try:
                new_terms.append(combine(terms[i], terms[i + 1]))
                i += 2
            except CombinationError:
                new_terms.append(terms[i])
                i += 1
        if i == len(terms) - 1:
            new_terms.append(terms[i])
        terms = new_terms
        if len(terms) == previous:
            raise TranslationError(
                "Could not translate the sentence: no way to merge "
                + ", ".join(
                    "[{} ({})]".format(term.text, term.type.concise_str())
                    for term in terms
                )
            )
        previous = len(terms)
    root = terms[0]._replace(formula=terms[0].formula.simplify())
    return root


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


def load_lexical_entry(key, value):
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

    return ast.SentenceNode(key, denotation, type_)


def default_for_unknown(word):
    """Provide a default definition for words that are not in the lexicon."""
    formula = ast.Lambda("x", ast.Call(ast.Var(word.title()), ast.Var("x")))
    type_et = ast.ComplexType(ast.TYPE_ENTITY, ast.TYPE_TRUTH_VALUE)
    return ast.SentenceNode(word, formula, type_et)
