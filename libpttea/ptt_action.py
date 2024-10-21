"""
libpttea.ptt_action
~~~~~~~~~~~~~~~~~

This module provides functions that wrap user operations to interact with PTT.
"""

from __future__ import annotations

import re
import typing

from . import pattern

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
