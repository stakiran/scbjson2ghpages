# coding: utf-8

import os
import unittest

import scbjson2ghpages as main

testdata_various_link = '''
o
[リンク]
[リンク]と[リンク]
[スペースを ふくむページへのリンク]
[存在しないリンク] これは後続の「当該ページ名を持つページが実際に存在するか判定」で弾く
#hash1 は問題なく #hash2 #hash2 検出されるはず #hash3

x
hash#ここは検出されない
`[りんく]` `#hash`
[* 太字]
[**** 太字]
[- 斜体]
[/sta]
[http://www.google.co.jp google(text後)]
[google(text前) http://www.google.co.jp]
[https://gyazo.com/505861e8a5c21ae87eb972c4affd8841]
[sta.icon]
[sta.icon*3]

end'''

class TestLinkContruction(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_linkee_pagenames(self):
        f = main.LinkConstructor.get_linkee_pagenames

        expect = ['リンク', 'リンク', 'リンク', 'スペースを ふくむページへのリンク', '存在しないリンク', 'hash1', 'hash2', 'hash2', 'hash3']
        actual = f(testdata_various_link)
        self.assertEqual(expect, actual)

        expect = ['リンク', 'スペースを ふくむページへのリンク', '存在しないリンク', 'hash1', 'hash2', 'hash3'].sort()
        actual = main.remove_duplicates_in_list(actual).sort()
        self.assertEqual(expect, actual)

if __name__ == '__main__':
    unittest.main()
