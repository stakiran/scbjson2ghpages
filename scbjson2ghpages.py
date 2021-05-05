# encoding: utf-8

import copy
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

def list2file(filepath, ls):
    with open(filepath, encoding='utf8', mode='w') as f:
        f.writelines(['{:}\n'.format(line) for line in ls] )

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

def today_datetimestr():
    todaydt = datetime.datetime.today()
    datestr = todaydt.strftime('%Y/%m/%d')
    timestr = todaydt.strftime('%H:%M:%S')

    wd =  todaydt.weekday()
    dow_j = ['月',"火", "水", "木","金","土","日"][wd]
    dow_e = ['Mon',"Tue","Wed","Thu","Fri","Sat","Sun"][wd]

    return '{}({}) {}'.format(datestr, dow_j, timestr)

def remove_duplicates_in_list(ls):
    return list(set(ls))

def ________LinkConstructor________():
    pass

RE_LITERAL = re.compile(r'`(.+?)`')
RE_SPECIAL_BRACKET = re.compile(r'\[[\*\-\/](.+?)\]')
RE_LINK_URL_OR_URL_FRONT = re.compile(r'\[(http)(s){0,1}(\:\/\/)(.+?)\]')
RE_LINK_URL_BACK = re.compile(r'\[(.+?)( )(http)(s){0,1}(\:\/\/)(.+?)\]')
RE_ICON = '\[(.+?)\.icon(\*[0-9]+){0,1}\]'
RE_HASHTAG = re.compile(r'[ ^\n\r]#(.+?)[ $\n\r]')
RE_LINK_ANOTHER_PAGE = re.compile(r'\[(.+?)\]')
class LinkConstructor:
    @staticmethod
    def get_linkee_pagenames(s):
        NO_MATCH = []
        work = s

        is_blank_line = len(work)==0
        if is_blank_line:
            return NO_MATCH

        not_found_bracket = work.find('[') == -1
        if not_found_bracket:
            return NO_MATCH

        work = re.sub(RE_LITERAL, '', work)
        work = re.sub(RE_SPECIAL_BRACKET, '', work)
        work = re.sub(RE_LINK_URL_OR_URL_FRONT, '', work)
        work = re.sub(RE_LINK_URL_BACK, '', work)
        work = re.sub(RE_ICON, '', work)

        pagenames = []

        # link
        # ----

        def repl(match_object):
            groups = match_object.groups()
            if len(groups)==0:
                return
            for group in groups:
                pagename = group
                pagenames.append(pagename)
            return
        re.sub(RE_LINK_ANOTHER_PAGE, repl, work)

        # hashtag
        # -------

        # aaa #hash #hash aaa
        #    ^^^^^^^
        #           ^
        #         連続する場合の後半の開始がこうなるせいで
        #         RE_HASHTAG ではキャプチャできない
        #
        # aaa #hash #hash aaa
        # aaa #hash  #hash aaa
        #           ^
        #         ので, このように余分にスペース追加することで強引に対応...
        work = work.replace(' #', '  #')

        re.sub(RE_HASHTAG, repl, work)

        return pagenames

    @staticmethod
    def remove_ghost_page(pagenames, pagenames_in_project_by_dict):
        new_pagenames = []
        for pagename in pagenames:
            not_found = not pagename in pagenames_in_project_by_dict
            if not_found:
                continue
            new_pagenames.append(pagename)
        return new_pagenames

    @staticmethod
    def construct(page_instances, pagenames_in_project_by_dict):
        # linkto
        for page_inst in page_instances:
            page_inst.update_linkto(pagenames_in_project_by_dict)

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

    def update_linkto(self, pagenames_in_project_by_dict):
        content = self.rawstring
        linkee_pagenames = LinkConstructor.get_linkee_pagenames(content)
        linkee_pagenames = remove_duplicates_in_list(linkee_pagenames)
        linkee_pagenames = LinkConstructor.remove_ghost_page(linkee_pagenames, pagenames_in_project_by_dict)
        self._linkto_pagenames = linkee_pagenames

    @property
    def linkto_pagenames(self):
        return self._linkto_pagenames

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

