# scbjson2ghpages
Scrapbox Exported JSON to Markdown for GitHub Pages.

## Demo
- ~~https://stakiran.github.io/scrapbox-sta/~~ NO LONGER MAINTAINED.

## How to use
Create and docs/*.md for ghpages.

```terminal
python scbjson2ghpages.py -i YOUR-EXPORTED-JSON.json
```

## How to test

```terminal
$ python test_lib_scblines2markdown.py
......................
----------------------------------------------------------------------
Ran 22 tests in 0.003s

OK

$ python test_pagetest.py
........
----------------------------------------------------------------------
Ran 8 tests in 0.032s

OK

$ python test_scbjson2ghpages.py
.
----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

About test_pagetest.py, Use testdata/ dir.

## LICENSE
[MIT](LICENSE)
