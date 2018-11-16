from montague.ast import *
from montague.interpreter import WorldModel, interpret_formula, satisfiers


John = object()
Mary = object()


test_model = WorldModel(
    set([John, Mary]),
    {
        'j': John,
        'm': Mary,
        'Good': {John},
        'Bad': {Mary},
        'Man': {John},
        'Human': {Mary, John},
        'Alien': set(),
    },
)


def test_john_is_good_is_true():
    formula = Call(Var('Good'), Var('j'))
    assert interpret_formula(formula, test_model)
    assert not interpret_formula(Not(formula), test_model)


def test_john_is_bad_is_false():
    formula = Call(Var('Bad'), Var('j'))
    assert not interpret_formula(formula, test_model)
    assert interpret_formula(Not(formula), test_model)


def test_mary_is_bad_and_john_is_good_is_true():
    formula = And(Call(Var('Bad'), Var('m')), Call(Var('Good'), Var('j')))
    assert interpret_formula(formula, test_model)


def test_everyone_is_bad_is_false():
    formula = ForAll('x', Call(Var('Bad'), Var('x')))
    assert not interpret_formula(formula, test_model)


def test_everyone_is_human_is_true():
    formula = ForAll('x', Call(Var('Human'), Var('x')))
    assert interpret_formula(formula, test_model)


def test_someone_is_bad_is_true():
    formula = Exists('x', Call(Var('Bad'), Var('x')))
    assert interpret_formula(formula, test_model)


def test_someone_is_alien_is_false():
    formula = Exists('x', Call(Var('Alien'), Var('x')))
    assert not interpret_formula(formula, test_model)


def test_the_man_is_john():
    formula = Iota('x', Call(Var('Man'), Var('x')))
    assert interpret_formula(formula, test_model) == John


def test_the_man_is_good_is_true():
    formula = Call(Var('Good'), Iota('x', Call(Var('Man'), Var('x'))))
    assert interpret_formula(formula, test_model)


def test_the_human_is_undefined():
    formula = Iota('x', Call(Var('Human'), Var('x')))
    assert interpret_formula(formula, test_model) is None


def test_satisfiers_good_set():
    sset = satisfiers(Call(Var('Good'), Var('x')), test_model, 'x')
    assert sset == {John}


def test_satisfiers_bad_set():
    sset = satisfiers(Call(Var('Bad'), Var('x')), test_model, 'x')
    assert sset == {Mary}


def test_satisfiers_human_set():
    sset = satisfiers(Call(Var('Human'), Var('x')), test_model, 'x')
    assert sset == {John, Mary}


def test_satisfiers_alien_set():
    sset = satisfiers(Call(Var('Alien'), Var('x')), test_model, 'x')
    assert sset == set()


def test_satisfiers_does_not_overwrite_assignment():
    model = WorldModel({Mary}, {'j': John})
    satisfiers(Var('j'), model, 'j')
    assert model.assignments['j'] == John


def test_satisfiers_does_not_create_assignment():
    satisfiers(Var('j'), test_model, 'some_nonexistent_variable')
    assert 'some_nonexistent_variable' not in test_model.assignments
