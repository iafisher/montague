import json
import os
import unittest

from montague.formula import (
    AllNode, AndNode, CallNode, ExistsNode, IfNode, LambdaNode, OrNode,
    TypeNode, VarNode, parse_formula, parse_type, TYPE_ENTITY, TYPE_EVENT,
    TYPE_TRUTH_VALUE,
)
from montague.translator import (
    LexiconEntry, LexiconError, TranslationError, can_combine, combine,
    load_lexicon, translate_sentence,
)


TYPE_ET = TypeNode(TYPE_ENTITY, TYPE_TRUTH_VALUE)


TEST_LEXICON = {
  "bad": LexiconEntry(
      LambdaNode('x', CallNode(VarNode('Bad'), VarNode('x'))),
      TYPE_ET
  ),
  "is": LexiconEntry(
      LambdaNode('P', VarNode('P')),
      TypeNode(TYPE_ET, TYPE_ET)
  ),
  "good": LexiconEntry(
      LambdaNode('x', CallNode(VarNode('Good'), VarNode('x'))),
      TYPE_ET
  ),
  "every": LexiconEntry(
      LambdaNode(
          'P',
          LambdaNode(
              'Q',
              AllNode(
                  'x',
                  IfNode(
                      CallNode(VarNode('P'), VarNode('x')),
                      CallNode(VarNode('Q'), VarNode('x'))
                  )
              )
          )
      ),
      TypeNode(
          TYPE_ET,
          TypeNode(TYPE_ET, TYPE_TRUTH_VALUE)
      )
  ),
  "child": LexiconEntry(
      LambdaNode('x', CallNode(VarNode('Child'), VarNode('x'))),
      TYPE_ET
  ),
  "John": LexiconEntry(VarNode('j'), TYPE_ENTITY),
}


class TranslatorTest(unittest.TestCase):
    def test_is_good(self):
        self.assertTupleEqual(
            translate_sentence('is good', TEST_LEXICON),
            LexiconEntry(
                LambdaNode(
                    'x',
                    CallNode(VarNode('Good'), VarNode('x'))
                ),
                TYPE_ET
            )
        )

    def test_john_is_good(self):
        self.assertTupleEqual(
            translate_sentence('John is good', TEST_LEXICON),
            LexiconEntry(
                CallNode(VarNode('Good'), VarNode('j')),
                TYPE_TRUTH_VALUE
            )
        )

    def test_john_is_bad(self):
        self.assertTupleEqual(
            translate_sentence('John is bad', TEST_LEXICON),
            LexiconEntry(
                CallNode(VarNode('Bad'), VarNode('j')),
                TYPE_TRUTH_VALUE
            )
        )

    def test_every_child_is_good(self):
        self.assertTupleEqual(
            translate_sentence('every child is good', TEST_LEXICON),
            LexiconEntry(
                AllNode(
                    'x',
                    IfNode(
                        CallNode(VarNode('Child'), VarNode('x')),
                        CallNode(VarNode('Good'), VarNode('x'))
                    )
                ),
                TYPE_TRUTH_VALUE
            )
        )

    def test_translate_invalid_sentence(self):
        with self.assertRaises(TranslationError):
            translate_sentence('every John is good', TEST_LEXICON)

    def test_translate_unknown_word(self):
        with self.assertRaisesRegex(TranslationError, r'.*whorlious.*'):
            translate_sentence('John is whorlious', TEST_LEXICON)


class CombinerTest(unittest.TestCase):
    pred = LexiconEntry(parse_formula('Lx.P(x)'), parse_type('<e, t>'))
    entity = LexiconEntry(VarNode('me'), TYPE_ENTITY)

    def test_saturate_predicate(self):
        self.assertTrue(can_combine(self.pred, self.entity))
        self.assertTupleEqual(
            combine(self.pred, self.entity),
            LexiconEntry(
                CallNode(self.pred.denotation, self.entity.denotation),
                TYPE_TRUTH_VALUE
            )
        )

    def test_combine_every_child(self):
        every = TEST_LEXICON['every']
        child = TEST_LEXICON['child']
        self.assertTupleEqual(
            combine(every, child),
            LexiconEntry(
                CallNode(every.denotation, child.denotation),
                TypeNode(TYPE_ET, TYPE_TRUTH_VALUE)
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
        tree = CallNode(
            LambdaNode('x', VarNode('x')),
            VarNode('j')
        )
        self.assertTupleEqual(
            tree.simplify(),
            VarNode('j')
        )

    def test_simplify_nested_call(self):
        # (Lx.Ly.x & y)(a)(b) -> a & b
        tree = CallNode(
            CallNode(
                LambdaNode(
                    'x',
                    LambdaNode(
                        'y',
                        AndNode(VarNode('x'), VarNode('y'))
                    )
                ),
                VarNode('a')
            ),
            VarNode('b')
        )
        self.assertTupleEqual(
            tree.simplify(),
            AndNode(VarNode('a'), VarNode('b'))
        )

    def test_simplify_call_with_lambda_arg(self):
        # (LP.P(x))(Lx.x | a) -> x | a
        tree = CallNode(
            LambdaNode(
                'P',
                CallNode(VarNode('P'), VarNode('x'))
            ),
            LambdaNode(
                'x',
                OrNode(VarNode('x'), VarNode('a'))
            )
        )
        self.assertTupleEqual(
            tree.simplify(),
            OrNode(VarNode('x'), VarNode('a'))
        )

    def test_simplify_super_nested_call(self):
        # (LP.P(a, b))(Lx.Ly.x & y) -> a & b
        tree = CallNode(
            LambdaNode(
                'P',
                CallNode(CallNode(VarNode('P'), VarNode('a')), VarNode('b'))
            ),
            LambdaNode(
                'x',
                LambdaNode(
                    'y',
                    AndNode(VarNode('x'), VarNode('y'))
                )
            )
        )
        self.assertTupleEqual(
            tree.simplify(),
            AndNode(VarNode('a'), VarNode('b'))
        )

    def test_simplify_every_child(self):
        # (LP.LQ.Ax.P(x) -> Q(x))(Lx.Child(x)) -> LQ.Ax.Child(x) -> Q(x)
        tree = CallNode(
            TEST_LEXICON['every'].denotation,
            TEST_LEXICON['child'].denotation
        )
        self.assertTupleEqual(
            tree.simplify(),
            LambdaNode(
                'Q',
                AllNode(
                    'x',
                    IfNode(
                        CallNode(VarNode('Child'), VarNode('x')),
                        CallNode(VarNode('Q'), VarNode('x'))
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
                'John': LexiconEntry(parse_formula('j'), parse_type('e')),
                'good': LexiconEntry(
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
