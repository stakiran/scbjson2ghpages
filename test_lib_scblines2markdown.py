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

        self.assertFalse(state.is_in_code_block())
        self.assertFalse(state.is_in_table_block())

        # ブロックはネストしない
        state.enter(mode_code, 1)
        with self.assertRaises(RuntimeError):
            state.enter(mode_code, 2)

class TestInBlockStateUser(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test(self):
        user = LIB.InBlockStateUser()

        testdata = '''title
段落段落
段落段落段落 ★2 not justnow
code:py ★3
 import os ★4
 for var in os.environ:
     print(var) ★6
ここはコードじゃない ★7 justnow/just_from_codeblock_now

block in the list ★9
 list1
  list2
   list3
    list4
    code:py ★14
     import os ★15
     for var in os.environ:
         print(var) ★17
         if len(var)<=4:
             print('4文字以内の変数だよ!') ★19
         #ここはまだコード ★20
     #ここはまだコード ★21 not just_from_codeblock_now
    ここはコードじゃない ★22 justnow/just_from_codeblock_now
    list4 ★23 not justnow/not just_from_codeblock_now
   list3
  list2
 list1
おしまい'''

        def pair(index):
            line = testdata_lines[index]
            cur_indentdepth = LIB.count_indentdepth(line)
            return [line, cur_indentdepth]

        testdata_lines = testdata.split('\n')

        for i,line in enumerate(testdata_lines):
            user.update(*pair(i))

            if i==2:
                self.assertFalse(user.state.is_in_block())
                self.assertFalse(user.is_left_just_now())
                continue

            if i==3:
                self.assertTrue(user.state.is_in_block())
                continue

            if i==4:
                self.assertTrue(user.state.is_in_block())
                self.assertTrue(user.state.is_in_code_block())
                self.assertFalse(user.state.is_in_table_block())
                continue

            if i==6:
                self.assertTrue(user.state.is_in_block())
                self.assertTrue(user.state.is_in_code_block())
                self.assertFalse(user.state.is_in_table_block())
                continue

            if i==7:
                self.assertFalse(user.state.is_in_block())
                self.assertTrue(user.is_left_just_now())
                self.assertTrue(user.is_left_from_codeblock_just_now())
                continue

            if i==14:
                self.assertTrue(user.state.is_in_block())
                self.assertTrue(user.state.is_in_code_block())
                self.assertFalse(user.state.is_in_table_block())
                continue

            if i==15:
                self.assertTrue(user.state.is_in_block())
                self.assertTrue(user.state.is_in_code_block())
                self.assertFalse(user.state.is_in_table_block())
                continue

            if i==17:
                self.assertTrue(user.state.is_in_block())
                self.assertTrue(user.state.is_in_code_block())
                self.assertFalse(user.state.is_in_table_block())
                continue

            if i==19:
                self.assertTrue(user.state.is_in_block())
                self.assertTrue(user.state.is_in_code_block())
                self.assertFalse(user.state.is_in_table_block())
                continue

            if i==20:
                self.assertTrue(user.state.is_in_block())
                self.assertTrue(user.state.is_in_code_block())
                self.assertFalse(user.state.is_in_table_block())
                continue

            if i==21:
                self.assertTrue(user.state.is_in_block())
                self.assertTrue(user.state.is_in_code_block())
                self.assertFalse(user.state.is_in_table_block())
                self.assertFalse(user.is_left_from_codeblock_just_now())
                continue

            if i==22:
                self.assertFalse(user.state.is_in_block())
                self.assertTrue(user.is_left_just_now())
                self.assertTrue(user.is_left_from_codeblock_just_now())
                continue

            if i==23:
                self.assertFalse(user.is_left_just_now())
                self.assertFalse(user.is_left_from_codeblock_just_now())
                continue

class TestLinkInDecoration(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_not_replaced(self):
        f = LIB._scb_to_markdown_in_line_about_link_in_decoration

        line = ''
        self.assertEqual(line, f(line))
        line = '[link]'
        self.assertEqual(line, f(line))
        line = '[* bold]'
        self.assertEqual(line, f(line))
        line = '[link][link]'
        self.assertEqual(line, f(line))

        line = '[link]`[- [in-literal]]`[link]'
        self.assertEqual(line, f(line))

        line = '`[- [in-literal]]`'
        self.assertEqual(line, f(line))

    def test_1_replaced(self):
        f = LIB._scb_to_markdown_in_line_about_link_in_decoration

        line = '[* [link]]'
        expect = '**[link]**'
        self.assertEqual(expect, f(line))

        line = '[- [link]]'
        expect = '~~[link]~~'
        self.assertEqual(expect, f(line))

        line = '[- [link]]xxx'
        expect = '~~[link]~~xxx'
        self.assertEqual(expect, f(line))

        line = 'xxx[- [link]]'
        expect = 'xxx~~[link]~~'
        self.assertEqual(expect, f(line))

        line = 'xxx[- [link]]xxx'
        expect = 'xxx~~[link]~~xxx'
        self.assertEqual(expect, f(line))

    def test_2_replaced(self):
        f = LIB._scb_to_markdown_in_line_about_link_in_decoration

        line = '[- [link]][- [link]]'
        expect = '~~[link]~~~~[link]~~'
        self.assertEqual(expect, f(line))

        line = '[- [link]]xxx[- [link]]'
        expect = '~~[link]~~xxx~~[link]~~'
        self.assertEqual(expect, f(line))

        line = 'xxx[- [link]]xxx[- [link]]'
        expect = 'xxx~~[link]~~xxx~~[link]~~'
        self.assertEqual(expect, f(line))

        line = '[- [link]]xxx[- [link]]xxx'
        expect = '~~[link]~~xxx~~[link]~~xxx'
        self.assertEqual(expect, f(line))

        line = 'xxx[- [link]]xxx[- [link]]xxx'
        expect = 'xxx~~[link]~~xxx~~[link]~~xxx'
        self.assertEqual(expect, f(line))

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

    def test_clear_indent_from_codeblock_line(self):
        f = LIB.clear_indent_from_codeblock_line

        # [scb]
        # code:py
        #  for _ in range(4):
        #      print('4 times.')
        # ^
        # ここを取り除きたい

        indentdepth = 0
        line   = ' for _ in range(4):'
        expect = 'for _ in range(4):'
        self.assertEqual(f(indentdepth, line), expect)

        indentdepth = 0
        line   = '     print(\'4 times.\')'
        expect = '    print(\'4 times.\')'
        self.assertEqual(f(indentdepth, line), expect)

        # [scb]
        # hoge
        #  list1
        #  code:py
        #   for _ in range(4):
        #       print('4 times.')
        # ^^

        indentdepth = 1
        line   = '  for _ in range(4):'
        expect = 'for _ in range(4):'
        self.assertEqual(f(indentdepth, line), expect)

        indentdepth = 1
        line   = '      print(\'4 times.\')'
        expect = '    print(\'4 times.\')'
        self.assertEqual(f(indentdepth, line), expect)

        # [scb]
        # hoge
        #  list1
        #   list2
        #    list3
        #    code:py
        #     for _ in range(4):
        #         print('4 times.')
        # ^^^^

        indentdepth = 3
        line   = '    for _ in range(4):'
        expect = 'for _ in range(4):'
        self.assertEqual(f(indentdepth, line), expect)

        indentdepth = 3
        line   = '        print(\'4 times.\')'
        expect = '    print(\'4 times.\')'
        self.assertEqual(f(indentdepth, line), expect)

if __name__ == '__main__':
    unittest.main()
