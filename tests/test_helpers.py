import unittest
from flatql.helpers import convert_pseudo_list, simple_rewrite

class TestDocument(unittest.TestCase):
    def test_simple_rewrite(self):
        result = simple_rewrite('aaa', 'bbb', {'test': 1})
        self.assertEqual(result, ('bbb', {'test': 1}))

    def test_convert_pseudo_list(self):
        input_data = {'items': {'#1': {'test': 1},
                                '#0': {'test': 0},
                                '#2': {'test':2},
                                '#3': {'test': 3}}}
        expected = {'items': [{'test': 0}, {'test': 1}, {'test': 2}, {'test': 3}]}
        result = convert_pseudo_list(input_data)
        self.assertEqual(result, expected)
