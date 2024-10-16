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

from .websocket_client import WebSocketClient


class Session:

    def __init__(self) -> None:

        self.websocket_client: WebSocketClient | None = None
        self.thread_client: threading.Thread | None = None

        self.ws_connection: websocket.WebSocketApp | None = None
        self.ws_queue: asyncio.Queue | None = None

        # binary buffer for receive message
        self.received_binary_buffer = deque()

        self.ansip_screen = ansiparser.new_screen()

        
    def send(self, string: str) -> bytes:
        """Send the message, encoded in UTF-8."""

        string_encode = string.encode('utf-8')
        self.ws_connection.send_bytes(string_encode)

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


        

    async def until_string_r(self, string: str, timeout=5) -> str:
        """until specific string received """
        pass









    # ------
    

    

    

    async def receive_to_buffer(self, encoding='utf-8') -> str:
        """Receive the message and put the raw message into `received_binary_buffer`."""

        raw_message = await self.receive_raw()
        self.received_binary_buffer.append(raw_message)

        return raw_message.decode(encoding=encoding, errors="ignore")

    def flush_buffer(self) -> str:
        """Remove all elements from `received_binary_buffer` and put them to the `a2h_screen` buffer."""

        raw_message = b"".join(self.received_binary_buffer)
        message = raw_message.decode(encoding='utf-8')

        self.ansip_screen.put(message)
        self.received_binary_buffer.clear()
        return message

    def clear_buffer(self) -> str:
        """Remove all elements from the `received_binary_buffer`"""
        self.received_binary_buffer.clear()

    async def until_string_(self, string: str, timeout=2) -> str:
        """Receive and put the raw message into `received_binary_buffer` 
        until the specified 'string' is found in `received_binary_buffer`."""

        while True:
            raw_message = await self.receive_raw(timeout=timeout)
            self.received_binary_buffer.append(raw_message)

            current_buffer = b"".join(self.received_binary_buffer)

            message = current_buffer.decode(encoding='utf-8', errors="ignore")
            if string in message:
                return message

    async def until_regex(self, regex: str | Pattern, timeout=2) -> str:
        """Receive and put the raw message into `received_binary_buffer` 
        until the string in `received_binary_buffer` matches the `regex`"""

        while True:
            raw_message = await self.receive_raw(timeout=timeout)
            self.received_binary_buffer.append(raw_message)

            current_buffer = b"".join(self.received_binary_buffer)

            message = current_buffer.decode(encoding='utf-8', errors="ignore")
            match = re.search(regex, message)
            if match:
                return message


