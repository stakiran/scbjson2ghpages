# coding: utf-8

import os
import unittest

import scbjson2ghpages as MAIN
import lib_scblines2markdown as LIB

'''
ページ単位で変換の正しさをテストする.

Input:
  --page-to-scb オプションで .scb ファイルをつくる.
  この .scb ファイルを読み込む.
  わかりやすさのため, ファイル名は 1_(pagename)_input.scb

Expect:
  input に対して, こうなるべきという答えを手作業で書いておく.
  ファイル名は 2_(pagename)_expect.md

Actual:
  input を使って lib_scblines2markdown.convert_stepX() に食わせた後の値.
  ファイル名は 3_(pagename)_actual_step(X).md

How to test:
  Expect と Actual が一致するかを調べる.
  一致しない場合, どこが違うかは WinMerge など手作業で調べる.
'''

def file2list(filepath):
    ret = []
    with open(filepath, encoding='utf8', mode='r') as f:
        ret = [line.rstrip('\n') for line in f.readlines()]
    return ret

TESTDATA_DIRECTORY = 'testdata'

class TestModer(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _test_onepage(self, pagename):
        in_filepath = os.path.join(TESTDATA_DIRECTORY, '1_{}_input.scb'.format(pagename))
        expect_filepath = os.path.join(TESTDATA_DIRECTORY, '2_{}_expect.md'.format(pagename))
        out1_filepath = os.path.join(TESTDATA_DIRECTORY, '3_{}_actual_step1.md'.format(pagename))
        out2_filepath = os.path.join(TESTDATA_DIRECTORY, '3_{}_actual_step2.md'.format(pagename))
        out3_filepath = os.path.join(TESTDATA_DIRECTORY, '3_{}_actual_step3.md'.format(pagename))
        actual_filepath = out3_filepath

        scblines = file2list(in_filepath)
        step1_converted_lines = LIB.convert_step1(scblines)
        MAIN.list2file(out1_filepath, step1_converted_lines)
        step2_converted_lines = LIB.convert_step2(step1_converted_lines)
        MAIN.list2file(out2_filepath, step2_converted_lines)
        markdown_lines = LIB.convert_step3(step2_converted_lines)
        MAIN.list2file(actual_filepath, markdown_lines)
        actual_lines = markdown_lines

        expect_lines = file2list(expect_filepath)

        LB = '\n'
        actual_contents = LB.join(actual_lines)
        expect_contents = LB.join(expect_lines)
        self.assertEqual(expect_contents, actual_contents)

        LIB.dp_all_off()

    def test_page(self):
        self._test_onepage('page')

    def test_image(self):
        self._test_onepage('image')

    def test_codeblock(self):
        self._test_onepage('codeblock')

    def test_table(self):
        self._test_onepage('table')

    def test_nestedblock(self):
        LIB.DP_scb_to_markdown_in_line = True
        self._test_onepage('nested_block')

if __name__ == '__main__':
    unittest.main()
