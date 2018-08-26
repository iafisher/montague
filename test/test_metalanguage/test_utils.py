import unittest

from montague.metalanguage.utils import IteratorWithMemory, Token


class IteratorWithMemoryTest(unittest.TestCase):
    def test_next_and_push(self):
        L = [1, 2, 3]
        it = IteratorWithMemory(iter(L))
        self.assertEqual(1, next(it))
        it.push(7)
        self.assertEqual(7, next(it))
        self.assertEqual(2, next(it))
