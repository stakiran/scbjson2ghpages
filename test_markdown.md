# リスト中のリンクが正しく反映されない
- リンク
    - [Link](link.md)
    - [#hashtag](hashtag.md)
    - scrapbox link
        - [/sta](https://scrapbox.io/sta)
    - direct url
        - https://www.google.co.jp/
        - [textが後](https://scrapbox.io/sta/)
        - [textが先](https://scrapbox.io/sta/)
    - ====
    - scrapbox link
        - [sta](https://scrapbox.io/sta)
    - direct url
        - → https://www.google.co.jp/
        - [textが後](https://scrapbox.io/sta/)
        - [textが先](https://scrapbox.io/sta/)
    - ====
    - scrapbox link
        - aaa
        - [sta](https://scrapbox.io/sta)
    - direct url
        - あああ
        - → https://www.google.co.jp/
        - [textが後](https://scrapbox.io/sta/)
        - [textが先](https://scrapbox.io/sta/)
    - ====
    - scrapbox link
        - /sta
    - direct url
        - google.co.jp
    - ====
    - scrapboxLink
      - /sta
    - directUrl
      - google.co.jp

# リスト-段落の空行あるなしの表現の違いを表現したい
scb でいうこれは全部ニュアンスが違うので、markdown にも正確に落とし込みたい。特に塊はA～Fの7個ができるはず。

```scrapbox
段落書いて(A)
 リストをぶら下げる
 リストをぶら下げる

 リスト
 リスト
 リストを書いて
段落でしめる(B)

段落(C)

 空行を置いてリスト(D)

 空行を置いてリスト(E)

段落(F)
 リストをぶら下げる
```

## pattern1: 全部空行で区切った
段落書いて

- リストをぶら下げる
- リストをぶら下げる

- リスト
- リスト
- リストを書いて

段落でしめる

段落

- 空行を置いてリスト

- 空行を置いてリスト

段落

- リストをぶら下げる

## pattern2: 愚直に空行なくしてみた
段落書いて
- リストをぶら下げる
- リストをぶら下げる

- リスト
- リスト
- リストを書いて
段落でしめる

段落

- 空行を置いてリスト

- 空行を置いてリスト

段落
- リストをぶら下げる

## pattern3: 塊の区切りを空段落で頑張ってみる（スペースや空行だとダメなのでとりあえず `.`）
段落書いて

- リストをぶら下げる
- リストをぶら下げる

.

- リスト
- リスト
- リストを書いて

段落でしめる

.

段落

.

- 空行を置いてリスト

.

- 空行を置いてリスト

.

段落

- リストをぶら下げる

## pattern4: `<br>` で区切る
段落書いて

- リストをぶら下げる
- リストをぶら下げる

<br>

- リスト
- リスト
- リストを書いて

段落でしめる

<br>

段落

<br>

- 空行を置いてリスト

<br>

- 空行を置いてリスト

<br>

段落

- リストをぶら下げる
