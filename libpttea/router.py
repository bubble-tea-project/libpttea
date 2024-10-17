from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from .sessions import Session

import re
from . import pattern , ptt_action




class Router:
    def __init__(self , session:Session ) -> None:
        
        self._session = session

        self._location = ""

    def __path_parts(self ,path: str) -> list:
        
        return path.strip('/').split('/')

    def __path_level(self ,path: str) -> int:

        # Remove  trailing slashes 
        level = path.rstrip('/').count("/")
        
        return level 

    def __path_current(self ,path: str) -> str:
        
        parts = self.__path_parts(path)
        
        if path == "/":
            return "/"
        
        return parts[-1]

    def __path_same_until(self ,current: str, go: str) -> int:
        # 
        current_parts = self.__path_parts(current)
        go_parts = self.__path_parts(go)
        
        # Find the shorter 
        min_length = min(len(current_parts), len(go_parts))
        
        # how long is same
        for index in range(min_length):
            if current_parts[index] != go_parts[index]:
                return index 
        
        # If one path is a subset of the other, return the length of the shorter one
        return min_length

    def __path_need_move(self ,current: str, go: str) :

        current_level = self.__path_level(current)
        current_parts = self.__path_parts(current)

        go_level = self.__path_level(go)
        go_parts = self.__path_parts(go)

        same_until = self.__path_same_until(current, go)
        
        need_back_level = current_level - same_until
        need_back = current_parts[same_until: (same_until + need_back_level)]

        need_go_level = go_level - same_until
        need_go = go_parts[same_until:(same_until + need_go_level)]

        return need_back , need_go

    async def __back(self ,needs:list) -> None:
        
        needs.reverse()

        for index, current_location in enumerate(needs):

            match current_location:
                case "utility":
                    await ptt_action.move_utility(self._session)
                    needs.pop()
                case "info":
                    await ptt_action.move_utility_info(self._session)
                    needs.pop()
                case _:
                    raise NotImplementedError(f"Not supported yet , ={current_location}.")
            # 
            self._location = "/" + "/".join(needs)

        return

    async def __go(self ,needs) -> None:

        for next_location in needs:

            match self.__path_current(self.location()):

                case "/":
                    await ptt_action.move_home(self._session,next_location)
                    self._location += f"{next_location}" 
                case "utility":
                    await ptt_action.move_utility(self._session,next_location)
                    self._location += f"/{next_location}" 
                case _:
                    raise NotImplementedError(f"Not supported yet , ={next_location}.")
        
        return


    def in_home(self) -> bool:
        
        if self._session.ansip_screen.buffer_empty() is False:
            self._session.ansip_screen.parse()

        current_screen = self._session.ansip_screen.to_formatted_string()
    
        # Check the title line
        if "主功能表" not in current_screen[0]:
            return False

        # check status bar
        match = re.search(pattern.regex_menu_status_bar, current_screen[-1])
        if match is None:
            return False

        return True

    def init_home(self) -> None:
        self._location = "/"

    def location(self) -> str:
        
        if self._location == "":
            raise RuntimeError("not init home")
        else:
            return self._location
        
    async def go(self , location) -> None:
        
        # same location
        if self.location() == location:
            raise RuntimeError("same location")
        
        # 
        need_back , need_go = self.__path_need_move( self.location(), location )

        await self.__back(need_back)
        await self.__go(need_go)












