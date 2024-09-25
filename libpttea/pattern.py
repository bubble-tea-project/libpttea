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


# Strict version: exclude the '100% condition at the end of the post' (last page split into two parts).
# r'\d{1,}~\d{1,}.+\x1b\[m\x1b\[24;80H'
regex_post_end_strict = re.compile(R'''
    \d{1,}~\d{1,}    # 第 xx~xx 行
    .+    # Intermediate part
    \x1b\[m\x1b\[24;80H  # use '\x1b[24;80H' as end 
''', re.VERBOSE)

# Loose version: include the '100% condition at the end of the post.'
# r'\d{1,}~\d{1,}.+\x1b\[m'
regex_post_end_loose = re.compile(R'''
    \d{1,}~\d{1,}    # 第 xx~xx 行
    .+    # Intermediate part
    \x1b\[m  # use '\x1b[m' as end 
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


# https://www.ptt.cc/bbs/PttNewhand/M.1286283859.A.F6D.html
# https://www.ptt.cc/bbs/PttNewhand/M.1265292872.A.991.html
# 351393 + 3 9/24 yankeefat    □ [敗北] 騙人...的八...
# r'(?P<index>\d+|★)\s+(?P<label>\D)?\s*(?P<count>爆|\d{1,2}|XX|X\d)?\s+(?P<date>\d{1,2}/\d{1,2})\s(?P<author>\S+)\s+(?P<title>.+)'
regex_post_item =  re.compile(R'''
    (?P<index>\d+|★)           # index , number or the '★' symbol
    \s+                         # One or more spaces   
    (?P<label>\D)?              # label, optional , "+" , "m" , or other   
    \s*                         # Optional spaces
    (?P<count>爆|\d{1,2}|XX|X\d)?   # count ,optional
    \s+                         # One or more spaces   
    (?P<date>\d{1,2}/\d{1,2})   # date , in 'MM/DD' format
    \s                          # One space
    (?P<author>\S+)             # author    
    \s+                         # One or more spaces 
    (?P<title>.+)               # post title                                                                                                                                                     
''', re.VERBOSE)


#   瀏覽 第 1/5 頁 ( 11%)  目前顯示: 第 01~22 行  (y)回應(X%)推文(h)說明(←)離開 
# r'第\s(?P<start>\d+)~(?P<end>\d+)\s行'
regex_post_display_line = re.compile(R'''
    第\s            # "第 "
    (?P<start>\d+)  # start line                         
    ~               # ~
    (?P<end>\d+)    # end line
    \s行            # " 行"                                
''', re.VERBOSE)