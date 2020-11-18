# import sys
# right = '\u001b[1000D'
# left = '\u001b[1000C'
# clear_line = '\u001b[2K'
# up = '\u001b[1A'
# clear_to_bottom = '\u001b[J'
#
#
# def print_multi_line(cmd_selector):
#     sys.stdout.write('Please Select the time')
#
#     for index, item in enumerate(cmd_selector.selectors):
#         first_word = '  '
#         if index in cmd_selector.select_index:
#             first_word = '> '
#         sys.stdout.write(first_word + item)
#
#     back_to_top = '\u001b[1A' * (len(cmd_selector.selectors) + 1)
#     sys.stdout.write(back_to_top)
#
#
# def clear_multi_line(cmd_selector):
#     sys.stdout.write(clear_to_bottom)
