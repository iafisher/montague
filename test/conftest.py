import json
import os

import pytest

from montague.translator import load_lexicon


@pytest.fixture(scope="session")
def lexicon():
    project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    fragment_path = os.path.join(project_dir, "montague", "resources", "fragment.json")
    with open(fragment_path) as f:
        return load_lexicon(json.load(f))
