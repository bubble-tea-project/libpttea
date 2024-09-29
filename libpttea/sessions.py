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

import ansiparser
import websocket

from .websocket_client import WebSocketClient


class Session:

    def __init__(self) -> None:

        self.websocket_client: WebSocketClient | None = None
        self.thread_client: threading.Thread | None = None

        self.ws_connection: websocket.WebSocketApp | None = None
        self.ws_queue: queue.Queue | None = None

        # binary buffer for receive message
        self.received_binary_buffer = deque()

        self.a2h_screen = ansiparser.new_screen()

        # current ptt page location
        self.current_location = ""

    def send(self, string: str) -> str:
        """Send the message, encoded in UTF-8."""

        string_encode = string.encode('utf-8')
        self.ws_connection.send_bytes(string_encode)

        return string_encode

    def receive_raw(self, timeout=2) -> str:
        """Receive the raw message, which is in a sequence of bytes."""

        try:
            raw_message = self.ws_queue.get(timeout=timeout)
        except queue.Empty:
            raise queue.Empty("Wait for receive timeout.")

        return raw_message

    def receive(self, encoding='utf-8', errors="ignore", timeout=2) -> str:
        """Receive the message, encoded with the encoding."""

        try:
            raw_message = self.ws_queue.get(timeout=timeout)
        except queue.Empty:
            raise queue.Empty("Wait for receive timeout.")

        return raw_message.decode(encoding=encoding, errors=errors)

    def receive_to_buffer(self, encoding='utf-8') -> str:
        """Receive the message and put the raw message into `received_binary_buffer`."""

        raw_message = self.receive_raw()
        self.received_binary_buffer.append(raw_message)

        return raw_message.decode(encoding=encoding, errors="ignore")

    def flush_buffer(self) -> str:
        """Remove all elements from `received_binary_buffer` and put them to the `a2h_screen` buffer."""

        raw_message = b"".join(self.received_binary_buffer)
        message = raw_message.decode(encoding='utf-8')

        self.a2h_screen.put(message)
        self.received_binary_buffer.clear()
        return message

    def clear_buffer(self) -> str:
        """Remove all elements from the `received_binary_buffer`"""
        self.received_binary_buffer.clear()

    def until_string(self, string: str, timeout=2) -> str:
        """Receive and put the raw message into `received_binary_buffer` 
        until the specified 'string' is found in `received_binary_buffer`."""

        while True:
            raw_message = self.receive_raw(timeout=timeout)
            self.received_binary_buffer.append(raw_message)

            current_buffer = b"".join(self.received_binary_buffer)

            message = current_buffer.decode(encoding='utf-8', errors="ignore")
            if string in message:
                return message

    def until_regex(self, regex: str | Pattern, timeout=2) -> str:
        """Receive and put the raw message into `received_binary_buffer` 
        until the string in `received_binary_buffer` matches the `regex`"""

        while True:
            raw_message = self.receive_raw(timeout=timeout)
            self.received_binary_buffer.append(raw_message)

            current_buffer = b"".join(self.received_binary_buffer)

            message = current_buffer.decode(encoding='utf-8', errors="ignore")
            match = re.search(regex, message)
            if match:
                return message

    def until_time(self, timeout=1) -> None:
        """Receive and put the raw message into `received_binary_buffer` until timeout."""

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                raw_message = self.ws_queue.get_nowait()
            except queue.Empty:
                continue

            self.received_binary_buffer.append(raw_message)
