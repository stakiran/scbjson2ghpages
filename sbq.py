# encoding: utf-8

import datetime
import json
import os
import re
import sys

MYFULLPATH = os.path.abspath(sys.argv[0])
MYDIR = os.path.dirname(MYFULLPATH)

def ________Util________():
    pass

def file2str(filepath):
    ret = ''
    with open(filepath, encoding='utf8', mode='r') as f:
        ret = f.read()
    return ret

def str2obj(s):
    return json.loads(s)

def create_datetime_from_unixtime(number):
    return datetime.datetime.fromtimestamp(number)

def count_first_space_or_tab(s):
    count = 0
    for c in s:
        if c == '\t':
            count += 1
            continue
        if c == ' ':
            count += 1
            continue
        break
    return count

def dir_without_magics(obj):
    # See: https://www.askpython.com/python/examples/find-all-methods-of-class
    return [method for method in dir(obj) if not method.startswith('__')]

def ________Argument________():
    pass

def arguments_title(parser):
    parser.add_argument('title_and_pageMethod', nargs=2)

def arguments_substr(parser):
    parser.add_argument('--title', default=False, action='store_true')
    parser.add_argument('--lines', default=False, action='store_true')
    parser.add_argument('keyword_and_pageMethod', nargs=2)

def arguments_root(parser):
    parser.add_argument('-i', '--input', default=None, required=True,
        help='An input .json filename.')

    parser.add_argument('--list-methods', default=False, action='store_true')

def parse_arguments():
    import argparse

    parser_root = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser_root.add_subparsers(
        dest = 'subcommand'
    )

    arguments_root(parser_root)

    arguments_substr(subparsers.add_parser('substr'))
    arguments_title(subparsers.add_parser('title'))

    args = parser_root.parse_args()
    return args

def ________Wrapper________():
    pass


class Project:
    def __init__(self, obj):
        self._obj = obj

    @property
    def name(self):
        return self._obj['name']

    @property
    def display_name(self):
        return self._obj['displayName']

    @property
    def exported_by_unixtime(self):
        return self._obj['exported']

    @property
    def pages(self):
        return self._obj['pages']

    @property
    def exported_by_datetime(self):
        unixtime = self.exported_by_unixtime
        return create_datetime_from_unixtime(unixtime)

    def __str__(self):
        return '''/{name} {displayName}
exported at {exported}'''.format(
            name=self.name,
            displayName=self.display_name,
            exported=self.exported_by_datetime,
        )

class PageSeeker:
    def __init__(self, proj):
        self._proj = proj
        self._parse()

    def _parse(self):
        projname = self._proj.name
        pages = self._proj.pages

        self._page_insts = {}
        for page in pages:
            page_inst = Page(page, projname)
            title = page_inst.title
            self._page_insts[title] = page_inst

    def get(self, title):
        if not title in self._page_insts:
            raise RuntimeError('Not found page "{}".'.format(title))
        return self._page_insts[title]

    def find_partially_from_title(self, keyword):
        found_page_insts = []
        for title in self._page_insts:
            if not keyword in title:
                continue
            page_inst = self._page_insts[title]
            found_page_insts.append(page_inst)
        return found_page_insts

    def find_partially_from_lines(self, keyword):
        found_page_insts = []
        for title in self._page_insts:
            page_inst = self._page_insts[title]
            lines_by_string = page_inst.rawstring
            if not keyword in lines_by_string:
                continue
            found_page_insts.append(page_inst)
        return found_page_insts

class Page:
    def __init__(self, page_obj, project_name):
        self._project_name = project_name
        self._obj = page_obj

        self._lines_cache = []

    @property
    def title(self):
        return self._obj['title']

    @property
    def id(self):
        return self._obj['id']

    @property
    def created_by_unixtime(self):
        return self._obj['created']

    @property
    def updated_by_unixtime(self):
        return self._obj['updated']

    @property
    def created_by_datetime(self):
        unixtime = self.created_by_unixtime
        return create_datetime_from_unixtime(unixtime)

    @property
    def updated_by_datetime(self):
        unixtime = self.updated_by_unixtime
        return create_datetime_from_unixtime(unixtime)

    @property
    def _lines(self):
        return self._obj['lines']

    @property
    def lines(self):
        ''' 以下を実施
        - 先頭行は title に等しいのでカット
        - 行頭インデントを space に揃える'''
        if len(self._lines_cache) != 0:
            return self._lines_cache

        newlines = []

        lines = self._obj['lines']
        lines = lines[1:]

        for line in lines:
            # 上手い正規表現思いつかなかった...
            # r'^[\t ]+' を「マッチした文字数個の ' '」にreplaceしたいんだが...
            count = count_first_space_or_tab(line)
            newline = '{}{}'.format(
                ' '*count,
                line[count:]
            )
            newlines.append(newline)
        self._lines_cache = newlines
        return newlines

    @property
    def url(self):
        ''' encodingなし. ブラウザ側で対応してくれるはず. '''
        return 'https://scrapbox.io/{}/{}'.format(
            self._project_name,
            self.title,
        )

    @property
    def rawstring(self):
        lines = self.lines
        return '\n'.join(lines)

    def __str__(self):
        lines = self.lines
        lineHeads = '\n'.join(lines[:3])
        line_number = len(lines)
        return '''{title}
created at: {created}
updated at: {updated}
url: {url}
---
{lineHeads}...

total {lineNumber} lines. '''.format(
            title=self.title,
            created=self.created_by_datetime,
            updated=self.updated_by_datetime,
            url=self.url,
            lineHeads=lineHeads,
            lineNumber=line_number,
        )

def ________Main________():
    pass

# @todo
# - subcommand つくるところコピペが多いのでもうちょっと
#   - Project つくるところ
#   - do_xxx() を定義して, func_table で対応して...
# - エラーが例外そのまま投げてて不親切
# - 戻り値は do_xxx() から __main__ に返すべきでは

def do_without_subcommand(args):
    if args.list_methods:
        method_list = dir_without_magics(Page)
        for method in method_list:
            print(method)
        return

def do_substr(args):
    keyword, page_method = args.keyword_and_pageMethod

    use_title = args.title
    use_lines = args.lines

    if not use_title and not use_lines:
        raise RuntimeError('No valid option. You must give each of "title" or "lines".')

    filename = args.input
    s = file2str(filename)
    obj = str2obj(s)
    proj = Project(obj)

    seeker = PageSeeker(proj)

    if use_title:
        page_insts = seeker.find_partially_from_title(keyword)
    elif use_lines:
        page_insts = seeker.find_partially_from_lines(keyword)

    if len(page_insts) == 0:
        print('No match with keyword "{}"..'.format(keyword))
        return

    for page_inst in page_insts:
        returned_value = getattr(page_inst, page_method)
        print(returned_value)

def do_title(args):
    title, page_method = args.title_and_pageMethod

    filename = args.input
    s = file2str(filename)
    obj = str2obj(s)
    proj = Project(obj)

    seeker = PageSeeker(proj)
    page = seeker.get(title)

    returned_value = getattr(page, page_method)
    print(returned_value)

if __name__ == '__main__':
    args = parse_arguments()

    subcommand = args.subcommand
 
    if not subcommand:
        do_without_subcommand(args)
        sys.exit(0)
 
    func_table = {
        'substr' : do_substr,
        'title' : do_title,
    }
    if not subcommand in func_table:
        raise RuntimeError('No subcommand "{}", especially impl miss.'.format(subcommand))

    f = func_table[subcommand]
    f(args)
    sys.exit(0)
