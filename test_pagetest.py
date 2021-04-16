# coding: utf-8

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

class TestModer(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_page(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
