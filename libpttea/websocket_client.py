"""
libpttea.websocket_client
~~~~~~~~~~~~

This module provides the WebSocket client for connecting to PTT.
"""

import queue
import asyncio
import websocket
import logging


logger = logging.getLogger("websocket_client")


class WebSocketClient:

    def __init__(self, url="wss://ws.ptt.cc/bbs/", origin="https://term.ptt.cc") -> None:

        self.url = url
        self.origin = origin

        self.ws_queue = asyncio.Queue()

        self.connected = False
        self.ws_connection = websocket.WebSocketApp(
            self.url,
            on_open=self.__on_open,
            on_message=self.__on_message,
            on_error=self.__on_error,
            on_close=self.__on_close)

    def __on_open(self, wsapp: websocket.WebSocketApp):

        logger.info("connection opened")
        self.connected = True

    def __on_message(self, wsapp: websocket.WebSocketApp, message: str):

        self.ws_queue.put_nowait(message)
        #
        logger.debug(f"receive >>({message.decode("utf-8", errors="ignore")})\n")


    def __on_error(self, wsapp: websocket.WebSocketApp, error: Exception):

        pass
        # raise ConnectionError(str(error))

    def __on_close(self, wsapp: websocket.WebSocketApp, close_status_code: int, close_msg: str):

        logger.info("connection closed")
        # raise ConnectionClosed(close_msg)

    def connect(self) -> None:
        """Connect to PTT."""

        self.ws_connection.run_forever(origin=self.origin)
