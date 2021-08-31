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

def datetimeobj_to_datetimestr(dtojb):
    datestr = dtojb.strftime('%Y/%m/%d')
    timestr = dtojb.strftime('%H:%M:%S')

    wd =  dtojb.weekday()
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
    def construct(page_instances, pagenames_in_project_by_dict, pageseeker):
        # linkto
        for page_inst in page_instances:
            page_inst.update_linkto(pagenames_in_project_by_dict, pageseeker)

        # linkfrom
        #
        # A-->B
        # |
        # v
        # C
        for A in page_instances:
            for pageinst_linked_from_A in A.linkto_page_instances:
                A_pagename = A.title
                pageinst_linked_from_A.append_to_linkfrom(A)

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
    def __init__(self, page_instances):
        self._page_instances = page_instances
        self._parse()

    def _parse(self):
        self._page_instances_by_dict = {}
        for page_inst in self._page_instances:
            title = page_inst.title
            self._page_instances_by_dict[title] = page_inst

    def get(self, title):
        if not title in self._page_instances_by_dict:
            raise RuntimeError('Not found page "{}".'.format(title))
        return self._page_instances_by_dict[title]

    def get_pagenames(self):
        pagenames = []
        for pagename in self._page_instances_by_dict:
            pagenames.append(pagename)
        return pagenames

