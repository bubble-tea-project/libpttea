"""
libpttea.api
~~~~~~~~~~~~

This module implements the libpttea API.
"""

from __future__ import annotations

from . import ptt_functions


async def login(account: str, password: str, del_duplicate=True, del_error_log=True) -> API:
    """Log in to PTT.

    登入 PTT"""

    api = API()
    await api.login(account, password, del_duplicate, del_error_log)

    return api


class API:
    def __init__(self) -> None:
        
        self.session = None

    async def login(self, account: str, password: str, del_duplicate=True, del_error_log=True) -> None:
        """Log in to PTT.

        登入 PTT"""

        self.session = await ptt_functions.login(self.session, account , password , del_duplicate , del_error_log)

        return
    
    async def logout(self, force=False) -> None:
        """Log out from PTT.

        登出 PTT"""

        return await ptt_functions.logout(self.session , force=force)


    async def get_system_info(self) -> list:
        """get the PTT system info. 

        查看 PTT 系統資訊"""

        return await ptt_functions.get_system_info(self.session)

        