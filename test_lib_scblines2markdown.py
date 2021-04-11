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

    def test_is_paragraph(self):
        f = LIB.Moder.is_paragraph

        self.assertFalse(f(''))
        self.assertFalse(f(' list'))
        self.assertFalse(f('code:xxx'))
        self.assertFalse(f('table:xxx'))
        self.assertFalse(f('  code:xxx'))
        self.assertFalse(f(' table:xxx'))

        self.assertTrue(f('1'))
        self.assertTrue(f('aa'))
        self.assertTrue(f('あいうえお'))

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

    def test_determin_mode(self):
        f = LIB.Moder.determin_mode
        m = LIB.MODE

        self.assertEqual(f(''), m.BLANKLINE)
        self.assertEqual(f('code'), m.PARAGRAPH)
        self.assertEqual(f(' code'), m.LIST)
        self.assertEqual(f(' code:xxx'), m.START_OF_BLOCK_CODE)

class TestInBlockState(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_valid(self):
        state = LIB.InBlockState()
        mode_code = LIB.MODE.START_OF_BLOCK_CODE
        mode_table = LIB.MODE.START_OF_BLOCK_TABLE

        self.assertFalse(state.is_in_block())

        state.enter(mode_code, 1)
        self.assertTrue(state.is_in_block())
        self.assertTrue(state.is_in_code_block())
        self.assertFalse(state.is_in_table_block())
        self.assertEqual(state.indentdepth_of_start, 1)

        state.leave()

        state.enter(mode_table, 3)
        self.assertTrue(state.is_in_block())
        self.assertFalse(state.is_in_code_block())
        self.assertTrue(state.is_in_table_block())
        self.assertEqual(state.indentdepth_of_start, 3)

    def test_invalid(self):
        state = LIB.InBlockState()
        mode_code = LIB.MODE.START_OF_BLOCK_CODE
        mode_table = LIB.MODE.START_OF_BLOCK_TABLE

        with self.assertRaises(RuntimeError):
            state.is_in_code_block()
        with self.assertRaises(RuntimeError):
            state.is_in_table_block()

        # ブロックはネストしない
        state.enter(mode_code, 1)
        with self.assertRaises(RuntimeError):
            state.enter(mode_code, 2)

class TestFuncs(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_count_indentdepth(self):
        f = LIB.count_indentdepth

        self.assertEqual(f('list'), 0)
        self.assertEqual(f(' list'), 1)
        self.assertEqual(f('  list'), 2)
        self.assertEqual(f('      list'), 6)

        self.assertEqual(f('   code:xxx'), 3)
        self.assertEqual(f('table:table1'), 0)

if __name__ == '__main__':
    unittest.main()
