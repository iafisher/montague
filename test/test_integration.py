from montague.interpreter import WorldModel, interpret_formula
from montague.translator import translate_sentence


John = object()
Mary = object()


test_model = WorldModel(
    set([John, Mary]),
    {
        "john": John,
        "mary": Mary,
        "Good": {John},
        "Bad": {Mary},
        "Man": {John},
        "Human": {Mary, John},
        "Alien": set(),
    },
)


def test_john_is_good_is_true(lexicon):
    nodes = translate_sentence("John is good", lexicon)

    assert len(nodes) == 1
    assert interpret_formula(nodes[0].formula, test_model)


def test_john_is_bad_is_false(lexicon):
    nodes = translate_sentence("John is bad", lexicon)

    assert len(nodes) == 1
    assert not interpret_formula(nodes[0].formula, test_model)
