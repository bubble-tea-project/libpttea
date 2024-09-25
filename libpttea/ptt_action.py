"""
libpttea.ptt_action
~~~~~~~~~~~~~~~~~

This module provides functions that wrap user operations to interact with PTT.
"""

import queue
import re

from . import pattern
from .sessions import Session


def is_home(session: Session) -> bool:
    """Check if the current page is the home page."""

    current_page = session.a2h_screen.to_formatted_string()

    # Check the title line
    if "主功能" not in current_page[0]:
        return False

    # check status bar
    match = re.search(pattern.regex_menu_status_bar, current_page[-1])
    if match is None:
        return False

    return True


def home_loaded_status_bar(session: Session) -> None:
    """Wait for the home menu to load completely (with status bar)."""

    # [34;46m[0/00 星期一 0:00][1;33;45m [ xx時 ]   [30;47m 線上[31m32376[30m人, 我是[31m xxxxx[30m          [呼叫器][31m打
    # 開 [m[16;21H
    session.until_string("\x1b[m\x1b[16;21H")

    session.current_location = "home"
    return


def home_to_sys_info_area(session: Session) -> None:
    """From the home menu to the sys_info_area (系統資訊區)."""

    # select index , 系統資訊區
    session.send("x")
    session.send(pattern.RIGHT_ARROW)

    # wait sys_info_area loaded
    session.until_string("《查看系統資訊》")

    session.current_location = "sys_info_area"
    return

def sys_info_area_to_home(session: Session) -> None:
    """from sys_info_area(系統資訊區) to home"""

    # back
    session.send(pattern.LEFT_ARROW)

    # wait home loaded
    # 【 系統資訊區 】[K[20;23H([1;36mG[m)oodbye[20;41H離開，再見
    session.until_string("\x1b[20;41H離開，再見")

    session.current_location = "home"
    return


def sys_info_area_to_sys_info(session: Session) -> None:
    """From sys_info_area (系統資訊區) to sys_info (查看系統資訊)."""

    # select index , 查看系統資訊
    session.send("x")
    session.send(pattern.RIGHT_ARROW)

    # wait sys_info loaded
    session.until_string("請按任意鍵繼續")

    session.current_location = "sys_info"
    return

def sys_info_to_sys_info_area(session: Session) -> None:
    """from sys_info(查看系統資訊) to sys_info_area(系統資訊區) """

    # back
    # 請按任意鍵繼續
    session.send(pattern.NEW_LINE)

    # wait sys_info_area loaded
    # [呼叫器][31m打開 [m[19;21H
    session.until_string("\x1b[m\x1b[19;21H")

    session.current_location = "sys_info_area"
    return


def home_to_favorite(session: Session) -> None:
    """from home menu to favorite(我 的 最愛)"""

    # select index , 我 的 最愛
    session.send("f")
    session.send(pattern.RIGHT_ARROW)

    # wait favorite loaded
    # [30m列出全部 [31m(v/V)[30m已讀/未讀
    session.until_string("已讀/未讀")

    session.current_location = "favorite"
    return

def favorite_to_home(session: Session) -> None:
    """from favorite(我 的 最愛) to home menu"""

    # back
    session.send(pattern.LEFT_ARROW)

    # wait home loaded
    # [呼叫器][31m打開 [m[15;21H
    session.until_string("\x1b[15;21H")

    session.current_location = "home"
    return


def favorite_to_board(session: Session, board: str) -> None:
    """from favorite(我 的 最愛) to board"""

    # (s)進入已知板名
    session.send("s")
    session.until_string("請輸入看板名稱(按空白鍵自動搜尋)")

    session.send(board)
    session.until_string(board)
    session.send(pattern.NEW_LINE)

    # If the board is in the favorite list,
    # check if the "greater-than sign" has moved.
    session.until_regex(R">.+\x1b\[\d{1,2};\d{1,2}H")
    session.flush_buffer()

    # to board
    session.send(pattern.RIGHT_ARROW)
    while True:
        message = session.receive_to_buffer()

        if "請按任意鍵繼續" in message:
            # skip Enter board screen
            session.send(pattern.RIGHT_ARROW)
            session.clear_buffer()

        # [30m進板畫面  [m[18;1H
        match = re.search(R"\x1b\[\d{1,2};1H", message)
        if match:
            # in board , loaded
            break

    # to the latest
    session.send(pattern.END)
    try:
        # check if the "greater-than sign" has moved.
        session.until_string("> ", 2)
    except queue.Empty:
        pass

    session.current_location = "board"
    return

def board_to_favorite(session: Session) -> None:
    """from board to favorite(我 的 最愛)"""

    # back
    session.send(pattern.LEFT_ARROW)

    # wait favorite loaded
    # [30m列出全部 [31m(v/V)[30m已讀/未讀
    session.until_string("已讀/未讀")

    session.current_location = "favorite"
    return


def board_to_post(session: Session, post_index) -> None:
    """from board to post"""

    # find post
    session.send(str(post_index))
    session.until_string("跳至第幾項")
    session.send(pattern.NEW_LINE)

    # Check if found
    while True:
        message = session.receive_to_buffer()

        match = re.search(R"進板畫面  \x1b\[m\x1b\[\d{1,2};1H", message)
        if match:
            # found in different page
            break

        match = re.search(R"\x1b\[K\x1b\[\d{1,2};1H", message)
        if match:
            # found in same page
            break

    # recheck
    session.flush_buffer()

    regex_post_id = R"^(>| )" + str(post_index)
    found_page = session.a2h_screen.to_formatted_string(peek=True)
    if not any([re.search(regex_post_id, item) for item in found_page]):
        raise RuntimeError("post_index not found")

    # go to post
    session.clear_buffer()
    session.send(pattern.RIGHT_ARROW)

    # wait post loaded
    # [30m說明[31m(  ←[24;74H)[30m離開[m[24;80H
    session.until_regex(R"\x1b\[30m離開\s*\x1b\[m")

    session.current_location = "post"
    return

def post_to_board(session: Session) -> None:
    """from post to board"""

    # back
    session.send(pattern.LEFT_ARROW)

    # wait board loaded
    # [30m找標題/作者 [31m(b)[30m進板畫面 [m[12;1H
    session.until_string("\x1b[30m進板畫面")

    session.current_location = "board"
    return
