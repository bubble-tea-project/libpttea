"""
libpttea.router
~~~~~~~~~~~~

This module provides a URL-based API for navigating between different PTT screens.
"""

from __future__ import annotations

import re
import typing

from . import navigator, pattern

if typing.TYPE_CHECKING:
    from .sessions import Session


class Router:

    def __init__(self, session: Session) -> None:

        self._session = session

        self._location = ""

    def __path_parts(self, path: str) -> list:
        """Split the path into individual parts."""

        return path.strip('/').split('/')

    def __path_level(self, path: str) -> int:
        """Get the level of the path, starting from 0."""

        # Remove trailing slashes
        level = path.rstrip('/').count("/")

        return level

    def __path_current(self, path: str) -> str:
        """Get the current location from the path."""

        if path == "/":
            return "/"

        parts = self.__path_parts(path)

        return parts[-1]

    def __path_same_until(self, current: str, go: str) -> int:
        """Get the level at which two paths are the same until they diverge."""

        current_parts = self.__path_parts(current)
        go_parts = self.__path_parts(go)

        # Find the shorter
        min_length = min(len(current_parts), len(go_parts))

        for index in range(min_length):
            if current_parts[index] != go_parts[index]:
                return index

        # If one path is a subset of the other
        return min_length

    def __path_need_move(self, current: str, go: str) -> tuple[list, list]:
        """Calculate required steps to navigate from the current path to the target path."""

        current_level = self.__path_level(current)
        current_parts = self.__path_parts(current)

        go_level = self.__path_level(go)
        go_parts = self.__path_parts(go)

        same_until = self.__path_same_until(current, go)

        need_back = current_parts[same_until:current_level]
        need_go = go_parts[same_until:go_level]

        return need_back, need_go

    async def __back(self, needs: list) -> None:

        for current_location in reversed(needs):

            match current_location:
                case "favorite":
                    await navigator.Favorite(self._session).back()
                case "utility":
                    await navigator.Utility(self._session).back()
                case "info":
                    await navigator.UtilityInfo(self._session).back()
                case _:
                    # when at Board
                    # /favorite/C_Chat
                    if re.search(pattern.regex_path_at_board, self.location()):
                        await navigator.Board(self._session).back()

                    # when at Post index
                    # /favorite/C_Chat/335045
                    elif re.search(pattern.regex_path_at_post_index, self.location()):
                        await navigator.Post(self._session).back()

                    else:
                        raise NotImplementedError(f"Not supported yet , back from ={current_location}.")
            #
            needs.pop()
            self._location = "/" + "/".join(needs)

    async def __go(self, needs) -> None:

        for next_location in needs:

            match self.__path_current(self.location()):
                case "/":
                    await navigator.Home(self._session).go(next_location)
                case "favorite":
                    await navigator.Favorite(self._session).go(next_location)
                case "utility":
                    await navigator.Utility(self._session).go(next_location)
                    self._location += f"/{next_location}"
                case _:
                    # when at Board
                    # /favorite/C_Chat
                    if re.search(pattern.regex_path_at_board, self.location()):
                        # go , /favorite/C_Chat/335045
                        await navigator.Board(self._session).go(next_location)
                    else:
                        raise NotImplementedError(f"Not supported yet , from ={self.location()} , go ={next_location}.")

            if self.location() == "/":
                self._location += f"{next_location}"
            else:
                self._location += f"/{next_location}"

    def in_home(self) -> bool:
        """Check if the current screen is the home menu."""

        return navigator._in_home(self._session)

    def init_home(self) -> None:
        """Initialize the path for the home menu."""

        self._location = "/"

    def location(self) -> str:
        """Get the current location path."""

        if self._location == "":
            raise RuntimeError("Home menu path is not initialized yet")
        else:
            return self._location

    async def go(self, location) -> None:
        """Navigate to a URL location"""

        # same location
        if self.location() == location:
            raise RuntimeError("Already at the location")

        need_back, need_go = self.__path_need_move(self.location(), location)

        await self.__back(need_back)
        await self.__go(need_go)
