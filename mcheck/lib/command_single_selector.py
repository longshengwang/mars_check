# -*- coding: utf-8 -*-
import sys
import termios
import tty

from color import UseStyle

left = u'\u001b[1000D'
right = u'\u001b[1000C'
clear_line = u'\u001b[2K'
up = u'\u001b[1A'
down = u'\u001b[1B'
clear_to_bottom = u'\u001b[J'


class CommandSingleSelector:
    selectors = None
    cur_index = 0
    cursor_index = -1
    header_word = None
    is_cancel = False
    top_index = 0
    bottom_index = 0

    def __init__(self, selectors, header_word):
        self.selectors = selectors
        if len(selectors) > 20:
            self.bottom_index = 20
        else:
            self.bottom_index = len(selectors) - 1

        self.header_word = header_word

    def up(self):
        if self.cur_index > 0:
            self.cur_index = self.cur_index - 1
            if self.cur_index < self.top_index:
                self.top_index = self.top_index - 1
                self.bottom_index = self.bottom_index - 1
            self.print_multi_line()

    def down(self):
        if self.cur_index < len(self.selectors) - 1:
            self.cur_index = self.cur_index + 1
            if self.cur_index > self.bottom_index:
                self.top_index = self.top_index + 1
                self.bottom_index = self.bottom_index + 1
            self.print_multi_line()

    def exit(self):
        self.clear_multi_line()

    def get_selector(self):
        sys.stdout.write(UseStyle(self.header_word, fore='yellow', mode='underline') + '\n')
        self.print_multi_line()
        is_multi_first = False
        is_multi_second = False

        while True:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
                as_code = ord(ch)

                # find the multi key for up/down
                if as_code == 27:
                    is_multi_first = True
                elif as_code == 91:
                    if is_multi_first:
                        is_multi_second = True
                elif as_code == 65:
                    if is_multi_first and is_multi_second:
                        self.up()
                    is_multi_second = False
                    is_multi_first = False
                elif as_code == 66:
                    if is_multi_first and is_multi_second:
                        self.down()
                    is_multi_second = False
                    is_multi_first = False
                elif as_code == 13:
                    is_multi_second = False
                    is_multi_first = False
                    self.exit()
                    break
                elif as_code == 3:
                    is_multi_second = False
                    is_multi_first = False
                    self.exit()
                    self.is_cancel = True
                    break
                else:
                    is_multi_second = False
                    is_multi_first = False
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        if self.is_cancel:
            raise Exception('Cancel this operation.')

        return self.selectors[self.cur_index]

    def print_multi_line(self):
        sys.stdout.write((self.cursor_index + 1) * up + left)
        sys.stdout.write(clear_to_bottom)

        up_size = self.bottom_index - self.cur_index + 1 + 1 + 1 # first and last word

        has_first_sign = '          '
        if self.top_index > 0:
            has_first_sign = '   ==== ^ ===='

        sys.stdout.write(left + clear_line + has_first_sign + '\n')


        for index, item in enumerate(self.selectors):
            if self.top_index <= index <= self.bottom_index:
                first_word = '   '
                if index == self.cur_index:
                    first_word = ' > '
                    sys.stdout.write(left + clear_line + UseStyle(first_word + item, fore='green') + '\n')
                else:
                    sys.stdout.write(left + clear_line + first_word + item + '\n')
        has_last_sign = '          '
        if len(self.selectors) - 1 > self.bottom_index:
            has_last_sign = '   ==== v ===='
        sys.stdout.write(left + clear_line + has_last_sign + '\n')

        back_to_cur_index = up * (up_size -1)
        self.cursor_index = self.cur_index - self.top_index
        sys.stdout.write(back_to_cur_index)
        sys.stdout.write(left)

    def clear_multi_line(self):
        back_to_top = up * (self.cur_index - self.top_index + 2)
        sys.stdout.write(back_to_top)
        sys.stdout.write(left)
        sys.stdout.write(clear_to_bottom)
