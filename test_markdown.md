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

# 空行 n 個の挙動
scb でいう以下のようなケースを、どう表現すればいいか

```scb
段落

段落 差1


段落 差2



段落 差3
```

## pattern1: br連結
段落

<br>段落 差1

<br><br>段落 差2

<br><br><br>段落 差3

## :x: pattern2: br連結、ただし空行なし （上手くいかない）
段落
<br>段落 差1
<br><br>段落 差2
<br><br><br>段落 差3

## :x: pattern3: br使わずに（上手くいかない（空行n個は1個に凝縮されるので
段落


段落 差1




段落 差2






段落 差3

## pattern4: 空行区切りマンな書き方で pattern1 を再現
段落

<br>

段落 差1

<br>

<br>

段落 差2

<br>

<br>

<br>

段落 差3

# block in the list をどうやって表現するか
以下のようなリスト中のブロックは、markdownでは表現できない

```scb
hello world
 pythonの例
  code:python
   print('hello world.!')
   
   # python2だとこうだよ
   print 'hello world.!'
  まあpython2は今どき見ることないと思うので気にしなくていいけど
 jsの例
  code:js
   console.log('hello world.!')
  console.logと打つのがだるい？ならこうすればいいじゃない
   code:js
    // エイリアス設定して
    c = console.log
    
    // エイリアスを使う
    c('hello world.!')
 以上、hello worldでした。いかがでしたか？
```

## pattern1: ゼロインデントにしつつ、空行をはさむ（nインデントのリストも全部1インデントになってしまう）
hello world

- pythonの例

```python
print('hello world.!')

# python2だとこうだよ
print 'hello world.!'
```

    - まあpython2は今どき見ることないと思うので気にしなくていいけど
- jsの例

```javascript
console.log('hello world.!')
```

    - console.logと打つのがだるい？ならこうすればいいじゃない

```javascript
// エイリアス設定して
c = console.log

// エイリアスを使う
c('hello world.!')
```

- 以上、hello worldでした。いかがでしたか？

## pattern2: 1インデント化を防ぐためにダミーリストを入れる(省略を想起する`...`を使ってみる)
hello world

- pythonの例

```python
print('hello world.!')

# python2だとこうだよ
print 'hello world.!'
```

- ...
    - まあpython2は今どき見ることないと思うので気にしなくていいけど
- jsの例

```javascript
console.log('hello world.!')
```

- ...
    - console.logと打つのがだるい？ならこうすればいいじゃない

```javascript
// エイリアス設定して
c = console.log

// エイリアスを使う
c('hello world.!')
```

- 以上、hello worldでした。いかがでしたか？