def ________Scb2md_and_save________():
    pass

def convert_one_page(scblines):
    step1_converted_lines = lib_scblines2markdown.convert_step1(scblines)
    step2_converted_lines = lib_scblines2markdown.convert_step2(step1_converted_lines)
    markdown_lines = lib_scblines2markdown.convert_step3(step2_converted_lines)
    return markdown_lines

def save_one_file(markdown_lines, pagename, basedir, use_dryrun):
    filename_based_on_pagename = '{}.md'.format(pagename)
    filename = lib_scblines2markdown.fix_filename_to_ghpages_compatible(filename_based_on_pagename)
    filepath = os.path.join(basedir, filename)

    if use_dryrun:
        print('saving {} lines to "{}"...'.format(len(markdown_lines), filename))
        return
    list2file(filepath, markdown_lines)

def convert_and_save_all(project, page_instances, basedir, args):
    use_dryrun = args.dryrun

    for i,page_inst in enumerate(page_instances):
        pagename = page_inst.title
        scblines = page_inst.lines

        if use_dryrun:
            print('No.{:05d} page "{}", '.format(i+1, pagename), end='')
        markdown_lines = convert_one_page(scblines)

        markdown_lines.insert(0, '## {}'.format(pagename))
        save_one_file(markdown_lines, pagename, basedir, use_dryrun)

class SpecialPageInterface:
    def __init__(self):
        pass

    def sortkey_function(self, page_inst):
        raise NotImplementedError()

    def generate_outline(self, no, pagename, filename_of_this_page, page_inst):
        raise NotImplementedError()

    @property
    def basename(self):
        raise NotImplementedError()

    @property
    def short_description(self):
        raise NotImplementedError()

class Special_TitleByAsc(SpecialPageInterface):
    def __init__(self):
        super().__init__()

    def sortkey_function(self, page_inst):
        return page_inst.title

    def generate_outline(self, no, pagename, filename_of_this_page, page_inst):
        outline = '- {:05d} [{}]({})'.format(no, pagename, filename_of_this_page)
        return outline

    @property
    def basename(self):
        return 'index_title_by_asc'

    @property
    def short_description(self):
        return 'ページタイトル昇順'

class Special_LineCount(SpecialPageInterface):
    def __init__(self):
        super().__init__()

    def sortkey_function(self, page_inst):
        return len(page_inst.lines)

    def generate_outline(self, no, pagename, filename_of_this_page, page_inst):
        linecount = self.sortkey_function(page_inst)
        outline = '- {} 行: [{}]({})'.format(linecount, pagename, filename_of_this_page)
        return outline

    @property
    def basename(self):
        return 'index_linecount'

    @property
    def short_description(self):
        return 'ページ行数降順'

class Special_BodyLength(SpecialPageInterface):
    def __init__(self):
        super().__init__()

    def sortkey_function(self, page_inst):
        return len(page_inst.rawstring)

    def generate_outline(self, no, pagename, filename_of_this_page, page_inst):
        bodylength = self.sortkey_function(page_inst)
        outline = '- {} 文字: [{}]({})'.format(bodylength, pagename, filename_of_this_page)
        return outline

    @property
    def basename(self):
        return 'index_bodylength'

    @property
    def short_description(self):
        return 'ページ文字数降順'

def save_one_special_pages(page_insts, basedir, special_page_interface):
    basename = special_page_interface.basename
    filename = '{}.md'.format(basename)
    filepath = os.path.join(basedir, filename)

    outlines = []
    for i,page_inst in enumerate(page_insts):
        no = i+1
        pagename = page_inst.title
        filename_of_this_page = '{}.md'.format(pagename)
        filename_of_this_page = lib_scblines2markdown.fix_filename_to_ghpages_compatible(filename_of_this_page)

        outline = special_page_interface.generate_outline(no, pagename, filename_of_this_page, page_inst)
        outlines.append(outline)

    list2file(filepath, outlines)

def save_index_page(lines, basedir):
    filename = 'index.md'
    filepath = os.path.join(basedir, filename)
    list2file(filepath, lines)

