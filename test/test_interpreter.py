import unittest

from montague.formula import (
    AllNode, AndNode, CallNode, ExistsNode, NotNode, VarNode,
)
from montague.interpreter import WorldModel, interpret_formula


John = object()
Mary = object()


test_model = WorldModel(
    set([John, Mary]),
    {
        'j': John,
        'm': Mary,
        'Good': set([John]),
        'Bad': set([Mary]),
        'Human': set([Mary, John]),
        'Alien': set([]),
    }
)


class InterpreterTest(unittest.TestCase):
    def test_john_is_good_is_true(self):
        formula = CallNode(VarNode('Good'), VarNode('j'))
        self.assertTrue(interpret_formula(formula, test_model))
        self.assertFalse(interpret_formula(NotNode(formula), test_model))

    def test_john_is_bad_is_false(self):
        formula = CallNode(VarNode('Bad'), VarNode('j'))
        self.assertFalse(interpret_formula(formula, test_model))

    def test_mary_is_bad_and_john_is_good_is_true(self):
        formula = AndNode(
            CallNode(VarNode('Bad'), VarNode('m')),
            CallNode(VarNode('Good'), VarNode('j'))
        )
        self.assertTrue(interpret_formula(formula, test_model))

    def test_everyone_is_bad_is_false(self):
        formula = AllNode('x', CallNode(VarNode('Bad'), VarNode('x')))
        self.assertFalse(interpret_formula(formula, test_model))

    def test_everyone_is_human_is_true(self):
        formula = AllNode('x', CallNode(VarNode('Human'), VarNode('x')))
        self.assertTrue(interpret_formula(formula, test_model))

    def test_someone_is_bad_is_true(self):
        formula = ExistsNode('x', CallNode(VarNode('Bad'), VarNode('x')))
        self.assertTrue(interpret_formula(formula, test_model))

    def test_someone_is_alien_is_false(self):
        formula = ExistsNode('x', CallNode(VarNode('Alien'), VarNode('x')))
        self.assertFalse(interpret_formula(formula, test_model))
