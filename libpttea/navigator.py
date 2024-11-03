"""
libpttea.navigator
~~~~~~~~~~~~~~~~~

This module provides navigation capabilities used by the router.
"""

from __future__ import annotations

import re
import typing

from . import pattern, ptt_action

if typing.TYPE_CHECKING:
    from .sessions import Session


def _in_home(session: Session) -> bool:

    if session.ansip_screen.buffer_empty() is False:
        session.ansip_screen.parse()

    current_screen = session.ansip_screen.to_formatted_string()

    # Check the title line
    if "主功能表" not in current_screen[0]:
        return False

    # check status bar
    match = re.search(pattern.regex_menu_status_bar, current_screen[-1])
    if match is None:
        return False

    return True


def _in_utility(session: Session) -> bool:

    if session.ansip_screen.buffer_empty() is False:
        session.ansip_screen.parse()

    current_screen = session.ansip_screen.to_formatted_string()

    # Check the title line
    if "工具程式" not in current_screen[0]:
        return False

    # check status bar
    match = re.search(pattern.regex_menu_status_bar, current_screen[-1])
    if match is None:
        return False

    return True


def _in_board(session: Session) -> bool:

    if session.ansip_screen.buffer_empty() is False:
        session.ansip_screen.parse()

    current_screen = session.ansip_screen.to_formatted_string()

    # check status bar
    match = re.search(pattern.regex_board_status_bar, current_screen[-1])
    if match is None:
        return False

    return True


def _in_post(session: Session) -> bool:

    if session.ansip_screen.buffer_empty() is False:
        session.ansip_screen.parse()

    current_screen = session.ansip_screen.to_formatted_string()

    # check status bar
    match_no_content = re.search(pattern.regex_post_no_content, current_screen[-1])
    if match_no_content:
        raise RuntimeError("The post has no content; it has already been deleted.")

    match = re.search(pattern.regex_post_status_bar_simple, current_screen[-1])
    if match:
        return True

    return False


class Home:
    """Path is `/`."""

    def __init__(self, session: Session) -> None:

        self.__session = session

    async def _go_utility(self) -> None:

        self.__session.send("x")
        self.__session.send(pattern.RIGHT_ARROW)

        # wait utility loaded
        await self.__session.until_string_and_put("《查看系統資訊》")
        self.__session.ansip_screen.parse()

    async def _go_favorite(self) -> None:

        # select index , 我 的 最愛
        self.__session.send("f")
        self.__session.send(pattern.RIGHT_ARROW)

        # wait favorite loaded
        # [30m列出全部 [31m(v/V)[30m已讀/未讀
        await self.__session.until_string_and_put("\x1b[30m已讀/未讀")
        self.__session.ansip_screen.parse()

    async def go(self, target: str) -> None:

        match target:
            case "favorite":
                await self._go_favorite()
            case "utility":
                await self._go_utility()
            case _:
                raise NotImplementedError(f"Not supported yet , {target}.")


class Utility:
    """Path is `/utility`."""

    def __init__(self, session: Session) -> None:

        self.__session = session

    async def _go_info(self) -> None:

        self.__session.send("x")
        self.__session.send(pattern.RIGHT_ARROW)

        # wait info loaded
        await self.__session.until_string_and_put("請按任意鍵繼續")
        self.__session.ansip_screen.parse()

    async def go(self, target: str) -> None:

        match target:
            case "info":
                await self._go_info()
            case _:
                raise NotImplementedError(f"Not supported yet , {target}.")

    async def back(self) -> None:

        self.__session.send(pattern.LEFT_ARROW)

        # wait home menu loaded
        # 【 系統資訊區 】[K[20;23H([1;36mG[m)oodbye[20;41H離開，再見
        await self.__session.until_string_and_put("\x1b[20;41H離開，再見")
        self.__session.ansip_screen.parse()


class UtilityInfo:
    """Path is `/utility/info`."""

    def __init__(self, session: Session) -> None:

        self.__session = session

    async def back(self) -> None:

        # 請按任意鍵繼續
        self.__session.send(pattern.NEW_LINE)

        # Wait for utility to load
        while True:
            await self.__session.receive_and_put()

            if _in_utility(self.__session):
                break


class Favorite:
    """Path is `/favorite`."""

    def __init__(self, session: Session) -> None:

        self.__session = session

    async def _go_board(self) -> None:

        # go board
        self.__session.send(pattern.RIGHT_ARROW)

        # wait for board loaded
        # 動畫播放中…可按 q,Ctrl-C 或其它任意鍵停止
        # 請按任意鍵繼續
        check_enter_board = ["請按任意鍵繼續", "任意鍵停止"]

        while True:
            message = await self.__session.receive_and_put()
            self.__session.ansip_screen.parse()

            # skip - Enter board screen
            if any(_ in message for _ in check_enter_board):
                self.__session.send(pattern.RIGHT_ARROW)
                continue

            # if already in board
            if _in_board(self.__session):
                break

        # go to the latest
        self.__session.send(pattern.END)

        # wait if cursor has moved.
        try:
            await self.__session.until_regex_and_put(R">.+\x1b\[")
        except TimeoutError:
            # already latest
            pass

        self.__session.ansip_screen.parse()
        return

    async def go(self, target: str) -> None:

        await ptt_action.search_board(self.__session, target)
        await self._go_board()

    async def back(self) -> None:

        self.__session.send(pattern.LEFT_ARROW)

        # Wait for home to load
        while True:
            await self.__session.receive_and_put()

            if _in_home(self.__session):
                break


class Board:
    """Path is `/favorite/board`."""

    def __init__(self, session: Session) -> None:

        self.__session = session

    async def _go_post_by_index(self, index: int) -> None:

        # find index
        await ptt_action.search_index(self.__session, index)

        # go to post
        self.__session.send(pattern.RIGHT_ARROW)

        # wait post loaded
        while True:
            await self.__session.receive_and_put()

            if _in_post(self.__session):
                break

    async def go(self, target: int) -> None:

        await self._go_post_by_index(target)

    async def back(self) -> None:

        self.__session.send(pattern.LEFT_ARROW)

        # wait favorite loaded
        # [30m列出全部 [31m(v/V)[30m已讀/未讀
        await self.__session.until_string_and_put("\x1b[30m已讀/未讀")
        self.__session.ansip_screen.parse()


class Post:
    """Path is `/favorite/board/post`."""

    def __init__(self, session: Session) -> None:

        self.__session = session

    async def back(self) -> None:

        self.__session.send(pattern.LEFT_ARROW)

        # wait Board loaded
        while True:
            await self.__session.receive_and_put()

            if _in_board(self.__session):
                break