class Page:
    def __init__(self, page_obj, project_name):
        self._project_name = project_name
        self._obj = page_obj

        self._linkto_pageinsts = []
        self._linkfrom_pageinsts = []

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

    def update_linkto(self, pagenames_in_project_by_dict, pageseeker):
        content = self.rawstring
        linkee_pagenames = LinkConstructor.get_linkee_pagenames(content)
        linkee_pagenames = remove_duplicates_in_list(linkee_pagenames)
        linkee_pagenames = LinkConstructor.remove_ghost_page(linkee_pagenames, pagenames_in_project_by_dict)

        self._linkto_pages = []
        for pagename in linkee_pagenames:
            page_inst = pageseeker.get(pagename)
            self._linkto_pageinsts.append(page_inst)

    @property
    def linkto_page_instances(self):
        return self._linkto_pageinsts

    def append_to_linkfrom(self, pageinst):
        self._linkfrom_pageinsts.append(pageinst)

    @property
    def linkfrom_page_instances(self):
        return self._linkfrom_pageinsts

    def __str__(self):
        lines = self.lines
        lineHeads = '\n'.join(lines[:3])
        line_number = len(lines)
        return '''{title}
created at: {created}
updated at: {updated}
url       : {url}
linkto    : {linktoCount}
linkfrom  : {linkFromCount}
---
{lineHeads}...

total {lineNumber} lines. '''.format(
            title=self.title,
            created=self.created_by_datetime,
            updated=self.updated_by_datetime,
            url=self.url,
            linktoCount=len(self.linkto_page_instances),
            linkFromCount=len(self.linkfrom_page_instances),
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

def save_one_file(markdown_lines, pagename, basedir):
    filename_based_on_pagename = '{}.md'.format(pagename)
    filename = lib_scblines2markdown.fix_filename_to_ghpages_compatible(filename_based_on_pagename)
    filepath = os.path.join(basedir, filename)
    list2file(filepath, markdown_lines)

def generate_links(page_inst, args):
    ''' ページ page_inst の Links と 2hop-links をつくる.
    - リンク数多すぎると jekyll ビルドが間に合わないので, オプションにて間引けるようにしている.
    - 生成されたリンク数を知るために, allcount_of_links で記録している. '''

    A = page_inst
    ADD_BLANKLINE = ''
    allcount_of_links = 0

    outlines = []
    outlines.append('## Links')

    # A の linkfrom
    # B -> A

    count_of_B = 0

    for B in A.linkfrom_page_instances:
        use_flimit = not args.no_flimit
        if use_flimit and count_of_B >= args.flimit:
            break

        B_pagename = B.title
        basename = '{}.md'.format(B_pagename)
        filename = lib_scblines2markdown.fix_filename_to_ghpages_compatible(basename)
        outlines.append('- ← [{}]({})'.format(B_pagename, filename))
        count_of_B += 1
        allcount_of_links += 1

    # A の linkto、は 2hop-link でわかるので出さない.
    # A -> B

    is_no_links = len(outlines)==1
    if is_no_links:
        outlines = []
    else:
        outlines.append(ADD_BLANKLINE)

    # A の 2hop-link
    #
    # A -> B <- C
    #
    # このような C を, B ごとに列挙する.
    # ただし分量が多くなりがちなので適当に制御する.
    # (Scrapbox 本家のアルゴリズムはよくわからなかった)

    is_no_linkto = len(A.linkto_page_instances)==0
    if is_no_linkto:
        return [outlines, allcount_of_links]

    outlines.append('## 2hop Links')

    count_of_B = 0
    count_of_C = 0

    for B in A.linkto_page_instances:
        # でかすぎる linkto はノイジーなので無視
        # (これはたぶん Scrapbox 本家でも搭載されている)
        is_B_links_too_large = len(B.linkfrom_page_instances)>=100
        if is_B_links_too_large:
            continue

        use_tlimit = not args.no_tlimit
        if use_tlimit and count_of_B >= args.tlimit:
            break

        B_pagename = B.title
        basename = '{}.md'.format(B_pagename)
        filename = lib_scblines2markdown.fix_filename_to_ghpages_compatible(basename)
        # jekyll が見出し部分で markdown error になるっぽいので, 見出しはやめる
        #outlines.append('## → [{}]({})'.format(B_pagename, filename))
        #outlines.append(ADD_BLANKLINE)
        outlines.append('- → [{}]({})'.format(B_pagename, filename))

        count_of_C_of_B = 0
        for C in B.linkfrom_page_instances:
            use_hlimit = not args.no_hlimit
            if use_hlimit and count_of_C_of_B >= args.hlimit:
                break

            C_pagename = C.title

            is_self_2hop = C_pagename==A.title
            if is_self_2hop:
                continue

            basename = '{}.md'.format(C_pagename)
            filename = lib_scblines2markdown.fix_filename_to_ghpages_compatible(basename)
            outlines.append('    - ← [{}]({})'.format(C_pagename, filename))
            count_of_C += 1
            count_of_C_of_B += 1
            allcount_of_links += 1

        is_not_2hoplink = count_of_C_of_B==0
        if is_not_2hoplink:
            # C が 0 個の B を表示しても仕方ないので消す
            outlines = outlines[:-1]

        count_of_B += 1
        allcount_of_links += 1

    return [outlines, allcount_of_links]

def convert_and_save_all(project, page_instances, basedir, args):
    use_dryrun = args.dryrun

    linkcount_of_allpages = 0
    for i,page_inst in enumerate(page_instances):
        pagename = page_inst.title
        scblines = page_inst.lines

        markdown_lines = convert_one_page(scblines)

        links_lines = []
        links_lines, linkcount = generate_links(page_inst, args)

        markdown_lines.extend(links_lines)
        markdown_lines.insert(0, '## {}'.format(pagename))

        linkcount_of_allpages += linkcount

        if use_dryrun:
            if args.no_dryrun_pagename:
                pass
            else:
                print('No.{:05d} page "{}"'.format(i+1, pagename))
            continue
        save_one_file(markdown_lines, pagename, basedir)

    if args.print_linkcount:
        print('Link count is about {}.'.format(linkcount_of_allpages))

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

class Special_MostLinked(SpecialPageInterface):
    def __init__(self):
        super().__init__()

    def sortkey_function(self, page_inst):
        return len(page_inst.linkfrom_page_instances)

    def generate_outline(self, no, pagename, filename_of_this_page, page_inst):
        linkfrom_count = self.sortkey_function(page_inst)
        outline = '- {} links: [{}]({})'.format(linkfrom_count, pagename, filename_of_this_page)
        return outline

    @property
    def basename(self):
        return 'index_mostlinked'

    @property
    def short_description(self):
        return '被リンク数順'

class Special_MostLinking(SpecialPageInterface):
    def __init__(self):
        super().__init__()

    def sortkey_function(self, page_inst):
        return len(page_inst.linkto_page_instances)

    def generate_outline(self, no, pagename, filename_of_this_page, page_inst):
        linkfrom_count = self.sortkey_function(page_inst)
        outline = '- {} links: [{}]({})'.format(linkfrom_count, pagename, filename_of_this_page)
        return outline

    @property
    def basename(self):
        return 'index_mostlinking'

    @property
    def short_description(self):
        return 'リンク数順'

class Special_DateCreated(SpecialPageInterface):
    def __init__(self):
        super().__init__()

    def sortkey_function(self, page_inst):
        return page_inst.created_by_unixtime

    def generate_outline(self, no, pagename, filename_of_this_page, page_inst):
        dtobj = page_inst.created_by_datetime
        dtstr = datetimeobj_to_datetimestr(dtobj)
        outline = '- {} [{}]({})'.format(dtstr, pagename, filename_of_this_page)
        return outline

    @property
    def basename(self):
        return 'index_date_created'

    @property
    def short_description(self):
        return '作成日時順'

def save_one_special_pages(page_insts, basedir, special_page_interface, args):
    basename = special_page_interface.basename
    filename = '{}.md'.format(basename)
    filepath = os.path.join(basedir, filename)

    use_link_to_scrapbox = args.link_to_scrapbox

    outlines = []
    for i,page_inst in enumerate(page_insts):
        no = i+1
        pagename = page_inst.title
        filename_of_this_page = '{}.md'.format(pagename)
        filename_of_this_page = lib_scblines2markdown.fix_filename_to_ghpages_compatible(filename_of_this_page)

        if use_link_to_scrapbox:
            pageurl = page_inst.url
            filename_of_this_page = pageurl

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

def generate_and_save_special_pages(project, page_instances, basedir, args):
    use_dryrun = args.dryrun
    if use_dryrun:
        return

    page_insts = page_instances
    specialpages = []

    specialpage = Special_TitleByAsc()
    new_insts = sorted(page_insts, key=specialpage.sortkey_function) 
    save_one_special_pages(new_insts, basedir, specialpage, args)
    specialpages.append(specialpage)

    specialpage = Special_LineCount()
    new_insts = sorted(page_insts, key=specialpage.sortkey_function, reverse=True)
    save_one_special_pages(new_insts, basedir, specialpage, args)
    specialpages.append(specialpage)

    specialpage = Special_BodyLength()
    new_insts = sorted(page_insts, key=specialpage.sortkey_function, reverse=True)
    save_one_special_pages(new_insts, basedir, specialpage, args)
    specialpages.append(specialpage)

    specialpage = Special_MostLinked()
    new_insts = sorted(page_insts, key=specialpage.sortkey_function, reverse=True)
    save_one_special_pages(new_insts, basedir, specialpage, args)
    specialpages.append(specialpage)

    specialpage = Special_MostLinking()
    new_insts = sorted(page_insts, key=specialpage.sortkey_function, reverse=True)
    save_one_special_pages(new_insts, basedir, specialpage, args)
    specialpages.append(specialpage)

    specialpage = Special_DateCreated()
    new_insts = sorted(page_insts, key=specialpage.sortkey_function, reverse=True)
    save_one_special_pages(new_insts, basedir, specialpage, args)
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

    parser.add_argument('--link-to-scrapbox', default=False, action='store_true',
        help='If True, Use the link to scrapbox project page about special pages.')

    parser.add_argument('--flimit', default=16, type=int,
        help='A limit count of linkfrom of a specific page.')
    parser.add_argument('--tlimit', default=8, type=int,
        help='A limit count of linkto of a specific page.')
    parser.add_argument('--hlimit', default=4, type=int,
        help='A limit count of 2hop-link of a specific page.')
    parser.add_argument('--print-linkcount', default=False, action='store_true',
        help='If True, display the total links count of all pages.')
    parser.add_argument('--no-flimit', default=False, action='store_true',
        help='If True, No use --flimit option.')
    parser.add_argument('--no-tlimit', default=False, action='store_true',
        help='If True, No use --tlimit option.')
    parser.add_argument('--no-hlimit', default=False, action='store_true',
        help='If True, No use --hlimit option.')

    parser.add_argument('--dryrun', default=False, action='store_true',
        help='If True, not save but display lines and filepath.')
    parser.add_argument('--no-dryrun-pagename', default=False, action='store_true',
        help='If True, no display about pagename')

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

    # parse json
    # ----------

    s = file2str(filename)
    obj = str2obj(s)
    proj = Project(obj)

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

    # proceed
    # -------

    if args.page_to_scb:
        seeker = PageSeeker(page_instances)
        page = seeker.get(args.page_to_scb)
        print(page.rawstring)
        sys.exit(0)

    BASEDIR = os.path.join(MYDIR, OUTDIR)
    if not(os.path.isdir(BASEDIR)):
        raise RuntimeError('docs/ dir not found...')

    seeker = PageSeeker(page_instances)
    LinkConstructor.construct(page_instances, pagenames_by_dict, seeker)

    if args.print_page:
        page = seeker.get(args.print_page)
        print(page)
        sys.exit(0)

    # I/O
    # ---

    generate_and_save_special_pages(proj, page_instances, BASEDIR, args)
    if args.only_specials:
        sys.exit(0)
    convert_and_save_all(proj, page_instances, BASEDIR, args)
