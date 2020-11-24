# -*- coding:utf-8 -*-

from color import UseStyle


def print_warn(word):
    print UseStyle(word, fore='red')


def print_normal(word):
    # print '[ ' + UseStyle('MARS', fore='green') + ' ] ' + word
    print ' ' + word


def print_normal_start(word, color=None):
    # print '[ ' + UseStyle('MARS', fore='green') + ' ] ---- ' + (word if color is None else UseStyle(word, fore=color))
    print ' ---- ' + (word if color is None else UseStyle(word, fore=color))


def print_normal_sub(word, color=None):
    # print '[ ' + UseStyle('MARS', fore='green') + ' ] |' + (word if color is None else UseStyle(word, fore=color))
    print ' |' + (word if color is None else UseStyle(word, fore=color))


def print_normal_center(word, color=None):
    # print '[ ' + UseStyle('MARS', fore='green') + ' ] |  ' + (word if color is None else UseStyle(word, fore=color))
    print ' |  ' + (word if color is None else UseStyle(word, fore=color))


def print_normal_end(word, color=None):
    # print '[ ' + UseStyle('MARS', fore='green') + ' ] ---- ' + word if color is None else UseStyle(word, fore=color)
    print ' ---- ' + (word if color is None else UseStyle(word, fore=color))
