"""
libpttea.sessions
~~~~~~~~~~~~

This module provides a Session object to manage resources (websocket_client, ansip_screen, router) 
in the connection.
"""

from __future__ import annotations

import asyncio
import re
import typing

import ansiparser

from . import pattern
from .router import Router
from .websocket_client import WebSocketClient

if typing.TYPE_CHECKING:
    from typing import Pattern


class Session:

    def __init__(self, timeout_delay=0) -> None:

        self.websocket_client = WebSocketClient()

        self.ansip_screen = ansiparser.new_screen()

        self.router = Router(self)

        # timeout_delay (seconds) , default_timeout + timeout_delay = total_timeout
        self.timeout_delay = timeout_delay

    def __total_timeout(self, timeout) -> int | None:
        """calculate the `total_timeout`"""

        if timeout is None:
            # return None for blocking operations
            return None
        else:
            return timeout + self.timeout_delay

    def send(self, string: str) -> bytes:
        """Send the message, encoded in UTF-8."""

        encoded_bytes = string.encode('utf-8')
        self.websocket_client.send(encoded_bytes)

        return encoded_bytes

    async def receive_raw(self, timeout: int | None = 3) -> bytes:
        """Receive the raw message that is in bytestring."""

        try:
            raw_message = await asyncio.wait_for(self.websocket_client.receive_queue.get(), timeout=self.__total_timeout(timeout))
        except TimeoutError:
            raise TimeoutError("Wait for receive timeout.")

        return raw_message

    async def receive(self, timeout: int | None = 5) -> str:
        """Receive the raw message, wait until all fragments are received,
          reassemble them, and return the UTF-8 decoded message"""

        async def _receive():

            # store fragmented messages
            message_frames = []

            while True:
                frame = await self.receive_raw(timeout=None)
                message_frames.append(frame)

                try:
                    message = b"".join(message_frames).decode('utf-8')
                    if re.search(pattern.regex_incomplete_ansi_escape, message):
                        # message contains an incomplete ANSI escape sequence
                        continue

                    return message
                except UnicodeDecodeError:
                    continue

        return await asyncio.wait_for(_receive(), timeout=self.__total_timeout(timeout))

    async def until_string(self, string: str, drop=False, timeout=10) -> str | list:
        """
        Wait until the specified `string` is found in the received message. 
        If `drop` is false, return all messages in the process.
        Otherwise , returns the message containing the string.
        """

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
            return await asyncio.wait_for(_until_string_drop(), timeout=self.__total_timeout(timeout))
        else:
            return await asyncio.wait_for(_until_string(), timeout=self.__total_timeout(timeout))

    async def until_regex(self, regex: str | Pattern, drop=False, timeout=10) -> str | list:
        """
        Wait until the received message matches the `regex`.
        If `drop` is false, return all messages in the process.
        Otherwise , returns the message matches the `regex`.
        """

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
            return await asyncio.wait_for(_until_regex_drop(), timeout=self.__total_timeout(timeout))
        else:
            return await asyncio.wait_for(_until_regex(), timeout=self.__total_timeout(timeout))

    async def receive_and_put(self, timeout=5) -> str:
        """Call `receive()` and put the returned message into `ansip_screen`."""

        message = await self.receive(timeout)
        self.ansip_screen.put(message)

        return message

    async def until_string_and_put(self, string: str, timeout=10) -> list:
        """Call `until_string(drop=False)` and put the returned message into `ansip_screen`."""

        messages = await self.until_string(string, False, timeout)
        for message in messages:
            self.ansip_screen.put(message)

        return messages

    async def until_regex_and_put(self, regex: str | Pattern, timeout=10) -> list:
        """Call `until_regex(drop=False)` and put the returned message into `ansip_screen`."""

        messages = await self.until_regex(regex, False, timeout)
        for message in messages:
            self.ansip_screen.put(message)

        return messages
