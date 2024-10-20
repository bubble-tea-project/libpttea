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


# regular expression

# r'\[\d+\/\d+\s\S+\s\d+:\d+\].+人,.+\[呼叫器\].+'
regex_menu_status_bar = re.compile(R'''
    \[\d+\/\d+\s\S+\s\d+:\d+\]    # [0/00 星期五 22:00]
    .+人,.+    # Intermediate part
    \[呼叫器\].+  # [呼叫器]打開
''', re.VERBOSE)


# favorite_item normal
# 3 ˇC_Chat       閒談 ◎[希洽] 從來不覺得開心過       爆!Satoman/nh50
# r'(?P<index>\d+)\s+ˇ?(?P<board>\S+)\s+(?P<type>\S+)\s+◎(?P<describe>.*\S+)\s{2,}(?P<popularity>爆!|HOT|\d{1,2})?\s*(?P<moderator>\w+.+)'
regex_favorite_item = re.compile(R'''
    (?P<index>\d+)               # Captures the index, "3"
    \s+                          # One or more spaces
    ˇ?                           # Optional ˇ character
    (?P<board>\S+)               # Board name , "C_Chat"
    \s+                          # One or more spaces
    (?P<type>\S+)                # Type , "閒談"
    \s+◎                         # Intermediate
    (?P<describe>.*\S+)          # Describe field , "[希洽] 從來不覺得開心過"
    \s{2,}                       # Two or more spaces
    (?P<popularity>爆!|HOT|\d{1,2})?  # Popularity, optional : "爆!", "HOT", or 1-2 digit number
    \s*                          # Optional spaces
    (?P<moderator>\w+.+)?        # Moderator, optional , "Satoman/nh50"
''', re.VERBOSE)

# favorite_item but no popularity and moderator
# r'(?P<index>\d+)\s+ˇ?(?P<board>\S+)\s+(?P<type>\S+)\s+◎(?P<describe>.*\S+)'
regex_favorite_item_describe = R"(?P<index>\d+)\s+ˇ?(?P<board>\S+)\s+(?P<type>\S+)\s+◎(?P<describe>.*\S+)"