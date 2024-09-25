"""
libpttea.ptt_functions
~~~~~~~~~~~~

This module implements various PTT functions.
"""

import queue
import re
import threading

from . import pattern, ptt_action
from .sessions import Session
from .websocket_client import WebSocketClient


def login(session: Session, account: str, password: str) -> Session:
    """Log in to PTT."""

    # create connection
    session.websocket_client = WebSocketClient()
    session.ws_queue = session.websocket_client.ws_queue
    session.ws_connection = session.websocket_client.ws_connection

    session.thread_client = threading.Thread(target=session.websocket_client.connect)

    print("### start connect")
    session.thread_client.start()

    # Wait for the client thread to connect.
    while True:
        if session.websocket_client.connected is True:
            break
    print("### connected")

    # start login
    # Use Big5 first and ignore errors (ignore Big5-UAO)

    # Wait for the login screen to load.
    while True:
        message = session.receive("big5")
        if "請輸入代號，或以 guest 參觀，或以 new 註冊" in message:
            break

    # send account
    session.send(account)

    # check receive
    message = session.receive("utf-8")
    if message != account:
        raise RuntimeError("The sent account could not be verified.")

    session.send(pattern.NEW_LINE)

    # check password input
    message = session.receive("big5")
    if "請輸入您的密碼" not in message:
        raise RuntimeError()

    # send password
    session.send(password)
    session.send(pattern.NEW_LINE)

    # Check if the login was successful.
    # If the login fails, will receive a mix of UTF-8 and Big5 UAO data.
    message = session.receive("utf-8")
    if "密碼正確" not in message:
        raise RuntimeError("Account or password is incorrect.")

    # Check if the login process is starting to load.
    message = session.receive("utf-8")
    if "登入中，請稍候" not in message:
        raise RuntimeError("Check if the login start loading failed.")

    print("### logged in")
    return session

def skip_init(session: Session, del_duplicate=True, del_error_log=True) -> Session:
    """Skip the initialization step until the home menu is loaded."""
    
    message = session.receive_to_buffer()

    # Skip - duplicate connections
    # 注意: 您有其它連線已登入此帳號。您想刪除其他重複登入的連線嗎？[Y/n]
    find_duplicate = "您想刪除其他重複登入的連線嗎"
    if find_duplicate in message:
        # Send selection
        if del_duplicate == True:
            session.send("y")
            session.until_string("y")
        else:
            session.send("n")
            session.until_string("n")

        session.send(pattern.NEW_LINE)

        # Wait for duplicate connections to be deleted
        session.until_string("按任意鍵繼續", timeout=10)
    elif "按任意鍵繼續" not in message:
        # if not in first message
        session.until_string("按任意鍵繼續")

    # Skip - if the system is busy
    session.flush_buffer()
    session.a2h_screen.buffer_clear_old()
    current_screen_str = session.a2h_screen.peek_string()

    find_busy = "請勿頻繁登入以免造成系統過度負荷"
    if find_busy in current_screen_str:

        session.send(pattern.NEW_LINE)

        # until next loaded
        session.until_string("按任意鍵繼續")
        session.flush_buffer()

        session.a2h_screen.buffer_clear_old()
        current_screen_str = session.a2h_screen.peek_string()

    # Skip - last login ip
    find_last = "歡迎您再度拜訪，上次您是從"
    if find_last in current_screen_str:
        session.send(pattern.NEW_LINE)
    else:
        raise RuntimeError()

    # Skip - Last login attempt failed
    message = session.receive_to_buffer()

    find_error_log = "您要刪除以上錯誤嘗試的記錄嗎"
    if find_error_log in message:
        # Send selection
        if del_error_log == True:
            session.send("y")
            session.until_string("y")
        else:
            session.send("n")
            session.until_string("n")

        session.send(pattern.NEW_LINE)
        session.clear_buffer()
    else:
        session.a2h_screen.buffer_clear()

    # Wait for the home menu to load
    ptt_action.home_loaded_status_bar(session)

    session.flush_buffer()
    session.a2h_screen.parse()
    session.current_location = "home"

    return session


def logout(session: Session) -> None:
    """Log out from PTT."""

    if not ptt_action.is_home(session):
        raise RuntimeError()

    # select index , 離開，再見
    session.send("g")
    session.send(pattern.RIGHT_ARROW)

    # wait ask
    # 您確定要離開【 批踢踢實業坊 】嗎(Y/N)？
    session.until_string("您確定要離開")

    # send yes
    session.send("y")
    session.until_string("y")
    session.send(pattern.NEW_LINE)

    # check logout success
    session.until_string("期待您下一次的光臨")

    return


