"""
libpttea.sessions
~~~~~~~~~~~~

This module provides a Session object to manage connections to PTT.
"""

import queue
import re
import threading
import time
from collections import deque
from typing import Pattern
import asyncio

import ansiparser
import websocket
import websockets.asyncio.client

from .websocket_client import WebSocketClient
from .router import Router

class Session:

    def __init__(self) -> None:

        self.websocket_client: WebSocketClient | None = None
        self.thread_client: threading.Thread | None = None

        self.ws_connection: websockets.asyncio.client.ClientConnection | None = None
        self.ws_queue: asyncio.Queue | None = None

        
        self.ansip_screen = ansiparser.new_screen()

        self.router = Router(self)

        
    def send(self, string: str) -> bytes:
        """Send the message, encoded in UTF-8."""

        string_encode = string.encode('utf-8')
        # self.ws_connection.send_bytes(string_encode)
        self.websocket_client.send( string_encode )

        return string_encode

    async def receive_raw(self, timeout=2) -> bytes:
        """Receive the raw message """

        try:
            raw_message = await asyncio.wait_for(self.ws_queue.get(), timeout=timeout)
        except TimeoutError:
            raise TimeoutError("Wait for receive timeout.")

        return raw_message

    async def receive(self , timeout=3) -> str:
        """Receive the message, assembles ,  UTF-8"""

        async def _receive():
            # for fragmented messages
            message_frames = []
            
            while True:
                
                frame = await self.receive_raw(timeout=None)
                message_frames.append(frame)

                try:
                    message = b"".join(message_frames).decode('utf-8')
                    return message
                except UnicodeDecodeError:
                    continue
        
        return await asyncio.wait_for( _receive() , timeout=timeout)

    async def until_string(self, string: str, drop=False, timeout=5) -> str | list:
        """until specific string received """
        
        async def _until_string_drop():

            while True:
                message = await self.receive(timeout=None)

                if string in message:
                    return message

        async def _until_string():
            messages = []

            while True:
                message = await self.receive(timeout=None)
                messages.append(message)

                if string in message:
                    return messages

        if drop is True:
            return await asyncio.wait_for( _until_string_drop() , timeout=timeout)
        else:
            return await asyncio.wait_for( _until_string() , timeout=timeout)


    async def until_regex(self, regex: str | Pattern, drop=False, timeout=2) -> str| list:
        """matches the `regex`"""

        async def _until_regex_drop():

            while True:
                message = await self.receive(timeout=None)

                match = re.search(regex, message)
                if match:
                    return message

        async def _until_regex():
            messages = []

            while True:
                message = await self.receive(timeout=None)
                messages.append(message)

                match = re.search(regex, message)
                if match:
                    return messages

        if drop is True:
            return await asyncio.wait_for( _until_regex_drop() , timeout=timeout)
        else:
            return await asyncio.wait_for( _until_regex() , timeout=timeout)


    async def receive_and_put(self , timeout=3) -> str:
        
        message = await self.receive(timeout)
        self.ansip_screen.put( message )

        return message

    async def until_string_and_put(self, string: str, timeout=5) -> list:
        """until specific string received """

        messages = await self.until_string(string,False,timeout)

        for message in messages:
            self.ansip_screen.put( message )

        return messages
    
    async def until_regex_and_put(self, regex: str | Pattern, timeout=5) -> list:
        """re"""

        messages = await self.until_regex(regex,False,timeout)

        for message in messages:
            self.ansip_screen.put( message )

        return messages









   

 

    


