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
[* 太字]や[** 太字]や[*** 太字]、あと普段使わないけど[/ 斜体]に[- 打ち消し線]
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

    def test_get_linkee_pagenames_and_remove_ghost(self):
        f = main.LinkConstructor.get_linkee_pagenames

        expect = ['リンク', 'リンク', 'リンク', 'スペースを ふくむページへのリンク', '存在しないリンク', 'hash1', 'hash2', 'hash2', 'hash3']
        actual = f(testdata_various_link)
        self.assertEqual(expect, actual)
        actual_duplicated_pagenames = actual

        expect = sorted(['リンク', 'スペースを ふくむページへのリンク', '存在しないリンク', 'hash1', 'hash2', 'hash3'])
        actual = sorted(main.remove_duplicates_in_list(actual_duplicated_pagenames))
        self.assertEqual(expect, actual)
        actual_sorted_and_no_duplicated_pagenames = actual

        # exist_pagenames にないページは省かれるはず
        exist_pagenames = sorted(['リンク', 'スペースを ふくむページへのリンク', 'hash1', 'hash3'])
        exist_pagenames_by_dict = {}
        for elm in exist_pagenames:
            exist_pagenames_by_dict[elm] = ''
        expect = exist_pagenames
        actual = main.LinkConstructor.remove_ghost_page(actual_sorted_and_no_duplicated_pagenames, exist_pagenames_by_dict)
        self.assertEqual(expect, actual)

if __name__ == '__main__':
    unittest.main()
