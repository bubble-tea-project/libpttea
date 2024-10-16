from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from ansiparser.screen_parser import ScreenParser

import re
from . import pattern


class Router:
    def __init__(self , ansip_screen:ScreenParser ) -> None:
        
        self.ansip_screen = ansip_screen
        self._location = ""

    def in_home(self) -> bool:
        
        if self.ansip_screen.buffer_empty() is False:
            self.ansip_screen.parse()

        current_screen = self.ansip_screen.to_formatted_string()
    
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
        
        
    def go(self) -> None:
        pass