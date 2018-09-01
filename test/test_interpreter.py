import unittest

from montague.ast import *
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
        'Man': set([John]),
        'Human': set([Mary, John]),
        'Alien': set([]),
    }
)


class InterpreterTest(unittest.TestCase):
    def test_john_is_good_is_true(self):
        formula = Call(Var('Good'), Var('j'))
        self.assertTrue(interpret_formula(formula, test_model))
        self.assertFalse(interpret_formula(Not(formula), test_model))

    def test_john_is_bad_is_false(self):
        formula = Call(Var('Bad'), Var('j'))
        self.assertFalse(interpret_formula(formula, test_model))
        self.assertTrue(interpret_formula(Not(formula), test_model))

    def test_mary_is_bad_and_john_is_good_is_true(self):
        formula = And(
            Call(Var('Bad'), Var('m')),
            Call(Var('Good'), Var('j'))
        )
        self.assertTrue(interpret_formula(formula, test_model))

    def test_everyone_is_bad_is_false(self):
        formula = ForAll('x', Call(Var('Bad'), Var('x')))
        self.assertFalse(interpret_formula(formula, test_model))

    def test_everyone_is_human_is_true(self):
        formula = ForAll('x', Call(Var('Human'), Var('x')))
        self.assertTrue(interpret_formula(formula, test_model))

    def test_someone_is_bad_is_true(self):
        formula = Exists('x', Call(Var('Bad'), Var('x')))
        self.assertTrue(interpret_formula(formula, test_model))

    def test_someone_is_alien_is_false(self):
        formula = Exists('x', Call(Var('Alien'), Var('x')))
        self.assertFalse(interpret_formula(formula, test_model))

    def test_the_man_is_john(self):
        formula = Iota('x', Call(Var('Man'), Var('x')))
        self.assertEqual(interpret_formula(formula, test_model), John)

    def test_the_man_is_good_is_true(self):
        formula = Call(Var('Good'), Iota('x', Call(Var('Man'), Var('x'))))
        self.assertTrue(interpret_formula(formula, test_model))

    def test_the_human_is_undefined(self):
        formula = Iota('x', Call(Var('Human'), Var('x')))
        self.assertEqual(interpret_formula(formula, test_model), None)
