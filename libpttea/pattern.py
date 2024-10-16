"""
libpttea.pattern
~~~~~~~~~~~~

This module implements commonly used patterns for libpttea.
"""

import re


# keyboard
NEW_LINE = "\r\n"

# https://en.wikipedia.org/wiki/ANSI_escape_code#Terminal_input_sequences
UP_ARROW = "\x1b[A"
DOWN_ARROW = "\x1b[B"
LEFT_ARROW = "\x1b[D"
RIGHT_ARROW = "\x1b[C"

HOME = "\x1b[1~"
END = "\x1b[4~"
PAGE_UP = "\x1b[5~"
PAGE_DOWN = "\x1b[6~"
