# encoding: utf-8

import re

class MODE:
    INVALID = -1
    NOMODE = 0
    BLANKLINE = 1
    PARAGRAPH = 2
    LIST = 3
    LIST_IN_BLOCK = 4
    START_OF_BLOCK_CODE = 10
    START_OF_BLOCK_TABLE = 11

class InBlockStateUser:
    def __init__(self):
        self._inblockstate = InBlockState()

        # block から抜けた行の検出に必要.
        # 抜けた時の行番号を InBlockState は保持しないので,
        # 利用者(User)の側で保持する必要がある.
        self._is_left_just_now = False

    def _clear_just_now_leaving_flag(self):
        self._is_left_just_now = False

    def update(self, line, cur_indentdepth):
        self._clear_just_now_leaving_flag()

        state = self.state

        if state.is_in_block():
            self._update_case_of_in_block(line, cur_indentdepth)
            return
        self._update_case_of_not_in_block(line, cur_indentdepth)

    def _update_case_of_not_in_block(self, line, cur_indentdepth):
        state = self.state

        if Moder.is_start_of_code(line):
            state.enter(MODE.START_OF_BLOCK_CODE, cur_indentdepth)
            return

        if Moder.is_start_of_table(line):
            state.enter(MODE.START_OF_BLOCK_TABLE, cur_indentdepth)
            return

    def _update_case_of_in_block(self, line, cur_indentdepth):
        state = self.state

        is_current_more_deep = cur_indentdepth > state.indentdepth_of_start
        if is_current_more_deep:
            return
        state.leave()
        self._is_left_just_now = True

    @property
    def state(self):
        return self._inblockstate

    def is_left_just_now(self):
        return self._is_left_just_now

class InBlockState:
    def __init__(self):
        self._clear()

    def _clear(self):
        NO_DUPLICATED_VALUE_OF_INDENT_DEPTH = -1

        self._mode = MODE.NOMODE
        self._depth = NO_DUPLICATED_VALUE_OF_INDENT_DEPTH

    def enter(self, mode, indentdepth):
        ''' @param mode MODE.xxx の値(START_OF_XXXX)
        @param indentdepth '''
        already_in_block = self.is_in_block()
        if already_in_block:
            raise RuntimeError('Already in block')

        self._mode = mode
        self._depth = indentdepth

    def leave(self):
        self._clear()

    def is_in_block(self):
        is_not_in_block = self._mode == MODE.NOMODE
        if is_not_in_block:
            return False
        return True

    def is_in_code_block(self):
        is_not_in_block = not self.is_in_block()
        if is_not_in_block:
            raise RuntimeError('is_in_code_block')

        is_matched = self._mode == MODE.START_OF_BLOCK_CODE
        if is_matched:
            return True
        return False

    def is_in_table_block(self):
        is_not_in_block = not self.is_in_block()
        if is_not_in_block:
            raise RuntimeError('is_in_table_block')

        is_matched = self._mode == MODE.START_OF_BLOCK_TABLE
        if is_matched:
            return True
        return False

    @property
    def indentdepth_of_start(self):
        return self._depth

