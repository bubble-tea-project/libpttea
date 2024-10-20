"""
libpttea.ptt_functions
~~~~~~~~~~~~

This module implements various PTT functions.
"""

import asyncio
import logging

from . import data_processor, pattern
from .sessions import Session
from .websocket_client import WebSocketClient


logger = logging.getLogger("libpttea")


async def _login(session: Session, account: str, password: str) -> Session:
    """Create connection and log in."""

    # create connection
    session = Session()
    session.websocket_client = WebSocketClient()

    asyncio.create_task(session.websocket_client.connect())
    logger.info("Connect to the WebSocket server")

    # Wait for connected
    await session.websocket_client.connected.wait()
    logger.info("WebSocket is connected")

    # Start login
    # Use Big5 first and ignore errors (ignore Big5-UAO)
    logger.info("Start login")

    # Wait for the login screen to load.
    logger.debug("Wait for the login screen to load.")
    while True:
        raw_message = await session.receive_raw()
        message = raw_message.decode("big5", errors="ignore")
        if "請輸入代號，或以 guest 參觀，或以 new 註冊" in message:
            break

    # send account
    logger.debug(f"send account,{account}")
    session.send(account)

    # verify account
    logger.debug("verify account")

    raw_message = await session.receive_raw()
    message = raw_message.decode("utf-8", errors="ignore")
    if message != account:
        raise RuntimeError("The sent account could not be verified.")
    else:
        session.send(pattern.NEW_LINE)

    # check password hint
    logger.debug("check password hint")

    raw_message = await session.receive_raw()
    message = raw_message.decode("big5", errors="ignore")
    if "請輸入您的密碼" not in message:
        raise RuntimeError("Check password hint failed.")

    # send password
    logger.debug("send password")

    session.send(password)
    session.send(pattern.NEW_LINE)

    # Check if the login was successful.
    # If the login fails, will receive a mix of UTF-8 and Big5 UAO data.
    logger.debug("Check if the login was successful.")

    raw_message = await session.receive_raw()
    message = raw_message.decode("utf-8", errors="ignore")
    if "密碼正確" not in message:
        raise RuntimeError("Account or password is incorrect.")

    # Check if the login process is starting to load.
    logger.debug("Check if the login process is starting to load.")

    raw_message = await session.receive_raw()
    message = raw_message.decode("utf-8", errors="ignore")
    if "登入中，請稍候" not in message:
        raise RuntimeError("Check if the login start loading failed.")

    logger.info("Logged in")
    return session


async def _skip_login_init(session: Session, del_duplicate=True, del_error_log=True) -> None:
    """Skip the login initialization step until the home menu is loaded."""

    logger.info("Skip the login initialization step")

    # Skip - duplicate connections
    # 注意: 您有其它連線已登入此帳號。您想刪除其他重複登入的連線嗎？[Y/n]
    messages = []

    message = await session.receive()
    messages.append(message)

    find_duplicate = "您想刪除其他重複登入的連線嗎"
    if find_duplicate in message:
        logger.debug("Skip - duplicate connections")

        # Send selection
        if del_duplicate == True:
            session.send("y")
            await session.until_string("y", drop=True)
        else:
            session.send("n")
            await session.until_string("n", drop=True)

        session.send(pattern.NEW_LINE)

        # Wait for duplicate connections to be deleted
        messages = await session.until_string("按任意鍵繼續", timeout=15)
    elif "按任意鍵繼續" not in message:
        # no duplicate connections
        # and if not in first message
        messages.extend(await session.until_string("按任意鍵繼續"))

    # Skip - system is busy
    find_busy = "請勿頻繁登入以免造成系統過度負荷"
    if any(find_busy in _ for _ in messages):
        logger.debug("Skip - system is busy")
        session.send(pattern.NEW_LINE)

        # until last login ip
        messages = await session.until_string("按任意鍵繼續")

    # Skip - last login ip
    find_last_ip = "歡迎您再度拜訪，上次您是從"
    if any(find_last_ip in _ for _ in messages):
        logger.debug("Skip - last login ip")
        session.send(pattern.NEW_LINE)
    else:
        raise RuntimeError()

    # Skip - Last login attempt failed
    messages = []

    message = await session.receive()

    find_error_log = "您要刪除以上錯誤嘗試的記錄嗎"
    if find_error_log in message:
        logger.debug("Skip - Last login attempt failed")

        # Send selection
        if del_error_log == True:
            session.send("y")
            await session.until_string("y", drop=True)
        else:
            session.send("n")
            await session.until_string("n", drop=True)

        session.send(pattern.NEW_LINE)
    else:
        messages.append(message)

    # Wait for the home menu to load
    for message in messages:
        session.ansip_screen.put(message)

    while True:
        await session.receive_and_put()

        if session.router.in_home():
            # init router
            session.router.init_home()
            break

    return


async def login(session: Session, account: str, password: str, del_duplicate: bool, del_error_log: bool) -> Session:
    """Log in to PTT."""

    logger.info("login")

    if session is not None:
        raise RuntimeError("Is already logged in.")

    # Add ',' to get the UTF-8 response from the PTT WebSocket connection.
    session = await _login(session, account + ",", password)

    await _skip_login_init(session, del_duplicate, del_error_log)

    return session


async def _get_system_info_page(session: Session) -> list:
    """get the PTT system info page"""

    if session.router.location() != "/utility/info":
        await session.router.go("/utility/info")

    system_info_page = session.ansip_screen.to_formatted_string()
    logger.debug("Got system_info_page.")

    return system_info_page


async def get_system_info(session: Session) -> list:
    """get the PTT system info"""

    logger.info("get_system_info")

    if session is None:
        raise RuntimeError("Not logged in yet.")

    system_info_page = await _get_system_info_page(session)

    system_info = data_processor.get_system_info(system_info_page)

    return system_info


async def _logout(session: Session) -> None:
    """Log out from PTT."""

    if session.router.location() != "/":
        await session.router.go("/")

    # select logout index , 離開，再見
    logger.debug("select logout index")
    session.send("g")
    session.send(pattern.RIGHT_ARROW)

    # Wait for logout confirmation prompt.
    # 您確定要離開【 批踢踢實業坊 】嗎(Y/N)？
    logger.debug("Wait for logout confirmation prompt")
    await session.until_string("您確定要離開")

    # send yes
    logger.debug("send yes")
    session.send("y")
    await session.until_string("y")
    session.send(pattern.NEW_LINE)

    # check logout success
    logger.debug("check logout success")
    await session.until_string("期待您下一次的光臨")

    return


async def logout(session: Session, force=False) -> None:
    """Log out from PTT."""

    logger.info("logout")

    if session is None:
        raise RuntimeError("Is already logged out")

    try:
        await _logout(session)
    except TimeoutError:
        logger.debug("logout timeout")

        if force is False:
            raise RuntimeError("logout failed")
        else:
            logger.info("force logout")

    logger.info("Logged out")

    await session.websocket_client.close()
    session = None
