# encoding: utf-8

class MODE:
    INVALID = -1
    NOMODE = 0
    BLANKLINE = 1
    PARAGRAPH = 2
    LIST = 3
    LIST_IN_BLOCK = 4
    START_OF_BLOCK_CODE = 10
    START_OF_BLOCK_TABLE = 11

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
    def judge_extra_insertion(cls, prev_indentdepth, cur_indentdepth, inblock_state):
        ''' @return 余分に挿入すべき文字列.
        @retval '' 何も挿入する必要がない. '''

        # returning values
        # @todo たぶん ignore は [] で、addlinefeed は [''] じゃないと行指向的にやりづらい気がする
        IGNORE = ''
        ADD_LINEFEED = '\n'

        # aliases
        p = prev_indentdepth
        c = cur_indentdepth
        state = inblock_state

        # 空行が続いている
        if c==0 and p==0:
            return IGNORE

        # list or block が終わった
        if c==0 and p>=1:
            # ★1
            return ''

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
            # ★1
            return ''

        # list or block が続いている(インデントは変わらず or 深くなった)
        is_more_deepen = c>=p
        if is_more_deepen:
            return IGNORE

        # ★2
        return ''

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

def convert(scblines):
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

    # step2: インデントの深さに伴う終端処理
    # 終端として必要な文字列(extra insertion)を挿入する.
    # -> \n, コードブロック終点(```) etc

    lines = outlines
    outlines = []

    mode_of_prevline = MODE.NOMODE
    inblock_state = InBlockState()

    for i,line in enumerate(lines):
        outlines.append(line)

        mode_of_curline = Moder.determin_mode(line)
        extra_insertion = Moder.judge_extra_insertion(mode_of_prevline, mode_of_curline, inblock_state)
        is_no_insertion = extra_insertion == ''
        if is_no_insertion:
            continue
        outlines.append(extra_insertion)

    return outlines

if __name__ == '__main__':
    pass