class Moder:
    @classmethod
    def judge_extra_insertion(cls, prev_indentdepth, cur_indentdepth, inblockstate_user):
        ''' string への挿入を前提としているため, 行指向の場合は適宜解釈し直すこと.
        @return 余分に挿入すべき文字列.
        @retval '' 何も挿入する必要がない.
        
        アルゴリズムがえぐいので Scrapbox のメモも参照のこと. '''

        # @todo ★1と★2内の返り値も定数に
        # ★1のケース
        def end_of_list_or_block(inblockstate_user):
            state = inblockstate_user.state
            if state.is_in_block():
                return '```'
            return '\n'

        # ★2のケース
        def continuous_indent(cur_indentdepth, inblockstate_user):
            state = inblockstate_user.state

            is_not_in_block = not state.is_in_block()
            is_left_from_block_just_now = inblockstate_user.is_left_just_now()

            if is_not_in_block and is_left_from_block_just_now:
                # @todo ネストしたブロックなので, ネスト削除とダミーリスト挿入が必要.
                #       ブロック開始時含めて追加処理が必要.
                return '\n'

            return ''

        # returning values
        IGNORE = ''
        ADD_LINEFEED = '\n'

        # aliases
        p = prev_indentdepth
        c = cur_indentdepth

        # 段落が続いている
        if c==0 and p==0:
            return ADD_LINEFEED

        # list or block が終わった
        if c==0 and p>=1:
            extra_insertion = end_of_list_or_block(inblockstate_user)
            return extra_insertion

        # list or block が始まった
        if c==1 and p==0:
            return ADD_LINEFEED
        # list or block が続いている(インデントは変わらず)
        if c==1 and p==1:
            return IGNORE
        # list or block が続いている(インデントは深くなった)
        if c==1 and p>1:
            return IGNORE

        # list or blockが終わった
        if p==0:
            extra_insertion = end_of_list_or_block(inblockstate_user)
            return extra_insertion

        # list or block が続いている(インデントは変わらず or 深くなった)
        # 先頭行のときもここに入る.
        is_more_deepen = c>=p
        if is_more_deepen:
            return IGNORE

        # list or block が続いている(インデントは変わらず or 深くなった or 浅くなった)
        # インデント 1 以上の深さで block が終わっているケース, もここに入る.
        extra_insertion = continuous_indent(c, inblockstate_user)
        return extra_insertion

    @classmethod
    def determin_mode(cls, line):
        mode = MODE.INVALID

        if cls.is_start_of_code(line):
            mode = MODE.START_OF_BLOCK_CODE
            return mode
        if cls.is_start_of_table(line):
            mode = MODE.START_OF_BLOCK_TABLE
            return mode

        if cls.is_list(line):
            mode = MODE.LIST
            return mode

        if cls.is_paragraph(line):
            mode = MODE.PARAGRAPH
            return mode

        if cls.is_blankline(line):
            mode = MODE.BLANKLINE
            return mode

        raise RuntimeError('不正なモード. ここに来ることはないはず.\n"{}"'.format(line))

    @classmethod
    def is_blankline(cls, line):
        if len(line) == 0:
            return True
        return False

    @classmethod
    def is_list(cls, line):
        if cls.is_blankline(line):
            return False

        is_firstchar_space = line[:1] == ' '
        is_firstchar_tab = line[:1] == '\t'
        if is_firstchar_space:
            return True
        if is_firstchar_tab:
            return True

        return False

    @classmethod
    def is_paragraph(cls, line):
        if cls.is_blankline(line):
            return False

        if cls.is_start_of_code(line):
            return False
        if cls.is_start_of_table(line):
            return False

        if cls.is_list(line):
            return False

        # 少なくとも空行ではないし,
        # 特殊記法で始まりもしないし,
        # リストでもない.
        #  -> 段落
        #
        # 消去法で決定する.

        return True

    @classmethod
    def is_start_of_code(cls, line):
        if cls.is_blankline(line):
            return False

        stripped_line = line.strip()

        CODE_GRAMMER = 'code:'
        MINIMUM_LENGTH_OF_CODE_GRAMMER = len(CODE_GRAMMER)
        is_too_short = len(stripped_line) <= MINIMUM_LENGTH_OF_CODE_GRAMMER
        if is_too_short:
            return False

        is_matched_prefix = stripped_line.startswith(CODE_GRAMMER)
        if is_matched_prefix:
            return True

        return False

    @classmethod
    def is_start_of_table(cls, line):
        # 不吉な臭い: DRYできるのでは?
        if cls.is_blankline(line):
            return False

        stripped_line = line.strip()

        CODE_TABLE = 'table:'
        MINIMUM_LENGTH_OF_CODE_TABLE = len(CODE_TABLE)
        is_too_short = len(stripped_line) <= MINIMUM_LENGTH_OF_CODE_TABLE
        if is_too_short:
            return False

        is_matched_prefix = stripped_line.startswith(CODE_TABLE)
        if is_matched_prefix:
            return True

        return False

def count_indentdepth(line):
    i = 0
    while line[i:i+1]==' ':
        i += 1
    return i

def convert_step1(scblines):
    lines = scblines
    outlines = []

    # step1: 空行
    # 空行は <br> と \n で置換するのがベストだと事前調査済.

    for line in lines:
        is_not_blankline = not Moder.is_blankline(line)
        if is_not_blankline:
            outlines.append(line)
            continue
        outlines.append('<br>')
        outlines.append('')

    return outlines

