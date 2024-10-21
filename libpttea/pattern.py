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

# r'文章選讀.+進板畫面'
# 文章選讀  (y)回應(X)推文(^X)轉錄 (=[]<>)相關主題(/?a)找標題/作者 (b)進板畫面
regex_board_status_bar = re.compile(R'''
    文章選讀        # '文章選讀'
    .+            # Intermediate part
    進板畫面       # '進板畫面'
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


# cursor has moved in favorite list
# '>     5   '
# r'>\s+(?!1\s)\d+\s{3}'
regex_favorite_cursor_moved = re.compile(R'''
    >\s+            # ">     "
    (?!1\s)\d+      # digit , excludes 1
    \s{3}           # '5   ' , space after digit               
''', re.VERBOSE)

# cursor not moved in favorite list
# '>     1   '
# r'>\s{5}1\s{3}'
regex_favorite_cursor_not_moved = re.compile(R'''
    >\s{5}      # ">     "
    1           # digit  1
    \s{3}       # '1   ' , space after digit               
''', re.VERBOSE)


# path at board
# /favorite/C_Chat
# r'^/favorite/\w+$'
regex_path_at_board = re.compile(R'''
    ^/favorite/     # "/favorite/"
    \w+$             # board and ensure is end               
''', re.VERBOSE)


# post_item
# https://www.ptt.cc/bbs/PttNewhand/M.1286283859.A.F6D.html
# https://www.ptt.cc/bbs/PttNewhand/M.1265292872.A.991.html
# 351393 + 3 9/24 yankeefat    □ [敗北] 騙人...的八...
# r'(?P<index>\d+|★)\s+(?P<label>\D)?(?P<count>爆|[\s\d]{2}|XX|X\d)?\s{0,1}(?P<date>\d{1,2}/\d{1,2})\s(?P<author>\S+)\s+(?P<title>.+)'
regex_post_item = re.compile(R'''
    (?P<index>\d+|★)                   # index , number or the '★' symbol
    \s+                                 # One or more spaces   
    (?P<label>\D)?                      # label, optional , "+" , "m" , or other   
    (?P<count>爆|[\s\d]{2}|XX|X\d)?     # count ,optional
    \s{0,1}                             # zero or one spaces   
    (?P<date>\d{1,2}/\d{1,2})           # date , in 'MM/DD' format
    \s                                  # One space
    (?P<author>\S+)                     # author    
    \s+                                 # One or more spaces 
    (?P<title>.+)                       # post title                                                                                                                                                     
''', re.VERBOSE)


