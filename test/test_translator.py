import json
import os
import unittest

from montague.formula import (
    AllNode, AndNode, CallNode, ExistsNode, LambdaNode, OrNode, TypeNode,
    VarNode, parse_formula, parse_type, semtype,
)
from montague.translator import (
    LexiconEntry, can_combine, combine, replace_variable, translate_sentence,
)


test_lexicon = {
  "bad": LexiconEntry(
    LambdaNode('x', CallNode('Bad', [VarNode('x')])),
    TypeNode(semtype.ENTITY, semtype.TRUTH_VALUE),
  ),
  "is": LexiconEntry(
    LambdaNode('P', VarNode('P')),
    TypeNode(
            TypeNode(semtype.ENTITY, semtype.TRUTH_VALUE),
            TypeNode(semtype.ENTITY, semtype.TRUTH_VALUE),
    ),
  ),
  "good": LexiconEntry(
    LambdaNode('x', CallNode('Good', [VarNode('x')])),
    TypeNode(semtype.ENTITY, semtype.TRUTH_VALUE),
  ),
  "John": LexiconEntry(VarNode('j'), semtype.ENTITY),
}


class TranslatorTest(unittest.TestCase):
    def test_is_good(self):
        tree = translate_sentence('is good', test_lexicon)
        self.assertEqual(tree, LexiconEntry(
            LambdaNode('x', CallNode('Good', [VarNode('x')])),
            TypeNode(semtype.ENTITY, semtype.TRUTH_VALUE)
        ))

    def test_john_is_good(self):
        tree = translate_sentence('John is good', test_lexicon)
        self.assertEqual(tree, LexiconEntry(
            CallNode('Good', [VarNode('j')]),
            semtype.TRUTH_VALUE
        ))

    def test_john_is_bad(self):
        tree = translate_sentence('John is bad', test_lexicon)
        self.assertEqual(tree, LexiconEntry(
            CallNode('Bad', [VarNode('j')]),
            semtype.TRUTH_VALUE
        ))


class CombinerTest(unittest.TestCase):
    pred = LexiconEntry(
        parse_formula('Lx.P(x)'),
        parse_type('<e, t>')
    )
    entity = LexiconEntry(VarNode('me'), semtype.ENTITY)

    def test_saturate_predicate(self):
        self.assertTrue(can_combine(self.pred, self.entity))
        saturated = combine(self.pred, self.entity)
        self.assertEqual(saturated.type, semtype.TRUTH_VALUE)
        self.assertEqual(saturated.denotation, CallNode('P', [VarNode('me')]))

    def test_can_combine_is_good(self):
        self.assertTrue(can_combine(test_lexicon['is'], test_lexicon['good']))

    def test_mismatched_types(self):
        self.assertFalse(can_combine(self.pred, self.pred))
        self.assertFalse(can_combine(self.entity, self.pred))
        self.assertFalse(can_combine(self.entity, self.entity))


class ReplacerTest(unittest.TestCase):
    def test_simple_replace_variable(self):
        replaced = replace_variable(VarNode('x'), 'x', VarNode('y'))
        self.assertEqual(replaced, VarNode('y'))

    def test_replace_variable_in_and_or(self):
        tree = AndNode(OrNode(VarNode('x'), VarNode('y')), VarNode('z'))
        replaced = replace_variable(tree, 'x', VarNode('x\''))
        self.assertEqual(replaced,
            AndNode(
                OrNode(VarNode('x\''), VarNode('y')),
                VarNode('z')
            )
        )

    def test_replace_variable_in_quantifiers(self):
        tree = AllNode('x',
            OrNode(
                AndNode(
                    AllNode('b', VarNode('b')),
                    ExistsNode('b', VarNode('b')),
                ),
                ExistsNode('y', VarNode('b'))
            )
        )
        replaced = replace_variable(tree, 'b', VarNode('bbb'))
        self.assertEqual(replaced, AllNode('x',
            OrNode(
                AndNode(
                    AllNode('b', VarNode('b')),
                    ExistsNode('b', VarNode('b')),
                ),
                ExistsNode('y', VarNode('bbb'))
            )
        ))


    def test_recursive_replace_variable(self):
        tree = CallNode('BFP', [
            VarNode('x'),
            LambdaNode('x', VarNode('x')),  # This 'x' should not be replaced.
            AndNode(VarNode('x'), VarNode('y')),
        ])
        tree = replace_variable(tree, 'x', VarNode('j'))
        self.assertEqual(tree, CallNode('BFP', [
            VarNode('j'),
            LambdaNode('x', VarNode('x')),
            AndNode(VarNode('j'), VarNode('y')),
        ]))
