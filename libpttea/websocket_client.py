"""
libpttea.websocket_client
~~~~~~~~~~~~

This module provides the WebSocket client for connecting to PTT.
"""

import queue

import websocket

from .exceptions import ConnectionClosed, ConnectionError


class WebSocketClient:

    def __init__(self, url="wss://ws.ptt.cc/bbs/", origin="https://term.ptt.cc") -> None:

        self.url = url
        self.origin = origin

        self.ws_queue = queue.Queue()
        self.ws_connection = websocket.WebSocketApp(
            self.url,
            on_open=self.__on_open,
            on_message=self.__on_message,
            on_error=self.__on_error,
            on_close=self.__on_close)

        self.connected = False

    def __on_open(self, wsapp: websocket.WebSocketApp):

        print("### Opened connection ###")
        self.connected = True

    def __on_message(self, wsapp: websocket.WebSocketApp, message: str):

        self.ws_queue.put(message)
        #
        tmp = (message.decode("utf-8", errors="ignore"),)
        print("get >>>", tmp)

    def __on_error(self, wsapp: websocket.WebSocketApp, error: Exception):

        raise ConnectionError(str(error))

    def __on_close(self, wsapp: websocket.WebSocketApp, close_status_code: int, close_msg: str):

        print("### Closed connection###")
        raise ConnectionClosed(close_msg)

    def connect(self) -> None:
        """Connect to PTT."""

        self.ws_connection.run_forever(origin=self.origin)