def get_system_info(session: Session) -> tuple[Session, list]:
    """get the system info (查看系統資訊)."""

    if not ptt_action.is_home(session):
        raise RuntimeError("Verification is in the home page failed.")

    ptt_action.home_to_sys_info_area(session)
    session.flush_buffer()

    ptt_action.sys_info_area_to_sys_info(session)
    session.flush_buffer()

    # page
    session.a2h_screen.parse()
    system_info_page = session.a2h_screen.to_formatted_string()

    # back
    ptt_action.sys_info_to_sys_info_area(session)
    ptt_action.sys_info_area_to_home(session)

    session.flush_buffer()
    session.a2h_screen.parse()

    return session, system_info_page


def get_favorite_list(session: Session) -> tuple[Session, list]:
    """get the user's favorite list."""

    if not ptt_action.is_home(session):
        raise RuntimeError("Verification is in the home page failed.")

    ptt_action.home_to_favorite(session)
    session.flush_buffer()

    # pages
    favorite_pages = []

    session.a2h_screen.parse()
    favorite_pages.append(session.a2h_screen.to_formatted_string())

    # check if more than 1 page
    session.send(pattern.PAGE_DOWN)  # to next page
    while True:
        message = session.receive_to_buffer()

        if "\x1b[4;1H" in message:
            # [4;1H
            # more than 1 page , now in next page
            session.flush_buffer()
            session.a2h_screen.parse()

            current_page = session.a2h_screen.to_formatted_string()
            favorite_pages.append(current_page)

            if current_page[-2] == "":
                # next page only has 1 item
                break
            else:
                session.send(pattern.PAGE_DOWN)  # to next page
                continue

        match = re.search(R"\d{1,2};1H>", message)
        if match:
            # Check if the "greater-than sign" has moved.
            # Same page, finished.
            break

    # back to first page
    session.send(pattern.PAGE_DOWN)

    # back
    ptt_action.favorite_to_home(session)

    session.flush_buffer()
    session.a2h_screen.parse()

    return session, favorite_pages


def get_post_list(session: Session, board: str, number=20) -> tuple[Session, list]:
    """get the post list for the board, starting with the latest post."""

    if not ptt_action.is_home(session):
        raise RuntimeError()

    ptt_action.home_to_favorite(session)
    session.flush_buffer()

    ptt_action.favorite_to_board(session, board)
    session.flush_buffer()

    # get the required number of posts
    post_list_pages = []
    got_number = 0

    # add current page
    session.a2h_screen.parse()
    post_list_pages.append(session.a2h_screen.to_formatted_string())
    got_number += 20

    # other pages
    while got_number < number:
        # next page
        session.send(pattern.PAGE_UP)

        # new page loaded
        # [4;1H
        session.until_regex(R".+\x1B\[\d{1,2};1H")
        session.flush_buffer()

        session.a2h_screen.parse()
        post_list_pages.append(session.a2h_screen.to_formatted_string())

        got_number += 20

    # back
    ptt_action.board_to_favorite(session)
    session.flush_buffer()

    ptt_action.favorite_to_home(session)
    session.flush_buffer()

    session.a2h_screen.parse()

    return session, post_list_pages


def get_post_all(session: Session, board: str, post_index: int) -> tuple[Session, list, list]:
    """get the entire content of the post."""

    if not ptt_action.is_home(session):
        raise RuntimeError()

    ptt_action.home_to_favorite(session)
    session.flush_buffer()

    ptt_action.favorite_to_board(session, board)
    session.flush_buffer()

    ptt_action.board_to_post(session, post_index)
    session.flush_buffer()

    # post pages
    post_pages = []
    raw_post_pages = []

    session.a2h_screen.parse()
    current_page = session.a2h_screen.to_formatted_string()
    post_pages.append(current_page)
    raw_post_pages.append(session.a2h_screen.parsed_screen())

    # load all post
    # use the status bar to check the load state
    # Load all posts.
    while "(100%)" not in current_page[-1]:

        session.send(pattern.PAGE_DOWN)  # next page

        try:
            session.until_regex(pattern.regex_post_end_strict)
        except queue.Empty:
            # sometimes in the (100%) condition, the message does not end with "\x1b[24;80H"
            # check if it is in the current buffer
            current_buffer = b"".join(session.received_binary_buffer)
            message = current_buffer.decode(encoding='utf-8', errors="ignore")

            # [30m推文[31m(h)[30m說明[31m(  ←[24;74H)[30m離開 [m
            match = re.search(R"\x1b\[30m離開.+\x1b\[m", message)
            if match is None:
                session.until_regex(R"\x1b\[30m離開.+\x1b\[m")

        session.flush_buffer()
        session.a2h_screen.parse()

        current_page = session.a2h_screen.to_formatted_string()
        post_pages.append(current_page)
        raw_post_pages.append(session.a2h_screen.parsed_screen())

    # back
    ptt_action.post_to_board(session)
    ptt_action.board_to_favorite(session)
    ptt_action.favorite_to_home(session)

    session.flush_buffer()
    session.a2h_screen.parse()

    return session, post_pages, raw_post_pages
