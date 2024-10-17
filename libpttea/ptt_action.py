"""
libpttea.ptt_action
~~~~~~~~~~~~~~~~~

This module provides functions that wrap user operations to interact with PTT.
"""

from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from .sessions import Session


import re
from . import pattern




async def move_home(session:Session , target=None ):
    
    async def __go_utility():

        session.send("x")
        session.send(pattern.RIGHT_ARROW)

        await session.until_string_and_put("《查看系統資訊》")
        session.ansip_screen.parse()
        

    # back
    if target is None:
        raise RuntimeError()

    # go
    match target:
        case "utility":
            await __go_utility()
        case _:
            raise NotImplementedError(f"Not supported yet , ={target}.")




async def move_utility(session:Session , target=None ):

    async def __back():
        
        session.send(pattern.LEFT_ARROW)

        # wait home loaded
        # 【 系統資訊區 】[K[20;23H([1;36mG[m)oodbye[20;41H離開，再見
        await session.until_string_and_put("\x1b[20;41H離開，再見")
       

    async def __go_info():
        
        session.send("x")
        session.send(pattern.RIGHT_ARROW)

        await session.until_string_and_put("請按任意鍵繼續")
        session.ansip_screen.parse()
    
    # back
    if target is None:
        await __back()


    # go
    match target:
        case "info":
            await __go_info() 
        case _:
            raise NotImplementedError(f"Not supported yet , ={target}.")
        

async def move_utility_info(session:Session):

    async def __in_utility():

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
        

    
    # back
    session.send(pattern.NEW_LINE)

    while True:
        
        message = await session.receive()
        session.ansip_screen.put( message )

        if __in_utility():
            session.ansip_screen.parse()
            return