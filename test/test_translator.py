import pytest

import json
import os

from montague.ast import *
from montague.parser import parse_formula, parse_type
from montague.translator import (
    LexiconError,
    TranslationError,
    can_combine,
    combine,
    load_lexicon,
    translate_sentence,
)


TYPE_ET = ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE)


TEST_LEXICON = {
    'bad': SentenceNode('bad', Lambda('x', Call(Var('Bad'), Var('x'))), TYPE_ET),
    'is': SentenceNode('is', Lambda('P', Var('P')), ComplexType(TYPE_ET, TYPE_ET)),
    'good': SentenceNode('good', Lambda('x', Call(Var('Good'), Var('x'))), TYPE_ET),
    'every': SentenceNode(
        'every',
        Lambda(
            'P',
            Lambda(
                'Q',
                ForAll('x', IfThen(Call(Var('P'), Var('x')), Call(Var('Q'), Var('x')))),
            ),
        ),
        ComplexType(TYPE_ET, ComplexType(TYPE_ET, TYPE_TRUTH_VALUE)),
    ),
    'child': SentenceNode('child', Lambda('x', Call(Var('Child'), Var('x'))), TYPE_ET),
    'John': SentenceNode('John', Var('j'), TYPE_ENTITY),
    'the': SentenceNode(
        'the',
        Lambda('P', Iota('x', Call(Var('P'), Var('x')))),
        ComplexType(TYPE_ET, TYPE_ENTITY),
    ),
}


def test_translate_is_good():
    node = translate_sentence('is good', TEST_LEXICON)
    assert node.text == 'is good'
    assert node.formula == Lambda('x', Call(Var('Good'), Var('x')))
    assert node.type == TYPE_ET


def test_translate_john_is_good():
    node = translate_sentence('John is good', TEST_LEXICON)
    assert node.text == 'John is good'
    assert node.formula == Call(Var('Good'), Var('j'))
    assert node.type == TYPE_TRUTH_VALUE


def test_translate_john_is_bad():
    node = translate_sentence('John is bad', TEST_LEXICON)
    assert node.text == 'John is bad'
    assert node.formula == Call(Var('Bad'), Var('j'))
    assert node.type == TYPE_TRUTH_VALUE


def test_translate_every_child_is_good():
    node = translate_sentence('every child is good', TEST_LEXICON)
    assert node.text == 'every child is good'
    assert node.formula == ForAll(
        'x', IfThen(Call(Var('Child'), Var('x')), Call(Var('Good'), Var('x')))
    )
    assert node.type == TYPE_TRUTH_VALUE


def test_translate_the_child():
    node = translate_sentence('the child', TEST_LEXICON)
    assert node.text == 'the child'
    assert node.formula == Iota('x', Call(Var('Child'), Var('x')))
    assert node.type == TYPE_ENTITY


def test_translate_invalid_sentence():
    with pytest.raises(TranslationError):
        translate_sentence('every John is good', TEST_LEXICON)


def test_translate_unknown_word():
    with pytest.raises(TranslationError) as e:
        translate_sentence('John is whorlious', TEST_LEXICON)
    assert 'whorlious' in str(e)


pred = SentenceNode('does', parse_formula('Lx.P(x)'), parse_type('<e, t>'))
entity = SentenceNode('me', Var('me'), TYPE_ENTITY)


def test_combine_to_saturate_predicate():
    assert can_combine(pred, entity)
    node = combine(pred, entity)
    assert node.text == 'does me'
    assert node.formula == Call(pred.formula, entity.formula)
    assert node.type == TYPE_TRUTH_VALUE


def test_combine_every_child():
    every = TEST_LEXICON['every']
    child = TEST_LEXICON['child']
    node = combine(every, child)
    assert node.text == 'every child'
    assert node.formula == Call(every.formula, child.formula)
    assert node.type == ComplexType(TYPE_ET, TYPE_TRUTH_VALUE)


def test_can_combine_is_good():
    assert can_combine(TEST_LEXICON['is'], TEST_LEXICON['good'])


def test_cannot_combine_mismatched_types():
    assert not can_combine(pred, pred)
    assert not can_combine(entity, pred)
    assert not can_combine(entity, entity)


def test_simplify_call():
    tree = Call(Lambda('x', Var('x')), Var('j'))
    assert tree.simplify() == Var('j')


def test_simplify_nested_call():
    # (Lx.Ly.x & y)(a)(b) -> a & b
    tree = Call(
        Call(Lambda('x', Lambda('y', And(Var('x'), Var('y')))), Var('a')), Var('b')
    )
    assert tree.simplify() == And(Var('a'), Var('b'))


def test_simplify_call_with_lambda_arg():
    # (LP.P(x))(Lx.x | a) -> x | a
    tree = Call(
        Lambda('P', Call(Var('P'), Var('x'))), Lambda('x', Or(Var('x'), Var('a')))
    )
    assert tree.simplify() == Or(Var('x'), Var('a'))


def test_simplify_super_nested_call():
    # (LP.P(a, b))(Lx.Ly.x & y) -> a & b
    tree = Call(
        Lambda('P', Call(Call(Var('P'), Var('a')), Var('b'))),
        Lambda('x', Lambda('y', And(Var('x'), Var('y')))),
    )
    assert tree.simplify() == And(Var('a'), Var('b'))


def test_simplify_every_child():
    # (LP.LQ.Ax.P(x) -> Q(x))(Lx.Child(x)) -> LQ.Ax.Child(x) -> Q(x)
    tree = Call(TEST_LEXICON['every'].formula, TEST_LEXICON['child'].formula)
    assert tree.simplify() == Lambda(
        'Q', ForAll('x', IfThen(Call(Var('Child'), Var('x')), Call(Var('Q'), Var('x'))))
    )


def test_load_lexicon():
    lexicon = load_lexicon(
        {'John': {'d': 'j', 't': 'e'}, 'good': {'d': 'Lx.Good(x)', 't': 'et'}}
    )
    assert lexicon == {
        'John': SentenceNode('John', parse_formula('j'), parse_type('e')),
        'good': SentenceNode('good', parse_formula('Lx.Good(x)'), parse_type('et')),
    }


def test_load_lexicon_missing_denotation_field():
    with pytest.raises(LexiconError) as e:
        load_lexicon({'John': {'t': 'e'}})
    assert 'John' in str(e)


def test_load_lexicon_with_missing_type_field():
    with pytest.raises(LexiconError) as e:
        load_lexicon({'John': {'d': 'j'}})
    assert 'John' in str(e)


def test_load_lexicon_with_invalid_denotation_formula():
    with pytest.raises(LexiconError) as e:
        load_lexicon({'John': {'d': '???', 't': 'e'}})
    assert 'John' in str(e)


def test_load_lexicon_with_invalid_type():
    with pytest.raises(LexiconError) as e:
        load_lexicon({'John': {'d': 'j', 't': '???'}})
    assert 'John' in str(e)
