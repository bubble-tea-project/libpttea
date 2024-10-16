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


async def _login(session: Session, account: str, password: str) -> Session:
    
    # create connection
    session = Session()

    session.websocket_client = WebSocketClient()
    session.thread_client = threading.Thread(target=session.websocket_client.connect)

    session.ws_queue = session.websocket_client.ws_queue
    session.ws_connection = session.websocket_client.ws_connection


    print("### start connect")
    session.thread_client.start()

    # Wait for connected
    while True:
        if session.websocket_client.connected is True:
            break
    print("### connected")


    # start login
    # Use Big5 first and ignore errors (ignore Big5-UAO)

    # Wait for the login screen to load.
    while True:
        raw_message = await session.receive_raw()
        message = raw_message.decode("big5", errors="ignore")
        if "請輸入代號，或以 guest 參觀，或以 new 註冊" in message:
            break

    # send account
    session.send(account)

    # verify account
    raw_message = await session.receive_raw()
    message = raw_message.decode("utf-8", errors="ignore")
    if message != account:
        raise RuntimeError("The sent account could not be verified.")
    else:
        session.send(pattern.NEW_LINE)

    # check password hint
    raw_message = await session.receive_raw()
    message = raw_message.decode("big5", errors="ignore")
    if "請輸入您的密碼" not in message:
        raise RuntimeError()

    # send password
    session.send(password)
    session.send(pattern.NEW_LINE)

    # Check if the login was successful.
    # If the login fails, will receive a mix of UTF-8 and Big5 UAO data.
    raw_message = await session.receive_raw()
    message = raw_message.decode("utf-8", errors="ignore")
    if "密碼正確" not in message:
        raise RuntimeError("Account or password is incorrect.")

    # Check if the login process is starting to load.
    raw_message = await session.receive_raw()
    message = raw_message.decode("utf-8", errors="ignore")
    if "登入中，請稍候" not in message:
        raise RuntimeError("Check if the login start loading failed.")


    print("### logged in")
    return session


async def _skip_login_init(session: Session, del_duplicate=True, del_error_log=True) -> Session:
    """skip the login initialization step until the home menu is loaded."""
    
    # Skip - duplicate connections
    # 注意: 您有其它連線已登入此帳號。您想刪除其他重複登入的連線嗎？[Y/n]
    messages = []

    message = await session.receive()
    messages.append(message)

    find_duplicate = "您想刪除其他重複登入的連線嗎"
    if find_duplicate in message:
        # Send selection
        if del_duplicate == True:
            session.send("y")
            await session.until_string("y",drop=True)
        else:
            session.send("n")
            await session.until_string("n",drop=True)

        session.send(pattern.NEW_LINE)

        # Wait for duplicate connections to be deleted
        messages = await session.until_string("按任意鍵繼續", timeout=10)
    elif "按任意鍵繼續" not in message:
        # no duplicate
        # if not in first message
        messages.extend( await session.until_string("按任意鍵繼續") )


    # Skip - if the system is busy
    find_busy = "請勿頻繁登入以免造成系統過度負荷"
    if any(find_busy in _ for _ in messages):
        session.send(pattern.NEW_LINE)

        # until last login ip
        messages = await session.until_string("按任意鍵繼續")
        

    # Skip - last login ip
    find_last_ip = "歡迎您再度拜訪，上次您是從"
    if any(find_last_ip in _ for _ in messages):
        session.send(pattern.NEW_LINE)
    else:
        raise RuntimeError()


    # Skip - Last login attempt failed
    messages = []

    message = await session.receive()

    find_error_log = "您要刪除以上錯誤嘗試的記錄嗎"
    if find_error_log in message:
        # Send selection
        if del_error_log == True:
            session.send("y")
            await session.until_string("y",drop=True)
        else:
            session.send("n")
            await session.until_string("n",drop=True)

        session.send(pattern.NEW_LINE)
    else:
        messages.append(message)


    # Wait for the home menu to load
    while True:
        
        message = await session.receive()
        messages.append(message)

        if "\x1b[m\x1b[16;21H" in message:
            break
    
    # ----
    for message in messages:
        session.ansip_screen.put( message )

    session.ansip_screen.parse()
    tmp = session.ansip_screen.to_formatted_string()
    # ptt_action.home_loaded_status_bar(session)

    # session.flush_buffer()
    # session.ansip_screen.parse()
    # session.current_location = "home"


    # ------
    

    return session


async def login(session: Session,  account: str, password: str, del_duplicate:bool, del_error_log:bool) -> Session:
    """Log in to PTT."""

    if session is not None:
        raise RuntimeError("Is logged in")
         

    # add ',' for use utf8 in  Websocket
    session = await _login(session, account + ",", password)

    session = await _skip_login_init(session, del_duplicate ,del_error_log)







    return