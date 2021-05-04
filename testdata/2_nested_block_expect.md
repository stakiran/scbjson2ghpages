ネストリスト中のコードブロック

- ネスト1
    - ネスト2
        - 前後のリストは

```python
# ネスト3
import os

print(os.environ)
```

- ...
    - ...
        - もちろん維持されます（深さ含めて）
    - ネスト2続き

```python
# ネスト2同列
import os

print(os.environ)
```

- ネスト1

<br>

ネストリスト中のテーブル

- ネスト1
    - table:てーぶる

| a | b | c |
| - | - | - |
| e | 1 | 2 |
| f | 3 | 4 |

- ...
    - table:テーブル

|  | 重要 | 重要でない |
| - | - | - |
| 緊急 |  |  |
| 緊急でない |  |  |

<br>

code codeやらcode tableやらのパターン

- nest1
    - code code

```py
print('a')
print('A')
```

- ...
    - ...

```js
console.log('b')
```

- ...
    - code table

```py
print('a')
print('A')
```

- ...
    - ...
        - table:table1

| a | b |
| - | - |
| c | d |

- ...
    - table code
        - table:table1

| a | b |
| - | - |
| c | d |

- ...
    - ...

```py
print('a')
print('A')
```

- ...
    - table table
        - table:table1

| a | b |
| - | - |
| c | d |

- ...
    - ....
        - table:table2

| A | B |
| - | - |
| C | D |

<br>

