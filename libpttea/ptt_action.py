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
        
    
    return




async def move_utility(session:Session , target=None ):

    async def __back():
        
        session.send(pattern.LEFT_ARROW)

        # wait home loaded
        # 【 系統資訊區 】[K[20;23H([1;36mG[m)oodbye[20;41H離開，再見
        await session.until_string_and_put("\x1b[20;41H離開，再見")
        session.ansip_screen.parse()
       

    async def __go_info():
        
        session.send("x")
        session.send(pattern.RIGHT_ARROW)

        await session.until_string_and_put("請按任意鍵繼續")
        session.ansip_screen.parse()
        
    
    # back
    if target is None:
        await __back()
        return


    # go
    match target:
        case "info":
            await __go_info() 
        case _:
            raise NotImplementedError(f"Not supported yet , ={target}.")
            
    return
        

async def move_utility_info(session:Session):

    # back
    # 請按任意鍵繼續
    session.send(pattern.NEW_LINE)

    # wait sys_info_area loaded
    # [呼叫器][31m打開 [m[19;21H
    await session.until_string_and_put("\x1b[m\x1b[19;21H")

    session.ansip_screen.parse()
    return
        
    