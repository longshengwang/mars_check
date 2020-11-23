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


class CommandSelector:
    selectors = None
    cur_index = 0
    select_index_list = []
    select_count = None
    cursor_index = 0
    header_word = None

    def __init__(self, selectors, header_word, select_count=None):
        self.selectors = selectors
        self.select_count = select_count
        self.header_word = header_word

    def up(self):
        if self.cur_index > 0:
            self.cur_index = self.cur_index - 1
            self.print_multi_line()

    def down(self):
        if self.cur_index < len(self.selectors) - 1:
            self.cur_index = self.cur_index + 1
            self.print_multi_line()

    # Return Code
    #   1: select
    #   0: unselect
    #  -1: more than max select
    def space(self):
        try:
            index = self.select_index_list.index(self.cur_index)
            self.select_index_list.remove(self.cur_index)
        except ValueError, e:
            if self.select_count is None:
                self.select_index_list.append(self.cur_index)
            else:
                if len(self.select_index_list) < self.select_count:
                    self.select_index_list.append(self.cur_index)
        self.print_multi_line()

    def exit(self):
        self.clear_multi_line()

    def get_selector(self):
        sys.stdout.write(UseStyle(self.header_word, fore='yellow') + '\n')
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
                elif as_code == 32:
                    is_multi_second = False
                    is_multi_first = False
                    self.space()
                # elif as_code == 100:
                #     is_multi_second = False
                #     is_multi_first = False
                #     cmd_selector.down()
                # elif as_code == 117:
                #     is_multi_second = False
                #     is_multi_first = False
                #     cmd_selector.up()
                elif as_code == 13:
                    is_multi_second = False
                    is_multi_first = False
                    self.exit()
                    break
                elif as_code == 3:
                    is_multi_second = False
                    is_multi_first = False
                    self.exit()
                    break
                else:
                    is_multi_second = False
                    is_multi_first = False
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        if self.select_count is None:
            res = []
            for i in self.select_index_list:
                res.append(self.selectors[i])
            return res
        else:
            if len(self.select_index_list) == self.select_count:
                res = []
                for i in self.select_index_list:
                    res.append(self.selectors[i])
                return res
            else:
                show_message = 'The selector count is not correct.(Expect is ' + \
                               str(self.select_count) + ', but only select ' + str(len(self.select_index_list)) + ')'
                print UseStyle(show_message, fore='red')
                return None

    def print_multi_line(self):
        sys.stdout.write(self.cursor_index * up + left)
        sys.stdout.write(clear_to_bottom)

        for index, item in enumerate(self.selectors):
            if index in self.select_index_list:
                first_word = '+ '
                sys.stdout.write(left + clear_line + UseStyle(first_word + item, fore='green') + '\n')
            else:
                first_word = '  '
                sys.stdout.write(left + clear_line + first_word + item + '\n')

        back_to_cur_index = up * (len(self.selectors) - self.cur_index)
        self.cursor_index = self.cur_index
        sys.stdout.write(back_to_cur_index)
        sys.stdout.write(left)

    def clear_multi_line(self):
        back_to_top = up * (self.cur_index + 1)
        sys.stdout.write(back_to_top)
        sys.stdout.write(left)
        sys.stdout.write(clear_to_bottom)
