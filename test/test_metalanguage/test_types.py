import unittest

from montague.metalanguage.types import TypeNode, parse_type, semtype

from lark.exceptions import LarkError


class TypeParseTest(unittest.TestCase):
    def test_parsing_atomic_types(self):
        tree = parse_type('e')
        self.assertEqual(tree, semtype.ENTITY)
        tree = parse_type('t')
        self.assertEqual(tree, semtype.TRUTH_VALUE)
        tree = parse_type('v')
        self.assertEqual(tree, semtype.EVENT)

    def test_parsing_compound_type(self):
        tree = parse_type('<e, t>')
        self.assertEqual(tree, TypeNode(semtype.ENTITY, semtype.TRUTH_VALUE))

    def test_parsing_abbreviated_compound_types(self):
        tree = parse_type('et')
        self.assertEqual(tree, TypeNode(semtype.ENTITY, semtype.TRUTH_VALUE))
        tree = parse_type('vt')
        self.assertEqual(tree, TypeNode(semtype.EVENT, semtype.TRUTH_VALUE))

    def test_parsing_big_compound_type(self):
        tree = parse_type('<<e, t>, <e, <e, t>>>')
        self.assertEqual(tree, TypeNode(
            TypeNode(
                semtype.ENTITY,
                semtype.TRUTH_VALUE
            ),
            TypeNode(
                semtype.ENTITY,
                TypeNode(
                    semtype.ENTITY,
                    semtype.TRUTH_VALUE
                )
            )
        ))


class ParseErrorTest(unittest.TestCase):
    def test_missing_opening_bracket(self):
        with self.assertRaises(LarkError):
            parse_type('e, t>')

    def test_missing_closing_bracket(self):
        with self.assertRaises(LarkError):
            parse_type('<e, t')

    def test_trailing_input(self):
        with self.assertRaises(LarkError):
            parse_type('<e, t> e')

    def test_missing_comma(self):
        with self.assertRaises(LarkError):
            parse_type('<e t>')

    def test_missing_output_type(self):
        with self.assertRaises(LarkError):
            parse_type('<e>')

    def test_invalid_abbreviation(self):
        with self.assertRaises(LarkError):
            parse_type('evt')

    def test_invalid_letter(self):
        with self.assertRaises(LarkError):
            parse_type('b')
