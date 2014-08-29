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
    ITALICS=3,
    UNDERLINE=4,
    STRIKETHROUGH=9,
    NORMAL=22,
    RESET_ALL=0,
)

Fore = gen_ansi_dict(AnsiFore)
Back = gen_ansi_dict(AnsiBack)
Style = gen_ansi_dict(AnsiStyle)

@contextmanager
def print_style(fg='', bg='', style=''):
    f_str = format_string(fg, bg, style)
    def ansi_printer(to_print):
        print(''.join((f_str, to_print, Style['RESET_ALL'],)))
    yield ansi_printer

def ansi_print(to_print, fg='', bg='', style=''):
    with print_style(fg=fg, bg=bg, style=style) as printer:
        printer(to_print)
    return True

def format_string(fg='', bg='', style=''):
    if isinstance(style,str):
        st_str = Style.get(style.upper(), '') 
    else:
        st_str = ''.join([Style.get(sty.upper(), '') for sty in style])
    return ''.join((Fore.get(fg.upper(), ''), Back.get(bg.upper(), ''), st_str,))

def ansi_string(to_print, fg='', bg='', style='', reset=True):
    a_str = ''.join((format_string(fg, bg, style),to_print))
    if reset:
        a_str += Style['RESET_ALL']
    return a_str
