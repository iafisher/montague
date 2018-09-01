import json
import os
import unittest

from montague.ast import *
from montague.parser import parse_formula, parse_type
from montague.translator import (
    LexiconEntry, LexiconError, TranslationError, can_combine, combine,
    load_lexicon, translate_sentence,
)


TYPE_ET = ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE)


TEST_LEXICON = {
  'bad': LexiconEntry(
      'bad',
      Lambda('x', Call(Var('Bad'), Var('x'))),
      TYPE_ET
  ),
  'is': LexiconEntry(
      'is',
      Lambda('P', Var('P')),
      ComplexType(TYPE_ET, TYPE_ET)
  ),
  'good': LexiconEntry(
      'good',
      Lambda('x', Call(Var('Good'), Var('x'))),
      TYPE_ET
  ),
  'every': LexiconEntry(
      'every',
      Lambda(
          'P',
          Lambda(
              'Q',
              ForAll(
                  'x',
                  IfThen(
                      Call(Var('P'), Var('x')),
                      Call(Var('Q'), Var('x'))
                  )
              )
          )
      ),
      ComplexType(
          TYPE_ET,
          ComplexType(TYPE_ET, TYPE_TRUTH_VALUE)
      )
  ),
  'child': LexiconEntry(
      'child',
      Lambda('x', Call(Var('Child'), Var('x'))),
      TYPE_ET
  ),
  'John': LexiconEntry('John', Var('j'), TYPE_ENTITY),
  'the': LexiconEntry(
      'the',
      Lambda('P', Iota('x', Call(Var('P'), Var('x')))),
      ComplexType(TYPE_ET, TYPE_ENTITY)
   )
}


class TranslatorTest(unittest.TestCase):
    def test_is_good(self):
        self.assertTupleEqual(
            translate_sentence('is good', TEST_LEXICON),
            LexiconEntry(
                'is good',
                Lambda(
                    'x',
                    Call(Var('Good'), Var('x'))
                ),
                TYPE_ET
            )
        )

    def test_john_is_good(self):
        self.assertTupleEqual(
            translate_sentence('John is good', TEST_LEXICON),
            LexiconEntry(
                'John is good',
                Call(Var('Good'), Var('j')),
                TYPE_TRUTH_VALUE
            )
        )

    def test_john_is_bad(self):
        self.assertTupleEqual(
            translate_sentence('John is bad', TEST_LEXICON),
            LexiconEntry(
                'John is bad',
                Call(Var('Bad'), Var('j')),
                TYPE_TRUTH_VALUE
            )
        )

    def test_every_child_is_good(self):
        self.assertTupleEqual(
            translate_sentence('every child is good', TEST_LEXICON),
            LexiconEntry(
                'every child is good',
                ForAll(
                    'x',
                    IfThen(
                        Call(Var('Child'), Var('x')),
                        Call(Var('Good'), Var('x'))
                    )
                ),
                TYPE_TRUTH_VALUE
            )
        )

    def test_the_child(self):
        self.assertTupleEqual(
            translate_sentence('the child', TEST_LEXICON),
            LexiconEntry(
                'the child',
                Iota('x', Call(Var('Child'), Var('x'))),
                TYPE_ENTITY
            )
        )

    def test_translate_invalid_sentence(self):
        with self.assertRaises(TranslationError):
            translate_sentence('every John is good', TEST_LEXICON)

    def test_translate_unknown_word(self):
        with self.assertRaisesRegex(TranslationError, r'.*whorlious.*'):
            translate_sentence('John is whorlious', TEST_LEXICON)


