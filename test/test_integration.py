import json
import os

import pytest

from montague.interpreter import WorldModel, interpret_formula
from montague.translator import load_lexicon, translate_sentence


John = object()
Mary = object()


test_model = WorldModel(
    set([John, Mary]),
    {
        "j": John,
        "m": Mary,
        "Good": {John},
        "Bad": {Mary},
        "Man": {John},
        "Human": {Mary, John},
        "Alien": set(),
    },
)


@pytest.fixture(scope="module")
def lexicon():
    project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    fragment_path = os.path.join(project_dir, "montague", "resources", "fragment.json")
    with open(fragment_path) as f:
        return load_lexicon(json.load(f))


def test_john_is_good_is_true(lexicon):
    node = translate_sentence("John is good", lexicon)
    assert interpret_formula(node.formula, test_model)


def test_john_is_bad_is_false(lexicon):
    node = translate_sentence("John is bad", lexicon)
    assert not interpret_formula(node.formula, test_model)
