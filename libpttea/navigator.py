"""
libpttea.navigator
~~~~~~~~~~~~~~~~~

This module provides navigation capabilities used by the router.
"""

from __future__ import annotations

import re
import typing

from . import pattern

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


class Home:
    """Path is `/`."""

    def __init__(self, session: Session) -> None:

        self.__session = session

    async def _utility(self) -> None:

        self.__session.send("x")
        self.__session.send(pattern.RIGHT_ARROW)

        await self.__session.until_string_and_put("《查看系統資訊》")
        self.__session.ansip_screen.parse()

    async def _favorite(self) -> None:

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
                await self._favorite()
            case "utility":
                await self._utility()
            case _:
                raise NotImplementedError(f"Not supported yet , {target}.")


class Utility:
    """Path is `/utility`."""

    def __init__(self, session: Session) -> None:

        self.__session = session

    async def _info(self) -> None:

        self.__session.send("x")
        self.__session.send(pattern.RIGHT_ARROW)

        await self.__session.until_string_and_put("請按任意鍵繼續")
        self.__session.ansip_screen.parse()

    async def go(self, target: str) -> None:

        match target:
            case "info":
                await self._info()
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

            self.__session.ansip_screen.parse()

        current_screen = self.__session.ansip_screen.to_formatted_string()



        return True
    
    async def back(self) -> None:
        
        self.__session.send(pattern.LEFT_ARROW)

        # Wait for home to load
        while True:
            await self.__session.receive_and_put()

            if _in_home(self.__session):
                break
        