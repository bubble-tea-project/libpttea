"""
libpttea.ptt_action
~~~~~~~~~~~~~~~~~

This module provides functions that wrap user operations to interact with PTT.
"""

from __future__ import annotations

import re
import typing

from . import pattern, navigator

if typing.TYPE_CHECKING:
    from .sessions import Session


async def search_board(session: Session, board: str) -> None:

    # let cursor to first item
    session.send(pattern.HOME)

    # switch list all
    current_screen = session.ansip_screen.to_formatted_string()
    # check status bar
    match = re.search(R"列出全部", current_screen[-1])
    if match:
        # (y)列出全部
        session.send("y")

    # search board
    # (s)進入已知板名
    session.send("s")
    await session.until_string_and_put("請輸入看板名稱(按空白鍵自動搜尋)")

    # send board
    session.send(board)
    await session.until_string(board)
    session.send(pattern.NEW_LINE)

    # Check search results
    while True:  # wait page load
        message = await session.receive_and_put()
        session.ansip_screen.parse()

        # The cursor has not moved
        match = re.search(pattern.regex_favorite_cursor_not_moved, message)
        if match:

            # Found, it is the first item
            regex_cursor_board = R"^>.+" + board
            current_screen = session.ansip_screen.to_formatted_string()
            if not any([re.search(regex_cursor_board, _) for _ in current_screen]):
                # Not found
                raise RuntimeError("board not found")
            else:
                break

        # The cursor has moved
        # Found, not the first item
        match = re.search(pattern.regex_favorite_cursor_moved, message)
        if match:
            break


async def search_index(session: Session, index: int) -> None:
    """Search for the index, and if it is found, the cursor will move to that position."""

    # go to the latest page of the board
    session.send(pattern.END)

    # find post
    session.send(str(index))
    await session.until_string_and_put("跳至第幾項")
    session.send(pattern.NEW_LINE)

    # Check if found
    while True:
        await session.receive_and_put()
        session.ansip_screen.parse()

        if navigator._in_board(session):
            # found in different page
            break

        current_screen = session.ansip_screen.to_formatted_string()
        if current_screen[-1] == "":
            # If found on the same page, the status bar will disappear.
            break

    # Recheck if the index is present on the current page
    current_screen = session.ansip_screen.to_formatted_string()
    regex_post_index = R"^(>| )\s?" + str(index)  # '>351769 +  10/22 kannax       □  [Vtub] '
    if not any([re.search(regex_post_index, line) for line in current_screen]):
        # same page , but not found
        raise RuntimeError("post index not found")
