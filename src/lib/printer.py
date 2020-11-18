from color import UseStyle


def print_warn(word):
    print UseStyle(word, fore='red')


def print_normal(word):
    print '[ ' + UseStyle('MARS', fore='green')+' ] ' + word

