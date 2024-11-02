"""
libpttea.ptt_functions
~~~~~~~~~~~~

This module implements various PTT functions.
"""

from __future__ import annotations
import asyncio
import logging
import re
import typing

import ansiparser

from . import data_processor, pattern, ptt_action
from .sessions import Session
from .websocket_client import WebSocketClient

if typing.TYPE_CHECKING:
    from typing import AsyncGenerator


logger = logging.getLogger("libpttea")


async def _login(session: Session, account: str, password: str) -> Session:
    """Create connection and log in."""

    # create connection
    session = Session()

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
        if del_duplicate is True:
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
    message = await session.receive()

    find_error_log = "您要刪除以上錯誤嘗試的記錄嗎"
    if find_error_log in message:
        logger.debug("Skip - Last login attempt failed")

        # Send selection
        if del_error_log is True:
            session.send("y")
            await session.until_string("y", drop=True)
        else:
            session.send("n")
            await session.until_string("n", drop=True)

        session.send(pattern.NEW_LINE)
    else:
        # The message is part of the home menu.
        session.ansip_screen.put(message)

    # Wait for the home menu to load
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
            raise RuntimeError("logout timeout")
        else:
            logger.info("logout timeout , force logout")

    finally:
        logger.info("Logged out")
        await session.websocket_client.close()

    session = None


async def _get_favorite_list_pages(session: Session) -> list:
    """get the favorite list pages"""

    if session.router.location() != "/favorite":
        await session.router.go("/favorite")

    # pages
    favorite_pages = []
    favorite_pages.append(session.ansip_screen.to_formatted_string())  # current page

    # check if more than 1 page
    session.send(pattern.PAGE_DOWN)  # to next page
    while True:  # wait page load
        message = await session.receive_and_put()

        if "\x1b[4;1H" in message:
            # [4;1H
            # more than 1 page , now in next page
            session.ansip_screen.parse()

            current_page = session.ansip_screen.to_formatted_string()
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

    return favorite_pages


async def get_favorite_list(session: Session) -> list:
    """get the favorite list"""

    logger.info("get_favorite_list")

    if session is None:
        raise RuntimeError("Not logged in yet.")

    favorite_pages = await _get_favorite_list_pages(session)

    favorite_list = data_processor.get_favorite_list(favorite_pages)

    return favorite_list


async def _get_board_page(session: Session, board: str) -> list:
    """get the board pages"""

    if session.router.location() != f"/favorite/{board}":
        await session.router.go(f"/favorite/{board}")

    board_page = session.ansip_screen.to_formatted_string()

    return board_page


async def get_latest_post_index(session: Session, board: str) -> int:
    """get the latest post index"""

    logger.info("get_latest_post_index")

    if session is None:
        raise RuntimeError("Not logged in yet.")

    if board == "":
        raise ValueError("board is empty")

    board_page = await _get_board_page(session, board)

    latest_post_index = data_processor.get_latest_post_index(board_page)

    return latest_post_index


async def _get_board_pages_by_range(session: Session, board: str, start: int, stop: int) -> list:
    """Get the board pages by range"""

    def __get_top_index(screen):

        top_line = screen[3]

        top_element = data_processor._process_board_line(top_line)
        if top_element is None:
            raise RuntimeError()

        return int(top_element["index"])

    if session.router.location() != f"/favorite/{board}":
        await session.router.go(f"/favorite/{board}")

    # find index
    await ptt_action.search_index(session, stop)

    # pages
    board_pages = []

    # add current
    current_screen = session.ansip_screen.to_formatted_string()
    board_pages.append(current_screen)

    # check top index in screen
    top_index = __get_top_index(current_screen)

    # if pages not enough
    while top_index > start:
        # go to previos page
        session.send(pattern.PAGE_UP)

        # wait new page loaded
        # '[4;1H' at end
        await session.until_regex_and_put(R".+\x1B\[4;1H$")

        session.ansip_screen.parse()
        current_screen = session.ansip_screen.to_formatted_string()
        board_pages.append(current_screen)

        # check top index in screen
        top_index = __get_top_index(current_screen)

    return board_pages


async def get_post_list_by_range(session: Session, board: str, start: int, stop: int) -> list:
    """Get the post list by range; the `start` < `stop` is required."""

    logger.info("get_post_list")

    if session is None:
        raise RuntimeError("Not logged in yet.")

    if start >= stop:
        raise ValueError("parameter error , `start` < `stop` is required")

    board_pages = await _get_board_pages_by_range(session, board, start, stop)

    post_list = data_processor.get_post_list_by_range(board_pages, start, stop)

    return post_list


async def _get_post_page(session: Session, old_post_status_bar: str) -> list:
    """get a post page"""

    # wait post page loaded
    while True:
        await session.receive_and_put()
        session.ansip_screen.parse()
        current_screen = session.ansip_screen.to_formatted_string()

        # check status bar
        post_status_bar = current_screen[-1]
        match = re.search(pattern.regex_post_status_bar, current_screen[-1])
        if (match and
                post_status_bar != old_post_status_bar):
            # check status bar is complete and differs from the previous one
            old_post_status_bar = post_status_bar
            return current_screen


async def _get_full_post(session: Session, board: str, index: int) -> AsyncGenerator[list]:
    """get a complete post that consists of multiple pages, 
    return an asynchronous generator that yields each raw page."""

    def __extract_progress(post_status_bar):

        match = re.search(pattern.regex_post_status_bar, post_status_bar)
        if match:
            return int(match.group("progress"))
        else:
            raise RuntimeError("Extract progress from the status bar error.")

    if session.router.location() != f"/favorite/{board}/{index}":
        await session.router.go(f"/favorite/{board}/{index}")

    # yield the current page
    current_screen = session.ansip_screen.to_formatted_string()
    yield session.ansip_screen.get_parsed_screen()

    progress = __extract_progress(current_screen[-1])

    # until the post loading is complete
    while progress < 100:
        old_post_status_bar = current_screen[-1]
        session.send(pattern.PAGE_DOWN)  # next page

        # yield the new page
        current_screen = await _get_post_page(session, old_post_status_bar)
        yield session.ansip_screen.get_parsed_screen()

        progress = __extract_progress(current_screen[-1])


async def get_post(session: Session, board: str, index: int) -> AsyncGenerator[tuple[list, list]]:
    """Get the post, return an Asynchronous Generator that 
    yields post data as a `tuple(content_html, post_replies)`."""

    logger.info("get_post")

    if session is None:
        raise RuntimeError("Not logged in yet.")

    last_page = []
    different_index = 0
    async for raw_page in _get_full_post(session, board, index):

        page = ansiparser.from_screen(raw_page).to_formatted_string()

        if last_page:
            different_index = data_processor.get_different_index(page, last_page)

        last_page = page

        contents_html, post_replies = data_processor.get_post_page(raw_page[different_index:])
        yield contents_html, post_replies
