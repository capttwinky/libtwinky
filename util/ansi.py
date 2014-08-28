from __future__ import print_function
from contextlib import contextmanager

CSI = '\033['

def code_to_chars(code):
    return '{}{}m'.format(CSI, code)

def gen_ansi_dict(codes):
    return {k:code_to_chars(v) for k, v in codes.items()}

AnsiFore = dict(
    BLACK=30,
    RED=31,
    GREEN=32,
    YELLOW=33,
    BLUE=34,
    MAGENTA=35,
    CYAN=36,
    WHITE=37,
    RESET=39,
)
AnsiBack = dict(
    BLACK=40,
    RED=41,
    GREEN=42,
    YELLOW=43,
    BLUE=44,
    MAGENTA=45,
    CYAN=46,
    WHITE=47,
    RESET=49,
)
AnsiStyle = dict(
    BRIGHT=1,
    DIM=2,
    NORMAL=22,
    RESET_ALL=0,
)

Fore = gen_ansi_dict(AnsiFore)
Back = gen_ansi_dict(AnsiBack)
Style = gen_ansi_dict(AnsiStyle)

@contextmanager
def print_style(fg='', bg='', style=''):
    ansi_str = ''.join((Fore.get(fg.upper(), ''), Back.get(bg.upper(), ''), Style.get(style.upper(), ''),))
    print(ansi_str, end='')
    yield True
    print(''.join((Fore['RESET'], Back['RESET'], Style['RESET_ALL'],)), end='')
    

def ansi_print(to_print, fg='', bg='', style=''):
    with print_style(fg=fg, bg=bg, style=style):
        print(to_print)
    return True
