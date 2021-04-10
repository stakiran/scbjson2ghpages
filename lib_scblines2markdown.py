# encoding: utf-8

class Moder:
    BLANKLINE = 1
    PARAGRAPH = 2
    LIST = 3
    LIST_IN_BLOCK = 4
    START_OF_BLOCK_CODE = 10
    START_OF_BLOCK_TABLE = 11

    def __init__(self):
        pass

    def set_as_prev(self, line):
        pass

    def set_as_current(self, line):
        pass

    @property
    def prevmode(self):
        return self._mode_prev

    @property
    def currentmode(self):
        return self._mode_current

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

class Converter:
    def __init__(self):
        pass

    def _clear(self):
        self._out_lines = []

    def parse(self, lines):
        self._clear()

        self._lines = lines
        for line in self._lines:
            self._parse_line(line)

    def _parse_line(self, line):
        pass

def convert(lines):
    pass

if __name__ == '__main__':
    moder = Moder()
    print(Moder.is_blankline(''))
    print(Moder.is_blankline(' list'))
    print(Moder.is_list(' list'))
    print(Moder.is_list('  '))
    print(Moder.is_list(''))

    print(Moder.is_start_of_code('code:js'))
