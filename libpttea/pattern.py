"""
libpttea.pattern
~~~~~~~~~~~~

This module implements commonly used patterns for libpttea.
"""

import re


# keyboard
# ---
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
# ---

# /favorite/C_Chat
# r'^/favorite/\w+$'
regex_path_at_board = re.compile(R'''
    ^/favorite/     # "/favorite/"
    \w+$             # board and ensure is end               
''', re.VERBOSE)

# /favorite/C_Chat/335045
# r'^/favorite/\w+/\d+'
regex_path_at_post_index = re.compile(R'''
    ^/favorite/     # "/favorite/"
    \w+             # board
    /\d+            # "/335045" ,  post index
''', re.VERBOSE)


# r'.+\x1b(?:\[[^\x40-\x7E]*)?$'
regex_incomplete_ansi_escape = re.compile(R'''
    .*                      # any
    \x1b                    # start with '\x1B'                                   
    (?:
        \[[^\x40-\x7E]*     # Final characters that are not valid terminators                            
    )?$                     # at end ,zero or one times           
''', re.VERBOSE)


# [00/0 星期天 00:00] [ 牡羊時 ]    線上66666人, 我是TEST         [呼叫器]打開
# r'\[\d+\/\d+\s\S+\s\d+:\d+\].+人,.+\[呼叫器\](?:打開|拔掉|防水|好友)'
regex_menu_status_bar = re.compile(R'''
    \[\d+\/\d+\s\S+\s\d+:\d+\]    # [0/00 星期五 22:00]
    .+人,.+                       # Intermediate part
    \[呼叫器\]                     # [呼叫器]
    (?:打開|拔掉|防水|好友)          #                               
''', re.VERBOSE)

# 文章選讀  (y)回應(X)推文(^X)轉錄 (=[]<>)相關主題(/?a)找標題/作者 (b)進板畫面
# r'文章選讀.+進板畫面'
regex_board_status_bar = re.compile(R'''
    文章選讀        # '文章選讀'
    .+            # Intermediate part
    進板畫面        # '進板畫面'
''', re.VERBOSE)

# 瀏覽 第 1/4 頁 ( 12%)  目前顯示: 第 01~25 行                                (y)回應(X%)推文(h)說明(← )離開
# r'瀏覽.+目前顯示.+說明.+離開'
regex_post_status_bar_simple = re.compile(R'''
    瀏覽         # 
    .+          # Intermediate part
    目前顯示      # 
    .+          # Intermediate part
    說明         #
    .+          # Intermediate part
    離開         #                                                                                                                         
''', re.VERBOSE)

# 瀏覽 第 1/4 頁 ( 12%)  目前顯示: 第 01~25 行                                (y)回應(X%)推文(h)說明(← )離開
# r'瀏覽.+\(\s{0,2}(?P<progress>\d+)%\).+第\s(?P<start>\d+)~(?P<end>\d+)\s行.+離開'
regex_post_status_bar = re.compile(R'''
    瀏覽                                 # 
    .+                                  # Intermediate part
    \(\s{0,2}(?P<progress>\d+)%\)       # '( 12%)' , progress
    .+                                  # Intermediate part
    第                                  #   
    \s(?P<start>\d+)                    # start line
    ~                                   # Intermediate part
    (?P<end>\d+)                        # end line    
    \s行.+離開                           #                                                                                                                                                    
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

# (?P<type>[推→噓])\s(?P<author>\w+):\s(?P<reply>.+)\s(?P<ip>(?:\d{1,3}\.?){4})?\s(?P<datetime>\d{1,2}\/\d{1,2}\s\d{2}:\d{2})
regex_post_reply = re.compile(R'''
    (?P<type>[推→噓])     # reply type
    \s   #                            
    (?P<author>\w+) # author
    :\s                               
    (?P<reply>.+)   # reply content
    \s
    (?P<ip>(?:\d{1,3}\.?){4})?  # ip ,optional
    \s
    (?P<datetime>\d{1,2}\/\d{1,2}\s\d{2}:\d{2}) # datetime                                                                                                                   
''', re.VERBOSE)

# The post has no content; it has already been deleted.
# r'此文章無內容.+按任意鍵繼續'
regex_post_no_content = re.compile(R'''
    此文章無內容       # 
    .+               # Intermediate part
    按任意鍵繼續       # 
''', re.VERBOSE)