def generate_index_contents(project, specialpages):
    outlines = []

    outlines.append('# {}'.format(project.display_name))

    outlines.append('- 案内ページ')
    outlines.append('    - [このサイトについて](このサイトについて.md)')
    outlines.append('    - [プロフィール](プロフィール.md)')

    outlines.append('- 一覧ページ')
    for specialpage in specialpages:
        filename = '{}.md'.format(specialpage.basename)
        text = specialpage.short_description
        line = '    - [{}]({})'.format(text, filename)
        outlines.append(line)

    outlines.append('')

    outlines.append('All {} pages.'.format(len(project.pages)))
    outlines.append('')
    outlines.append('Generated at {}, by {} from {}'.format(
        today_datetimestr(),
        '[scbjson2ghpages](https://github.com/stakiran/scbjson2ghpages)',
        '[scrapbox/sta](https://scrapbox.io/sta/)',
    ))

    return outlines

def generate_and_save_special_pages(project, basedir, args):
    use_dryrun = args.dryrun
    if use_dryrun:
        return

    page_insts = []
    for page in project.pages:
        page_inst = Page(page, project.name)
        page_insts.append(page_inst)

    specialpages = []

    specialpage = Special_TitleByAsc()
    new_insts = sorted(page_insts, key=specialpage.sortkey_function) 
    save_one_special_pages(new_insts, basedir, specialpage)
    specialpages.append(specialpage)

    specialpage = Special_LineCount()
    new_insts = sorted(page_insts, key=specialpage.sortkey_function, reverse=True)
    save_one_special_pages(new_insts, basedir, specialpage)
    specialpages.append(specialpage)

    specialpage = Special_BodyLength()
    new_insts = sorted(page_insts, key=specialpage.sortkey_function, reverse=True)
    save_one_special_pages(new_insts, basedir, specialpage)
    specialpages.append(specialpage)

    index_lines = generate_index_contents(project, specialpages)
    save_index_page(index_lines, basedir)

def ________Argument________():
    pass

def parse_arguments():
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument('-i', '--input', default=None, required=True,
        help='An input .json filename.')

    parser.add_argument('--page-to-scb', default=None, type=str,
        help='A page name to output the normalized contents .scb file.')
    parser.add_argument('--print-page', default=None, type=str,
        help='A page name to output the information of the instance.')
    parser.add_argument('--only-specials', default=False, action='store_true',
        help='If True, do generate special pages only. About pages, will be not generated.')

    parser.add_argument('--dryrun', default=False, action='store_true',
        help='If True, not save but display lines and filepath.')

    args = parser.parse_args()
    return args

def ________Main________():
    pass

if __name__ == '__main__':
    MYFULLPATH = os.path.abspath(sys.argv[0])
    MYDIR = os.path.dirname(MYFULLPATH)
    OUTDIR = 'docs'

    args = parse_arguments()

    filename = args.input

    s = file2str(filename)
    obj = str2obj(s)
    proj = Project(obj)

    if args.page_to_scb:
        seeker = PageSeeker(proj)
        page = seeker.get(args.page_to_scb)
        print(page.rawstring)
        sys.exit(0)

    BASEDIR = os.path.join(MYDIR, OUTDIR)
    if not(os.path.isdir(BASEDIR)):
        raise RuntimeError('docs/ dir not found...')

    page_instances = []
    for page in proj.pages:
        page_inst = Page(page, proj.name)
        page_instances.append(page_inst)
    # 指定ページの存在確認を O(1) で行う用の辞書
    pagenames_by_dict = {}
    for page_inst in page_instances:
        dummyvalue = 1
        pagename = page_inst.title
        pagenames_by_dict[pagename] = dummyvalue

    LinkConstructor.construct(page_instances, pagenames_by_dict)

    if args.print_page:
        seeker = PageSeeker(proj)
        page = seeker.get(args.print_page)
        print(page)
        sys.exit(0)

    generate_and_save_special_pages(proj, BASEDIR, args)
    if args.only_specials:
        sys.exit(0)
    convert_and_save_all(proj, page_instances, BASEDIR, args)
