import unittest
from unittest.mock import patch

from montague.formula import (
    Call, ComplexType, Lambda, Var, TYPE_ENTITY, TYPE_TRUTH_VALUE,
)
from montague.montague import ShellState, execute_command, HELP_MESSAGE
from montague.translator import LexiconEntry


TEST_LEXICON = {
  "good": LexiconEntry(
      Lambda('x', Call(Var('Good'), Var('x'))),
      ComplexType(TYPE_ENTITY, TYPE_TRUTH_VALUE)
  ),
}


class MontagueShellTest(unittest.TestCase):
    def setUp(self):
        self.shell_state = ShellState(lexicon=TEST_LEXICON)

    def test_command_help(self):
        response = execute_command('!help', self.shell_state)
        self.assertIn(HELP_MESSAGE, response)
        self.assertIn('currently in ' + self.shell_state.mode, response)

    def test_command_mode(self):
        response = execute_command('!mode', self.shell_state)
        self.assertIn(self.shell_state.mode, response)

    def test_command_switch_mode(self):
        response = execute_command('!mode translate', self.shell_state)
        self.assertIn('translate', response)
        self.assertEqual(self.shell_state.mode, 'translate')

    def test_switch_to_unrecognized_mode(self):
        old_mode = self.shell_state.mode
        response = execute_command('!mode bolivia', self.shell_state)
        self.assertIn('bolivia is not a recognized mode', response)
        self.assertEqual(self.shell_state.mode, old_mode)

    @patch('montague.montague.translate_sentence')
    def test_display_formula(self, mock_translate_sentence):
        mock_translate_sentence.return_value = LexiconEntry(
            Call(Var('Good'), Var('j')),
            TYPE_TRUTH_VALUE
        )
        response = execute_command('John is good', self.shell_state)
        self.assertIn('Denotation: Good(j)', response)
        self.assertIn('Type: t', response)

    def test_unrecognized_command(self):
        response = execute_command('!paraguay', self.shell_state)
        self.assertEqual('Unrecognized command paraguay.', response)
