"""
libpttea.api
~~~~~~~~~~~~

This module implements the libpttea API.
"""

from __future__ import annotations

from . import data_processor, ptt_functions, sessions


def login(account: str, password: str, del_duplicate=True, del_error_log=True) -> API:
    """Log in to PTT.

    登入 PTT"""

    api = API()
    api.login(account, password, del_duplicate, del_error_log)

    return api


class API:

    def __init__(self) -> None:

        self.session = None

        self.account = ""
        self.password = ""

    def login(self, account: str, password: str, del_duplicate=True, del_error_log=True) -> None:
        """Log in to PTT.

        登入 PTT"""

        if self.session is not None:
            raise RuntimeError("Is logged in")
        else:
            self.session = sessions.Session()

        self.account = account
        self.password = password

        self.session = ptt_functions.login(self.session, account, password)
        self.session = ptt_functions.skip_init(self.session, del_duplicate, del_error_log)

        return

    def logout(self, force=False) -> None:
        """Log out from PTT.

        登出 PTT"""

        if self.session is None:
            raise RuntimeError("Is logged out")

        try:
            ptt_functions.logout(self.session)
        except RuntimeError:

            if force is False:
                raise RuntimeError("logout failed")
            else:
                self.session.ws_connection.close()
                self.session = None

        self.session.ws_connection.close()
        self.session = None

        self.account = ""
        self.password = ""

        return

    def system_info(self) -> list:
        """get the PTT system info. 

        查看 PTT 系統資訊"""

        if self.session is None:
            raise RuntimeError("Not logged in yet.")

        self.session, system_info_page = ptt_functions.get_system_info(self.session)

        system_info = data_processor.get_system_info(system_info_page)

        return system_info

    def favorite_list(self) -> list:
        """get the user's favorite list.

        取得 "我 的 最愛" 清單"""

        if self.session is None:
            raise RuntimeError("Not logged in yet.")

        self.session, favorite_pages = ptt_functions.get_favorite_list(self.session)

        favorite_list = data_processor.get_favorite_list(favorite_pages)

        return favorite_list

    def post_list(self, board: str, number=20) -> list:
        """get the post list for the board, starting with the latest post.

        取得看板的文章列表，從最新的文章開始。"""

        if self.session is None:
            raise RuntimeError("Not logged in yet.")

        self.session, post_list_pages = ptt_functions.get_post_list(self.session, board, number)

        post_list = data_processor.get_post_list(post_list_pages)

        return post_list

    def get_post(self, board: str, post_index: int) -> list:
        """get the entire content of the post.

        取得整篇文章內容。"""

        if self.session is None:
            raise RuntimeError("Not logged in yet.")

        self.session, post_pages, raw_post_pages = ptt_functions.get_post_all(self.session, board, post_index)

        post = data_processor.get_post_all(post_pages, raw_post_pages)

        return post
