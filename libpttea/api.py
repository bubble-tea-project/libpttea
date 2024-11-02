"""
libpttea.api
~~~~~~~~~~~~

This module implements the libpttea API.
"""

from __future__ import annotations

import typing

from . import ptt_functions

if typing.TYPE_CHECKING:
    from typing import AsyncGenerator

    from .sessions import Session


async def login(account: str, password: str, del_duplicate=True, del_error_log=True) -> API:
    """Log in to PTT.

    登入 PTT"""

    api = API()
    await api.login(account, password, del_duplicate, del_error_log)

    return api


class API:
    def __init__(self) -> None:

        self.session: Session = None

    async def login(self, account: str, password: str, del_duplicate=True, del_error_log=True) -> None:
        """Log in to PTT.

        登入 PTT"""

        self.session = await ptt_functions.login(self.session, account, password, del_duplicate, del_error_log)

    async def logout(self, force=False) -> None:
        """Log out from PTT.

        登出 PTT"""

        await ptt_functions.logout(self.session, force=force)

    async def get_system_info(self) -> list:
        """get the PTT system info. 

        查看 PTT 系統資訊"""

        return await ptt_functions.get_system_info(self.session)

    async def get_favorite_list(self) -> list:
        """get the favorite list.

        取得 "我的最愛" 清單"""

        return await ptt_functions.get_favorite_list(self.session)

    async def get_latest_post_index(self, board: str) -> int:
        """get the latest post index.

        取得最新的文章編號
        """

        return await ptt_functions.get_latest_post_index(self.session, board)

    async def get_post_list(self, board: str, start: int, stop: int) -> list:
        """Get the post list by range; the `start` < `stop` is required.

        取得範圍內的文章列表
        """

        return await ptt_functions.get_post_list_by_range(self.session, board, start, stop)

    async def get_post(self, board: str, index: int) -> AsyncGenerator[tuple[list, list]]:
        """Get the post, return an Asynchronous Generator that 
        yields post data as a `tuple(content_html, post_replies)`.

        取得文章資料"""

        return ptt_functions.get_post(self.session, board, index)
