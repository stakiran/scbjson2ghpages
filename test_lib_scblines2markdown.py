# coding: utf-8

import unittest

import lib_scblines2markdown as LIB

class TestModer(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_blankline(self):
        f = LIB.Moder.is_blankline

        self.assertFalse(f(' '))
        self.assertFalse(f('\t'))
        self.assertFalse(f('a'))

        self.assertTrue(f(''))

    def test_is_list(self):
        f = LIB.Moder.is_list

        self.assertFalse(f('aaa'))
        self.assertFalse(f('[link]'))

        self.assertTrue(f(' list1'))
        self.assertTrue(f('\tlist1-タブ'))
        self.assertTrue(f('  list n-indent'))
        self.assertTrue(f('  \t \t  list n-indent mixture'))

    def test_is_start_of_code(self):
        f = LIB.Moder.is_start_of_code

        self.assertFalse(f(''))
        self.assertFalse(f('code:'))
        self.assertFalse(f('  code:'))
        self.assertFalse(f('table:xxx'))

        self.assertTrue(f('code:a'))
        self.assertTrue(f('code:js'))
        self.assertTrue(f('code:.js'))
        self.assertTrue(f('code:日本語ファイル名.js'))
        self.assertTrue(f('code:拡張子なし'))
        self.assertTrue(f('  code:javascript'))

    def test_is_start_of_table(self):
        f = LIB.Moder.is_start_of_table

        self.assertFalse(f(''))
        self.assertFalse(f('table:'))
        self.assertFalse(f('  table:'))
        self.assertFalse(f('code:xxx'))

        self.assertTrue(f('table:a'))
        self.assertTrue(f('table:aaa'))
        self.assertTrue(f('table:あいうえお'))
        self.assertTrue(f('  table:あいうえお'))

if __name__ == '__main__':
    unittest.main()