class CombinerTest(unittest.TestCase):
    pred = LexiconEntry('', parse_formula('Lx.P(x)'), parse_type('<e, t>'))
    entity = LexiconEntry('', Var('me'), TYPE_ENTITY)

    def test_saturate_predicate(self):
        self.assertTrue(can_combine(self.pred, self.entity))
        self.assertTupleEqual(
            combine(self.pred, self.entity),
            LexiconEntry(
                ' ',
                Call(self.pred.denotation, self.entity.denotation),
                TYPE_TRUTH_VALUE
            )
        )

    def test_combine_every_child(self):
        every = TEST_LEXICON['every']
        child = TEST_LEXICON['child']
        self.assertTupleEqual(
            combine(every, child),
            LexiconEntry(
                'every child',
                Call(every.denotation, child.denotation),
                ComplexType(TYPE_ET, TYPE_TRUTH_VALUE)
            )
        )

    def test_can_combine_is_good(self):
        self.assertTrue(can_combine(TEST_LEXICON['is'], TEST_LEXICON['good']))

    def test_mismatched_types(self):
        self.assertFalse(can_combine(self.pred, self.pred))
        self.assertFalse(can_combine(self.entity, self.pred))
        self.assertFalse(can_combine(self.entity, self.entity))


class SimplifierTest(unittest.TestCase):
    def test_simplify_call(self):
        tree = Call(
            Lambda('x', Var('x')),
            Var('j')
        )
        self.assertTupleEqual(
            tree.simplify(),
            Var('j')
        )

    def test_simplify_nested_call(self):
        # (Lx.Ly.x & y)(a)(b) -> a & b
        tree = Call(
            Call(
                Lambda(
                    'x',
                    Lambda(
                        'y',
                        And(Var('x'), Var('y'))
                    )
                ),
                Var('a')
            ),
            Var('b')
        )
        self.assertTupleEqual(
            tree.simplify(),
            And(Var('a'), Var('b'))
        )

    def test_simplify_call_with_lambda_arg(self):
        # (LP.P(x))(Lx.x | a) -> x | a
        tree = Call(
            Lambda(
                'P',
                Call(Var('P'), Var('x'))
            ),
            Lambda(
                'x',
                Or(Var('x'), Var('a'))
            )
        )
        self.assertTupleEqual(
            tree.simplify(),
            Or(Var('x'), Var('a'))
        )

    def test_simplify_super_nested_call(self):
        # (LP.P(a, b))(Lx.Ly.x & y) -> a & b
        tree = Call(
            Lambda(
                'P',
                Call(Call(Var('P'), Var('a')), Var('b'))
            ),
            Lambda(
                'x',
                Lambda(
                    'y',
                    And(Var('x'), Var('y'))
                )
            )
        )
        self.assertTupleEqual(
            tree.simplify(),
            And(Var('a'), Var('b'))
        )

    def test_simplify_every_child(self):
        # (LP.LQ.Ax.P(x) -> Q(x))(Lx.Child(x)) -> LQ.Ax.Child(x) -> Q(x)
        tree = Call(
            TEST_LEXICON['every'].denotation,
            TEST_LEXICON['child'].denotation
        )
        self.assertTupleEqual(
            tree.simplify(),
            Lambda(
                'Q',
                ForAll(
                    'x',
                    IfThen(
                        Call(Var('Child'), Var('x')),
                        Call(Var('Q'), Var('x'))
                    )
                )
            )
        )


class LexiconLoaderTest(unittest.TestCase):
    def test_load_lexicon(self):
        lexicon = load_lexicon({
            'John': {
                'd': 'j',
                't': 'e',
            },
            'good': {
                'd': 'Lx.Good(x)',
                't': 'et',
            },
        })
        self.assertDictEqual(
            lexicon,
            {
                'John': LexiconEntry(
                    'John', parse_formula('j'), parse_type('e')
                ),
                'good': LexiconEntry(
                    'good',
                    parse_formula('Lx.Good(x)'),
                    parse_type('et')
                ),
            }
        )

    def test_missing_denotation_field(self):
        with self.assertRaisesRegex(LexiconError, r'.*John.*'):
            load_lexicon({'John': {'t': 'e'}})

    def test_missing_type_field(self):
        with self.assertRaisesRegex(LexiconError, r'.*John.*'):
            load_lexicon({'John': {'d': 'j'}})

    def test_invalid_denotation_formula(self):
        with self.assertRaisesRegex(LexiconError, r'.*John.*'):
            load_lexicon({'John': {'d': '???', 't': 'e'}})

    def test_invalid_type(self):
        with self.assertRaisesRegex(LexiconError, r'.*John.*'):
            load_lexicon({'John': {'d': 'j', 't': '???'}})