def _step2_append_extra_insertion(outlines, prev_indentdepth, cur_indentdepth, inblock_state):
    extra_insertion = Moder.judge_extra_insertion(prev_indentdepth, cur_indentdepth, inblock_state)

    is_no_insertion = extra_insertion == ''
    if is_no_insertion:
        return

    is_newline_insertion = extra_insertion == '\n'
    if is_newline_insertion:
        outlines.append('')
        return

    outlines.append(extra_insertion)

def convert_step2(step1_converted_lines):
    # step2: インデントの深さに伴う終端処理
    # 終端として必要な文字列(extra insertion)を挿入する.
    # -> \n, コードブロック終点(```) etc

    lines = step1_converted_lines
    outlines = []

    inblockstate_user = InBlockStateUser()
    cur_indentdepth = -1
    prev_indentdepth = -1

    is_prev_blankline = False
    is_cur_blankline = False

    # 空行は step1 で処理しているので extra insertion は不要.
    # - 「prevが空行だった」「curが空行」の 2 パターンあるので両方除外する
    # - 除外ルーチンは extra insertion には含まれてないので, メタで(呼び出し元で)やる

    for i,line in enumerate(lines):
        prev_indentdepth = cur_indentdepth
        cur_indentdepth = count_indentdepth(line)
        inblockstate_user.update(line, cur_indentdepth)

        is_prev_blankline = is_cur_blankline
        is_cur_blankline = Moder.is_blankline(line)
        if is_cur_blankline or is_prev_blankline:
            pass
        else:
            _step2_append_extra_insertion(outlines, prev_indentdepth, cur_indentdepth, inblockstate_user)

        outlines.append(line)

    return outlines

RE_LINK_ANOTHER_PROJECT = re.compile(r'\[/(.+?)\]')
RE_LINK_URL_TEXT = re.compile(r'\[http(s){0,1}\:\/\/(.+?)( )(.+?)\]')
RE_LINK_TEXT_URL = re.compile(r'\[(.+?)( )http(s){0,1}\:\/\/(.+?)\]')
RE_BOLD = re.compile(r'\[\*+( )(.+?)\]')
RE_STRIKE = re.compile(r'\[\-( )(.+?)\]')
def scb_to_markdown_in_line(line, cur_indentdepth, inblockstate_user):
    newline = line

    state = inblockstate_user.state
    is_in_list = cur_indentdepth>0
    is_in_block = state.is_in_block()

    if is_in_block and state.is_in_code_block():
        return line

    if is_in_block and state.is_in_table_block():
        # テーブル中でも他の文法を使う表現は(Markdownには)あるが, Scrapboxにはないので
        # ないとみなして fall through しない.
        return '| テーブルは | あとで | {} | 実装します |'.format(line)

    if is_in_list:
        lstripped_newline = newline.lstrip()
        markdown_indent = '    '*(cur_indentdepth-1)
        newline = '{}- {}'.format(markdown_indent, lstripped_newline)

    # @todo 置換順はちゃんと根拠とともに整理する
    # とりあえずリンクを先にしないと link in bold や link in strike が上手くいかないってのはわかってる

    newline = re.sub(RE_LINK_ANOTHER_PROJECT, '[/\\1](https://scrapbox.io/\\1)', newline)

    newline = re.sub(RE_LINK_URL_TEXT, '[\\4](http\\1://\\2)', newline)
    newline = re.sub(RE_LINK_TEXT_URL, '[\\1](http\\3://\\4)', newline)

    newline = re.sub(RE_BOLD, '**\\2**', newline)
    newline = re.sub(RE_STRIKE, '~~\\2~~', newline)

    return newline

def convert_step3(step2_converted_lines):
    # step3: インラインの Scrapbox 記法を Markdown のものに変換

    lines = step2_converted_lines
    outlines = []

    inblockstate_user = InBlockStateUser()
    cur_indentdepth = -1

    for scbline in lines:
        cur_indentdepth = count_indentdepth(scbline)
        inblockstate_user.update(scbline, cur_indentdepth)

        markdown_line = scb_to_markdown_in_line(scbline, cur_indentdepth, inblockstate_user)
        outlines.append(markdown_line)

    return outlines

if __name__ == '__main__':
    pass
