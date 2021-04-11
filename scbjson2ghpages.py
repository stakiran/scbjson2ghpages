# encoding: utf-8

import datetime
import json
import os
import re
import sys

import lib_scblines2markdown

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

def ________Argument________():
    pass

def parse_arguments():
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument('-i', '--input', default=None, required=True,
        help='An input .json filename.')

    args = parser.parse_args()
    return args

def ________Main________():
    pass

MYFULLPATH = os.path.abspath(sys.argv[0])
MYDIR = os.path.dirname(MYFULLPATH)

if __name__ == '__main__':
    args = parse_arguments()

    filename = args.input
    s = file2str(filename)
    obj = str2obj(s)
    proj = Project(obj)
    seeker = PageSeeker(proj)

    # 当面は testdata-for-to-markdown.json でテストする
    # https://scrapbox.io/testdata-for-to-markdown/
    #
    # まずはページ 'page' の to markdown を一通り
    page = seeker.get('page')

    scblines = page.lines
    markdown_lines = lib_scblines2markdown.convert(scblines)

    for line in markdown_lines:
        print(line)
