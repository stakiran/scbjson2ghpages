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

class Moder:
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
    # \n あるいはコードブロック終点(```)の挿入が必要なので, 該当箇所に挿入する.
    lines = outlines
    mode_of_prevline = MODE.NOMODE
    for i,line in enumerate(lines):
        pass

    return outlines

if __name__ == '__main__':
    pass
